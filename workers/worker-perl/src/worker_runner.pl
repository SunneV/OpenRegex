#!/usr/bin/env perl

use strict;
use warnings;

use FindBin;
use lib "$FindBin::Bin";

# Container logs are not a TTY, so without this nothing shows up until exit.
$| = 1;

use JSON::PP;
use Redis;

use OpenRegex::Processor;
use OpenRegex::Registry;

my $WORKERS_HASH_KEY = 'openregex:workers';

my $redis_url = $ENV{REDIS_URL} || 'redis://redis:6379';
my $server    = $redis_url;
$server =~ s{^redis://}{};
$server =~ s{/.*$}{};
$server = 'redis:6379' if $server eq '';

my $redis = Redis->new( server => $server, reconnect => 60, every => 500_000 );

# The heartbeat must be live before registration so discovery never sees a
# registered worker without one.
eval { $redis->setex( $OpenRegex::Processor::HEARTBEAT_KEY, 15, time() ); 1 };

my $codec = JSON::PP->new->utf8;
$redis->hset( $WORKERS_HASH_KEY, $OpenRegex::Registry::WORKER_NAME,
    $codec->encode( OpenRegex::Registry::worker_info() ) );
print "[Worker] Registered '$OpenRegex::Registry::WORKER_NAME' with 1 engine.\n";

# Graceful unregister on shutdown (docker stop / Ctrl+C).
my $unregister = sub {
    eval {
        $redis->hdel( $WORKERS_HASH_KEY, $OpenRegex::Registry::WORKER_NAME );
        $redis->del($OpenRegex::Processor::HEARTBEAT_KEY);
        1;
    };
    exit 0;
};
$SIG{TERM} = $unregister;
$SIG{INT}  = $unregister;

OpenRegex::Processor::listen_and_process($redis);
