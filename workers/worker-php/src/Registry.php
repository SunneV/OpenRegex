<?php

namespace OpenRegex\Worker;

class Registry {
    private static function flagMetadata(string $name): array {
        return match ($name) {
            'i' => ['Case-insensitive matching.', 'Basic'],
            'm' => ['Multiline mode. Makes ^ and $ work per line.', 'Basic'],
            's' => ['DotAll mode. Makes . match newline.', 'Basic'],
            'x' => ['Extended/free-spacing pattern mode.', 'Basic'],
            'A' => ['Force pattern to be anchored at the start of the subject.', 'Advance'],
            'D' => ['$ matches only at the true end of the subject.', 'Advance'],
            'S' => ['Compatibility study modifier; ignored in modern PHP/PCRE2.', 'Unique'],
            'U' => ['Ungreedy mode; quantifiers are lazy by default.', 'Advance'],
            'X' => ['Extra syntax checking for unknown escaped letters.', 'Unique'],
            'J' => ['Allow duplicate named capturing groups.', 'Unique'],
            'u' => ['Treat subject and pattern as UTF-8.', 'Basic'],
            'n' => ['No auto-capture mode (PHP 8.2+).', 'Advance'],
            'r' => ['Restrict caseless ASCII/non-ASCII boundary folds (PHP 8.4+).', 'Unique'],
            default => ["Flag ({$name})", 'Basic'],
        };
    }

    private static function buildEngineFlags(array $names): array {
        $flags = [];
        foreach ($names as $name) {
            [$description, $group] = self::flagMetadata($name);
            $flags[] = [
                'name' => $name,
                'description' => $description,
                'group' => $group,
            ];
        }
        return $flags;
    }

    public static function registerEngines($client) {
        $workerVersion = getenv('WORKER_VERSION') ?: '1.0.0';
        $releaseDate = getenv('WORKER_RELEASE_DATE') ?: 'Unreleased';

        $pcreFlagNames = ['i', 'm', 's', 'x', 'A', 'D', 'S', 'U', 'X', 'J', 'u'];

        if (defined('PHP_VERSION_ID') && PHP_VERSION_ID >= 80200) {
            $pcreFlagNames[] = 'n';
        }

        if (defined('PHP_VERSION_ID') && PHP_VERSION_ID >= 80400) {
            $pcreFlagNames[] = 'r';
        }

        $workerInfo = [
            'worker_name' => 'worker-php',
            'worker_version' => $workerVersion,
            'worker_release_date' => $releaseDate,
            'engines' => [
                [
                    'engine_id' => 'php_pcre',
                    'engine_language_type' => 'PHP',
                    'engine_language_version' => phpversion(),
                    'engine_regex_lib' => 'PCRE',
                    'engine_regex_lib_version' => PCRE_VERSION,
                    'engine_label' => 'PHP (PCRE)',
                    'engine_capabilities' => [
                        'flags' => self::buildEngineFlags($pcreFlagNames),
                        'supports_lookaround' => true,
                        'supports_backrefs' => true
                    ],
                    'engine_docs' => [
                        'trivia' => [
                            "Powered by the highly compatible Perl Compatible Regular Expressions (PCRE/PCRE2) C library.",
                            "PCRE2 is distributed under BSD-3-Clause licensing with the PCRE2 exception.",
                            "The standard preg_* functions utilize an NFA backtracking engine.",
                            "Susceptible to ReDoS if patterns are poorly optimized; however, execution is protected internally via pcre.backtrack_limit.",
                            "The 'u' (PCRE_UTF8) modifier is automatically appended by OpenRegex to safely navigate string payloads."
                        ],
                        'cheat_sheet_url' => 'https://www.php.net/manual/en/reference.pcre.pattern.syntax.php'
                    ],
                    'engine_cheat_sheet' => [
                        [
                            'category' => 'Character Classes & Escapes',
                            'items' => [
                                ['character' => '.', 'description' => "Any character except newline unless 's' flag is set"],
                                ['character' => '\w', 'description' => 'Word character; ASCII by default, Unicode-aware with UCP mode'],
                                ['character' => '\W', 'description' => 'Non-word character'],
                                ['character' => '\d', 'description' => 'Decimal digit; ASCII by default, Unicode-aware with UCP mode'],
                                ['character' => '\D', 'description' => 'Non-digit'],
                                ['character' => '\s', 'description' => 'Whitespace character; ASCII by default, Unicode-aware with UCP mode'],
                                ['character' => '\S', 'description' => 'Non-whitespace character'],
                                ['character' => '\h', 'description' => 'Horizontal whitespace'],
                                ['character' => '\v', 'description' => 'Vertical whitespace'],
                                ['character' => '\p{L}', 'description' => 'Unicode letter property'],
                                ['character' => '\P{L}', 'description' => 'Negated Unicode letter property'],
                                ['character' => '[a-z]', 'description' => 'Character class'],
                                ['character' => '[^a-z]', 'description' => 'Negated character class']
                            ]
                        ],
                        [
                            'category' => 'Anchors & Boundaries',
                            'items' => [
                                ['character' => '^', 'description' => "Start of subject, or start of line if 'm' flag is set"],
                                ['character' => '$', 'description' => "End of subject or before final newline, or end of line if 'm' flag is set"],
                                ['character' => '\A', 'description' => 'Absolute start of subject'],
                                ['character' => '\z', 'description' => 'Absolute end of subject'],
                                ['character' => '\Z', 'description' => 'End of subject or before final newline'],
                                ['character' => '\G', 'description' => 'First matching position in subject'],
                                ['character' => '\b', 'description' => 'Word boundary'],
                                ['character' => '\B', 'description' => 'Non-word boundary']
                            ]
                        ],
                        [
                            'category' => 'Quantifiers',
                            'items' => [
                                ['character' => '*', 'description' => '0 or more times, greedy'],
                                ['character' => '+', 'description' => '1 or more times, greedy'],
                                ['character' => '?', 'description' => '0 or 1 time, greedy'],
                                ['character' => '{m}', 'description' => 'Exactly m times'],
                                ['character' => '{m,n}', 'description' => 'Between m and n times, greedy'],
                                ['character' => '*?', 'description' => '0 or more times, lazy'],
                                ['character' => '+?', 'description' => '1 or more times, lazy'],
                                ['character' => '??', 'description' => '0 or 1 time, lazy'],
                                ['character' => '{m,n}?', 'description' => 'Between m and n times, lazy'],
                                ['character' => '*+', 'description' => '0 or more times, possessive'],
                                ['character' => '++', 'description' => '1 or more times, possessive'],
                                ['character' => '?+', 'description' => '0 or 1 time, possessive'],
                                ['character' => '{m,n}+', 'description' => 'Between m and n times, possessive']
                            ]
                        ],
                        [
                            'category' => 'Grouping & Backreferences',
                            'items' => [
                                ['character' => '(...)', 'description' => 'Capturing group'],
                                ['character' => '(?:...)', 'description' => 'Non-capturing group'],
                                ['character' => 'x|y', 'description' => 'Alternation (match x or y)'],
                                ['character' => '(?<name>...)', 'description' => 'Named capturing group'],
                                ['character' => "(?'name'...)", 'description' => 'Named capturing group'],
                                ['character' => '(?P<name>...)', 'description' => 'Named capturing group'],
                                ['character' => '\1', 'description' => 'Backreference to capture group 1'],
                                ['character' => '\k<name>', 'description' => 'Backreference to named group'],
                                ['character' => '(?&name)', 'description' => 'Subroutine call to a named group'],
                                ['character' => '(?R)', 'description' => 'Recursive subroutine call to the whole pattern']
                            ]
                        ],
                        [
                            'category' => 'Lookarounds & Advanced',
                            'items' => [
                                ['character' => '(?=...)', 'description' => 'Positive lookahead'],
                                ['character' => '(?!...)', 'description' => 'Negative lookahead'],
                                ['character' => '(?<=...)', 'description' => 'Positive lookbehind with fixed-length alternatives'],
                                ['character' => '(?<!...)', 'description' => 'Negative lookbehind with fixed-length alternatives'],
                                ['character' => '(?>...)', 'description' => 'Atomic group'],
                                ['character' => '(*SKIP)(*F)', 'description' => 'Backtracking-control verbs commonly used to skip alternatives'],
                                ['character' => '\K', 'description' => 'Reset the start of the reported match'],
                                ['character' => '(?(condition)yes|no)', 'description' => 'Conditional subpattern'],
                                ['character' => '(?i)', 'description' => 'Inline flag: Case-insensitive'],
                                ['character' => '(?m)', 'description' => 'Inline flag: Multiline'],
                                ['character' => '(?s)', 'description' => 'Inline flag: Dot matches newline'],
                                ['character' => '(?x)', 'description' => 'Inline flag: Extended / free-spacing'],
                                ['character' => '(?U)', 'description' => 'Inline flag: Ungreedy quantifiers'],
                                ['character' => '(?J)', 'description' => 'Inline flag: Allow duplicate named groups']
                            ]
                        ]
                    ],
                    'engine_examples' => [
                        [
                            'regex' => '(?<IP>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))(/(\d{1,2}))?(?:-(?<IP2>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)))?(?::(?<port>\d{1,5}))?',
                            'text' => "This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255\n192.168.1.1-192.168.1.255:80\n192.168.1.0/24:80"
                        ]
                    ]
                ]
            ]
        ];

        $client->hset('openregex:workers', 'worker-php', json_encode($workerInfo));
        echo "[Worker] Registered 'worker-php' with 1 engine.\n";
    }
}
