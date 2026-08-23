package OpenRegex::Registry;

use strict;
use warnings;

our $WORKER_NAME = 'worker-perl';

my %FLAG_METADATA = (
    'i' => [ 'Case-insensitive matching.',                                   'Basic' ],
    'm' => [ 'Multiline mode. Makes ^ and $ match at line boundaries.',      'Basic' ],
    's' => [ 'DotAll mode. Makes . match newline.',                          'Basic' ],
    'x' => [ 'Extended mode. Ignores unescaped whitespace, allows comments.', 'Basic' ],
    'a' => [ 'ASCII-restricted mode for \\d, \\w, \\s and \\b.',             'Advance' ],
    'u' => [ 'Unicode ruleset for character classes and casing.',            'Advance' ],
    'l' => [ 'Locale ruleset for character classes and casing.',             'Unique' ],
    'n' => [ 'No auto-capture: plain (...) groups stop capturing.',          'Advance' ],
    'p' => [ 'Preserve the matched string in ${^MATCH}; legacy in 5.20+.',   'Unique' ],
);

sub build_flags {
    my @names = @_;
    my @flags;
    for my $name (@names) {
        my $meta = $FLAG_METADATA{$name} || [ "Flag ($name)", 'Basic' ];
        push @flags, { name => $name, description => $meta->[0], group => $meta->[1] };
    }
    return \@flags;
}

sub worker_info {
    my $version = sprintf( '%vd', $^V );

    return {
        worker_name         => $WORKER_NAME,
        worker_version      => $ENV{WORKER_VERSION}      || 'Unknown',
        worker_release_date => $ENV{WORKER_RELEASE_DATE} || 'Unreleased',

        # Contract version: "1.1" = match offsets normalized to Unicode code points.
        worker_schema_version => '1.1',
        engines               => [ engine($version) ],
    };
}

sub engine {
    my ($version) = @_;

    return {
        engine_id               => 'perl_standard',
        engine_language_type    => 'Perl',
        engine_language_version => $version,
        engine_regex_lib        => 'perlre (built-in)',
        engine_regex_lib_version => $version,
        engine_label            => "Perl $version (perlre)",
        engine_capabilities     => {
            flags               => build_flags(qw(i m s x a u l n p)),
            supports_lookaround => 1,
            supports_backrefs   => 1,
        },
        engine_docs => {
            trivia => [
                'This is the original engine everyone else calls "Perl-compatible" - PCRE was written to imitate it, not the other way round.',
                'Perl is dual-licensed under the Artistic License 1.0 and the GNU General Public License v1 or later.',
                'Perl regexes can execute arbitrary Perl code with (?{ ... }) and (??{ ... }); OpenRegex compiles patterns without the use re "eval" pragma, so those constructs are rejected.',
                'Recursion via (?R), (?1) and (?&name) landed in Perl 5.10, together with named captures and possessive quantifiers.',
                'The backtracking control verbs (*PRUNE), (*SKIP), (*FAIL) and (*ACCEPT) are Perl inventions later copied by PCRE.',
                'Perl has no built-in match timeout, so this worker runs every pattern in a forked child process that is killed when the SLA expires.',
                'Since 5.18 the /a, /u and /l modifiers let a single pattern pick its character-class ruleset explicitly.',
            ],
            cheat_sheet_url => 'https://perldoc.perl.org/perlre',
        },
        engine_cheat_sheet => cheat_sheet(),
        engine_examples    => [
            {
                regex => '(?<IP>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))(?:/(?<mask>\d{1,2}))?(?::(?<port>\d{1,5}))?',
                text  => "This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255",
            }
        ],
    };
}

sub cheat_sheet {
    return [
        {
            category => 'Character Classes & Escapes',
            items    => [
                { character => '.',           description => "Any character except newline unless the 's' flag is set" },
                { character => '\w',          description => 'Word character; Unicode by default, ASCII-only under /a' },
                { character => '\W',          description => 'Non-word character' },
                { character => '\d',          description => 'Decimal digit; Unicode by default, ASCII-only under /a' },
                { character => '\D',          description => 'Non-digit' },
                { character => '\s',          description => 'Whitespace character' },
                { character => '\S',          description => 'Non-whitespace character' },
                { character => '\h',          description => 'Horizontal whitespace' },
                { character => '\v',          description => 'Vertical whitespace' },
                { character => '\R',          description => 'Generic linebreak, including CRLF as one unit' },
                { character => '\N',          description => 'Any character except newline, regardless of /s' },
                { character => '\p{L}',       description => 'Unicode property' },
                { character => '\X',          description => 'Extended grapheme cluster' },
                { character => '[[:alpha:]]', description => 'POSIX bracket expression' },
            ],
        },
        {
            category => 'Anchors & Boundaries',
            items    => [
                { character => '^',   description => "Start of string, or start of line under 'm'" },
                { character => '$',   description => "End of string or before a trailing newline, per line under 'm'" },
                { character => '\A',  description => 'Absolute start of string' },
                { character => '\z',  description => 'Absolute end of string' },
                { character => '\Z',  description => 'End of string, ignoring a trailing newline' },
                { character => '\G',  description => 'Where the previous /g match ended' },
                { character => '\b',  description => 'Word boundary' },
                { character => '\B',  description => 'Non-word boundary' },
                { character => '\b{wb}', description => 'Unicode word boundary (5.22+)' },
                { character => '\K',  description => 'Keep-out: drop everything to the left from the reported match' },
            ],
        },
        {
            category => 'Quantifiers',
            items    => [
                { character => '*',      description => '0 or more times, greedy' },
                { character => '+',      description => '1 or more times, greedy' },
                { character => '?',      description => '0 or 1 time, greedy' },
                { character => '{m,n}',  description => 'Between m and n times, greedy' },
                { character => '*?',     description => '0 or more times, lazy' },
                { character => '+?',     description => '1 or more times, lazy' },
                { character => '??',     description => '0 or 1 time, lazy' },
                { character => '*+',     description => '0 or more times, possessive' },
                { character => '++',     description => '1 or more times, possessive' },
                { character => '?+',     description => '0 or 1 time, possessive' },
                { character => '{m,n}+', description => 'Between m and n times, possessive' },
            ],
        },
        {
            category => 'Grouping & Backreferences',
            items    => [
                { character => '(...)',        description => 'Capturing group' },
                { character => '(?:...)',      description => 'Non-capturing group' },
                { character => 'x|y',          description => 'Alternation (match x or y)' },
                { character => '(?<name>...)', description => 'Named capturing group' },
                { character => '(?P<name>...)', description => 'Named capturing group, Python-compatible syntax' },
                { character => '\1',           description => 'Backreference to capture group 1' },
                { character => '\g{-1}',       description => 'Relative backreference to the previous group' },
                { character => '\k<name>',     description => 'Backreference to a named group' },
                { character => '(?|...|...)',  description => 'Branch reset: alternatives share capture numbers' },
                { character => '(?R)',         description => 'Recurse into the whole pattern' },
                { character => '(?1)',         description => 'Recurse into group 1' },
                { character => '(?&name)',     description => 'Recurse into a named group' },
            ],
        },
        {
            category => 'Lookarounds & Advanced',
            items    => [
                { character => '(?=...)',  description => 'Positive lookahead' },
                { character => '(?!...)',  description => 'Negative lookahead' },
                { character => '(?<=...)', description => 'Positive lookbehind; variable length since 5.30 (experimental)' },
                { character => '(?<!...)', description => 'Negative lookbehind' },
                { character => '(?>...)',  description => 'Atomic group; prevents backtracking' },
                { character => '(*PRUNE)', description => 'Backtracking verb: discard the current match attempt' },
                { character => '(*SKIP)',  description => 'Backtracking verb: restart scanning past this point' },
                { character => '(*FAIL)',  description => 'Backtracking verb: force a failure' },
                { character => '(*ACCEPT)', description => 'Backtracking verb: accept the match immediately' },
                { character => '(?(1)yes|no)', description => 'Conditional on whether group 1 matched' },
                { character => '(?i)',     description => 'Inline flag: case-insensitive' },
                { character => '(?s)',     description => 'Inline flag: dot matches newline' },
                { character => '(?x)',     description => 'Inline flag: extended / free-spacing' },
                { character => '(?i:...)', description => 'Scoped inline flag group' },
            ],
        },
    ];
}

1;
