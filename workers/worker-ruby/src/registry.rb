# frozen_string_literal: true

require 'json'

module OpenRegex
  # Builds the engine descriptor published to the backend via Redis.
  module Registry
    WORKER_NAME = 'worker-ruby'

    FLAG_METADATA = {
      'i' => ['Case-insensitive matching.', 'Basic'],
      'm' => ['Multi-line mode. In Ruby this makes . match newline (dotall elsewhere).', 'Unique'],
      'x' => ['Extended mode. Ignores unescaped whitespace and allows comments.', 'Basic'],
      'o' => ['Interpolate the pattern only once; accepted for parity, no effect here.', 'Unique']
    }.freeze

    def self.build_flags(names)
      names.map do |name|
        description, group = FLAG_METADATA.fetch(name, ["Flag (#{name})", 'Basic'])
        { 'name' => name, 'description' => description, 'group' => group }
      end
    end

    def self.onigmo_version
      # Onigmo does not expose its version number to Ruby code; report the host runtime.
      "bundled with Ruby #{RUBY_VERSION}"
    end

    def self.worker_info
      {
        'worker_name' => WORKER_NAME,
        'worker_version' => ENV.fetch('WORKER_VERSION', 'Unknown'),
        'worker_release_date' => ENV.fetch('WORKER_RELEASE_DATE', 'Unreleased'),
        # Contract version: "1.1" = match offsets normalized to Unicode code points.
        'worker_schema_version' => '1.1',
        'engines' => [engine]
      }
    end

    def self.engine
      {
        'engine_id' => 'ruby_onigmo',
        'engine_language_type' => 'Ruby',
        'engine_language_version' => RUBY_VERSION,
        'engine_regex_lib' => 'Onigmo',
        'engine_regex_lib_version' => onigmo_version,
        'engine_label' => "Ruby #{RUBY_VERSION.split('.').first(2).join('.')} (Onigmo)",
        'engine_capabilities' => {
          'flags' => build_flags(%w[i m x o]),
          'supports_lookaround' => true,
          'supports_backrefs' => true
        },
        'engine_docs' => {
          'trivia' => [
            'Onigmo is a fork of Oniguruma maintained specifically for Ruby; it adds Perl-style constructs such as \\K and the absence operator.',
            'Onigmo is distributed under the BSD-2-Clause license; Ruby itself under the Ruby License or BSD-2-Clause.',
            "Ruby's 'm' flag is NOT multiline in the Perl sense - it is dotall. ^ and $ always match at line boundaries in Ruby.",
            'Ruby 3.2 introduced Regexp.timeout, a global ReDoS guard that aborts a match after a configurable wall-clock budget. OpenRegex runs every request under that guard.',
            'Ruby 3.2 also added a memoizing optimizer that makes many otherwise exponential patterns run in linear time.',
            'Match offsets in Ruby MatchData are character indices, never byte indices, so multibyte subjects behave intuitively.',
            'Named groups switch off numbered capturing: once (?<name>...) appears in a pattern, plain (...) groups stop capturing.'
          ],
          'cheat_sheet_url' => 'https://docs.ruby-lang.org/en/master/Regexp.html'
        },
        'engine_cheat_sheet' => cheat_sheet,
        'engine_examples' => [
          {
            'regex' => '(?<IP>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))(?:/(?<mask>\d{1,2}))?(?::(?<port>\d{1,5}))?',
            'text' => "This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255"
          }
        ]
      }
    end

    def self.cheat_sheet
      [
        {
          'category' => 'Character Classes & Escapes',
          'items' => [
            { 'character' => '.', 'description' => "Any character except newline unless the 'm' flag is set" },
            { 'character' => '\\w', 'description' => 'Word character; ASCII-only unless the pattern is Unicode-encoded' },
            { 'character' => '\\W', 'description' => 'Non-word character' },
            { 'character' => '\\d', 'description' => 'Decimal digit (ASCII)' },
            { 'character' => '\\D', 'description' => 'Non-digit' },
            { 'character' => '\\s', 'description' => 'Whitespace character' },
            { 'character' => '\\S', 'description' => 'Non-whitespace character' },
            { 'character' => '\\h', 'description' => 'Hexadecimal digit character' },
            { 'character' => '\\R', 'description' => 'Generic linebreak (\\r\\n, \\n, \\v, \\f, \\r, U+0085, U+2028, U+2029)' },
            { 'character' => '\\p{Alpha}', 'description' => 'POSIX or Unicode property class' },
            { 'character' => '\\p{Han}', 'description' => 'Unicode script property' },
            { 'character' => '[[:alpha:]]', 'description' => 'POSIX bracket expression' },
            { 'character' => '[a-z&&[^aeiou]]', 'description' => 'Character class intersection' }
          ]
        },
        {
          'category' => 'Anchors & Boundaries',
          'items' => [
            { 'character' => '^', 'description' => 'Start of line - always line-based in Ruby' },
            { 'character' => '$', 'description' => 'End of line - always line-based in Ruby' },
            { 'character' => '\\A', 'description' => 'Start of string' },
            { 'character' => '\\z', 'description' => 'End of string' },
            { 'character' => '\\Z', 'description' => 'End of string, ignoring a trailing newline' },
            { 'character' => '\\b', 'description' => 'Word boundary' },
            { 'character' => '\\B', 'description' => 'Non-word boundary' },
            { 'character' => '\\G', 'description' => 'Where the previous match ended' },
            { 'character' => '\\K', 'description' => 'Keep-out: drop everything matched so far from the reported match' }
          ]
        },
        {
          'category' => 'Quantifiers',
          'items' => [
            { 'character' => '*', 'description' => '0 or more times, greedy' },
            { 'character' => '+', 'description' => '1 or more times, greedy' },
            { 'character' => '?', 'description' => '0 or 1 time, greedy' },
            { 'character' => '{m,n}', 'description' => 'Between m and n times, greedy' },
            { 'character' => '*?', 'description' => '0 or more times, lazy' },
            { 'character' => '+?', 'description' => '1 or more times, lazy' },
            { 'character' => '??', 'description' => '0 or 1 time, lazy' },
            { 'character' => '*+', 'description' => '0 or more times, possessive' },
            { 'character' => '++', 'description' => '1 or more times, possessive' },
            { 'character' => '?+', 'description' => '0 or 1 time, possessive' }
          ]
        },
        {
          'category' => 'Grouping & Backreferences',
          'items' => [
            { 'character' => '(...)', 'description' => 'Capturing group' },
            { 'character' => '(?:...)', 'description' => 'Non-capturing group' },
            { 'character' => 'x|y', 'description' => 'Alternation (match x or y)' },
            { 'character' => '(?<name>...)', 'description' => 'Named capturing group; disables numbered capture' },
            { 'character' => "(?'name'...)", 'description' => 'Named capturing group, quoted syntax' },
            { 'character' => '\\1', 'description' => 'Backreference to capture group 1' },
            { 'character' => '\\k<name>', 'description' => 'Backreference to a named group' },
            { 'character' => '\\k<-1>', 'description' => 'Relative backreference to the previous group' },
            { 'character' => '\\g<name>', 'description' => 'Subexpression call (recursion into a named group)' },
            { 'character' => '\\g<0>', 'description' => 'Recursive call of the whole pattern' }
          ]
        },
        {
          'category' => 'Lookarounds & Advanced',
          'items' => [
            { 'character' => '(?=...)', 'description' => 'Positive lookahead' },
            { 'character' => '(?!...)', 'description' => 'Negative lookahead' },
            { 'character' => '(?<=...)', 'description' => 'Positive lookbehind' },
            { 'character' => '(?<!...)', 'description' => 'Negative lookbehind' },
            { 'character' => '(?>...)', 'description' => 'Atomic group; prevents backtracking' },
            { 'character' => '(?~...)', 'description' => 'Absence operator: match anything that does not contain the subpattern' },
            { 'character' => '(?(1)yes|no)', 'description' => 'Conditional on whether group 1 participated' },
            { 'character' => '(?i)', 'description' => 'Inline flag: case-insensitive' },
            { 'character' => '(?m)', 'description' => 'Inline flag: dot matches newline' },
            { 'character' => '(?x)', 'description' => 'Inline flag: extended / free-spacing' },
            { 'character' => '(?i:...)', 'description' => 'Scoped inline flag group' },
            { 'character' => '(?-i:...)', 'description' => 'Scoped inline flag group, flag turned off' }
          ]
        }
      ]
    end
  end
end
