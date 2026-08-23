package OpenRegex::Processor;

use strict;
use warnings;

use Encode ();
use IO::Select;
use JSON::PP;
use POSIX ();
use Time::HiRes ();

our $QUEUE         = 'queue:perl';
our $DEAD_QUEUE    = 'queue:perl:dead';
our $HEARTBEAT_KEY = 'openregex:workers:heartbeat:worker-perl';

my $TIMEOUT_MS     = $ENV{WORKER_EXECUTION_TIMEOUT_MS} || 1000;
my $MAX_INPUT_SIZE = $ENV{WORKER_MAX_INPUT_SIZE}       || 10485760;
my $MAX_MATCHES    = $ENV{WORKER_MAX_MATCHES}          || 10000;
my $MAX_GROUPS     = $ENV{WORKER_MAX_GROUPS}           || 1000;
my $MAX_JSON_SIZE  = $ENV{WORKER_MAX_JSON_SIZE}        || 10485760;

my $CODEC = JSON::PP->new->utf8->canonical(0);

# Inline modifiers accepted by (?...) in perlre.
my %ALLOWED_FLAGS = map { $_ => 1 } qw(i m s x a d l u n p);

# Walks the pattern to learn how many capture groups it declares and what each
# one is called. Perl numbers named groups too, so the index -> name map has to
# follow the textual order of the opening parentheses.
sub scan_groups {
    my ($pattern) = @_;

    my $count   = 0;
    my %names   = ();
    my $in_class = 0;
    my @chars   = split //, $pattern;
    my $i       = 0;

    while ( $i < @chars ) {
        my $ch = $chars[$i];

        if ( $ch eq '\\' ) { $i += 2; next; }

        if ($in_class) {
            $in_class = 0 if $ch eq ']';
            $i++;
            next;
        }

        if ( $ch eq '[' ) { $in_class = 1; $i++; next; }

        if ( $ch eq '(' ) {
            my $rest = substr( $pattern, $i, 128 );

            if ( $rest =~ /^\((\?P?<([A-Za-z_][A-Za-z0-9_]*)>|\?'([A-Za-z_][A-Za-z0-9_]*)')/ ) {
                $count++;
                $names{$count} = defined $2 ? $2 : $3;
            }
            elsif ( $rest =~ /^\(\?/ ) {

                # (?:  (?=  (?!  (?<=  (?<!  (?>  (?#  (?imsx)  (?{ ... and friends
            }
            elsif ( $rest =~ /^\(\*/ ) {

                # backtracking control verb, never a capture
            }
            else {
                $count++;
            }
            $i++;
            next;
        }

        $i++;
    }

    return ( $count, \%names );
}

sub build_pattern {
    my ( $pattern, $flags ) = @_;

    my @mods;
    for my $flag ( @{ $flags || [] } ) {
        next if !defined $flag || $flag eq '';
        die "Unsupported flag '$flag' for the Perl engine\n" unless $ALLOWED_FLAGS{$flag};
        push @mods, $flag;
    }

    my $prefix = @mods ? '(?' . join( '', @mods ) . ')' : '';
    return $prefix . $pattern;
}

# Runs in the forked child: the parent kills it if it blows past the SLA, which
# is the only ReDoS guard perlre offers.
sub match_all {
    my ($req) = @_;

    my $text = defined $req->{text} ? $req->{text} : '';
    die "Input text exceeds maximum allowed size of $MAX_INPUT_SIZE bytes.\n"
        if length( Encode::encode_utf8($text) ) > $MAX_INPUT_SIZE;

    my $source = build_pattern( $req->{regex}, $req->{flags} );

    my $re = eval { qr/$source/ };
    die "Compilation failed: $@" if !defined $re;

    my ( $group_count, $group_names ) = scan_groups( $req->{regex} );
    die "Exceeded maximum allowed groups per match ($MAX_GROUPS).\n" if $group_count > $MAX_GROUPS;

    my @matches;
    while ( $text =~ /$re/g ) {
        die "Exceeded maximum allowed matches ($MAX_MATCHES).\n" if @matches >= $MAX_MATCHES;

        my @groups;
        for my $index ( 1 .. $group_count ) {
            next unless defined $-[$index];
            push @groups, {
                group_id => $index,
                name     => $group_names->{$index},
                content  => substr( $text, $-[$index], $+[$index] - $-[$index] ),
                start    => $-[$index] + 0,
                end      => $+[$index] + 0,
            };
        }

        push @matches, {
            match_id   => scalar(@matches),
            full_match => substr( $text, $-[0], $+[0] - $-[0] ),
            start      => $-[0] + 0,
            end        => $+[0] + 0,
            groups     => \@groups,
        };
    }

    return \@matches;
}

# Perl cannot interrupt a running regex, so the match happens in a child process
# that the parent reaps once the SLA expires.
sub run_with_timeout {
    my ( $req, $timeout_s ) = @_;

    pipe( my $reader, my $writer ) or die "pipe failed: $!\n";

    my $pid = fork();
    die "fork failed: $!\n" unless defined $pid;

    if ( $pid == 0 ) {
        close $reader;
        my $payload;
        eval {
            $payload = { matches => match_all($req) };
            1;
        } or do {
            my $message = "$@";
            $message =~ s/\s+\z//;
            $payload = { error => $message };
        };
        binmode $writer;
        print {$writer} $CODEC->encode($payload);
        close $writer;
        POSIX::_exit(0);
    }

    close $writer;

    my $select   = IO::Select->new($reader);
    my $deadline = Time::HiRes::time() + $timeout_s;
    my $buffer   = '';
    my $complete = 0;

    while (1) {
        my $remaining = $deadline - Time::HiRes::time();
        last if $remaining <= 0;

        my @ready = $select->can_read($remaining);
        last unless @ready;

        my $chunk = '';
        my $read  = sysread( $reader, $chunk, 65536 );
        if ( !defined $read || $read == 0 ) {

            # EOF: the child closed the pipe right before exiting.
            $complete = 1;
            last;
        }
        $buffer .= $chunk;
    }

    close $reader;

    if ( !$complete ) {
        kill 'KILL', $pid;
        waitpid( $pid, 0 );
        return { error => "TIMEOUT: $req->{engine_id} execution exceeded ${TIMEOUT_MS}ms SLA." };
    }

    waitpid( $pid, 0 );

    return { error => 'WORKER CRASH: match process exited without a result.' } if $buffer eq '';

    my $decoded = eval { $CODEC->decode($buffer) };
    return { error => 'WORKER CRASH: unreadable result from the match process.' } if !defined $decoded;

    return $decoded;
}

sub handle_dlq {
    my ( $redis, $task, $error ) = @_;
    eval {
        $task = {} unless ref $task eq 'HASH';
        $task->{attempt_count} = ( $task->{attempt_count} || 0 ) + 1;
        $task->{error_reason}  = $error;
        $redis->lpush( $DEAD_QUEUE, $CODEC->encode($task) );
        1;
    };
}

sub publish_result {
    my ( $redis, $task_id, $result ) = @_;

    my $json = $CODEC->encode($result);
    if ( length($json) > $MAX_JSON_SIZE ) {
        $result->{success} = JSON::PP::false;
        $result->{matches} = [];
        $result->{error}   = "Output JSON exceeds maximum allowed size of $MAX_JSON_SIZE bytes.";
        $json = $CODEC->encode($result);
    }

    $redis->setex( "result:$task_id", 60, $json );
    $redis->publish( "result:$task_id", 'ready' );
}

sub process_task {
    my ( $redis, $raw ) = @_;

    my $task = eval { $CODEC->decode($raw) };
    if ( !defined $task ) {
        handle_dlq( $redis, {}, 'JSON Parse error' );
        return;
    }

    if ( defined $task->{text_payload_id} && $task->{text_payload_id} ne '' ) {
        my $payload = $redis->get( $task->{text_payload_id} );
        if ( !defined $payload ) {
            my $message = 'Payload expired or missing from Redis';
            handle_dlq( $redis, $task, $message );
            publish_result(
                $redis,
                $task->{task_id},
                {
                    task_id           => $task->{task_id},
                    engine_id         => $task->{engine_id},
                    success           => JSON::PP::false,
                    matches           => [],
                    execution_time_ms => 0,
                    error             => $message,
                }
            );
            return;
        }
        $task->{text} = Encode::decode_utf8($payload);
    }

    my $started = Time::HiRes::time();
    my $outcome = eval { run_with_timeout( $task, $TIMEOUT_MS / 1000 ) };
    if ($@) {
        my $message = "$@";
        $message =~ s/\s+\z//;
        $outcome = { error => $message };
    }
    my $elapsed = ( Time::HiRes::time() - $started ) * 1000;

    handle_dlq( $redis, $task, $outcome->{error} ) if $outcome->{error};

    publish_result(
        $redis,
        $task->{task_id},
        {
            task_id           => $task->{task_id},
            engine_id         => $task->{engine_id},
            success           => $outcome->{error} ? JSON::PP::false : JSON::PP::true,
            matches           => $outcome->{error} ? [] : $outcome->{matches},
            execution_time_ms => $elapsed,
            error             => $outcome->{error},
        }
    );
}

sub listen_and_process {
    my ($redis) = @_;

    print "[Worker] Perl worker listening on '$QUEUE'...\n";

    # Perl runs single-threaded here, so the TTL heartbeat is refreshed from the
    # poll loop; brpop's 5s timeout keeps refreshes well inside the 15s TTL.
    my $last_beat = 0;

    while (1) {
        my $ok = eval {
            if ( time() - $last_beat >= 5 ) {
                eval { $redis->setex( $HEARTBEAT_KEY, 15, time() ); 1 };
                $last_beat = time();
            }

            # Non-zero timeout keeps idle TCP connections from being dropped silently.
            my $entry = $redis->brpop( $QUEUE, 5 );
            process_task( $redis, $entry->[1] ) if $entry && defined $entry->[1];
            1;
        };
        if ( !$ok ) {
            my $message = "$@";
            $message =~ s/\s+\z//;
            print STDERR "[Error] Perl worker loop failure: $message\n";
            sleep 2;
        }
    }
}

1;
