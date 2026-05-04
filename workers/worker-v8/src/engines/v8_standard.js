import {
  LANGUAGE_VERSION,
  V8_VERSION,
  CAT_CLASSES,
  CAT_ANCHORS,
  CAT_QUANTIFIERS,
  CAT_GROUPS,
  CAT_ADVANCED,
  buildEngineFlags
} from './common.js';

export const engine = {
  engine_id: "v8_standard",
  engine_language_type: "JavaScript",
  engine_language_version: LANGUAGE_VERSION,
  engine_regex_lib: "V8",
  engine_regex_lib_version: V8_VERSION,
  engine_label: "JavaScript (V8)",
  engine_capabilities: {
    flags: buildEngineFlags("d", "g", "i", "m", "s", "u", "v", "y"),
    supports_lookaround: true,
    supports_backrefs: true
  },
  engine_docs: {
    trivia: [
      "Native RegExp engine running in Node.js (V8).",
      "V8 is distributed under the BSD-3-Clause license.",
      "Supports modern ECMAScript RegExp features including named captures, lookbehind, match indices, Unicode property escapes, and the 'v' flag when available in the runtime.",
      "Uses a backtracking engine for many patterns and can be susceptible to ReDoS if patterns are poorly optimized.",
      "The 'u' and 'v' flags are mutually exclusive Unicode modes."
    ],
    cheat_sheet_url: "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_expressions"
  },
  engine_cheat_sheet: [
    {
      category: CAT_CLASSES,
      items: [
        { character: ".", description: "Any character except line terminators unless 's' flag is set" },
        { character: "\\w", description: "ASCII word character ([A-Za-z0-9_])" },
        { character: "\\W", description: "Non-ASCII-word character" },
        { character: "\\d", description: "ASCII decimal digit ([0-9])" },
        { character: "\\D", description: "Non-digit" },
        { character: "\\s", description: "Whitespace character" },
        { character: "\\S", description: "Non-whitespace character" },
        { character: "\\p{L}", description: "Unicode letter property; requires 'u' or 'v' flag" },
        { character: "\\P{L}", description: "Negated Unicode letter property; requires 'u' or 'v' flag" },
        { character: "[a-z]", description: "Character class" },
        { character: "[^a-z]", description: "Negated character class" }
      ]
    },
    {
      category: CAT_ANCHORS,
      items: [
        { character: "^", description: "Start of input, or start of line if 'm' flag is set" },
        { character: "$", description: "End of input, or end of line if 'm' flag is set" },
        { character: "\\b", description: "ASCII word boundary" },
        { character: "\\B", description: "Non-ASCII-word boundary" }
      ]
    },
    {
      category: CAT_QUANTIFIERS,
      items: [
        { character: "*", description: "0 or more times, greedy" },
        { character: "+", description: "1 or more times, greedy" },
        { character: "?", description: "0 or 1 time, greedy" },
        { character: "{m}", description: "Exactly m times" },
        { character: "{m,n}", description: "Between m and n times, greedy" },
        { character: "*?", description: "0 or more times, lazy" },
        { character: "+?", description: "1 or more times, lazy" },
        { character: "??", description: "0 or 1 time, lazy" },
        { character: "{m,n}?", description: "Between m and n times, lazy" }
      ]
    },
    {
      category: CAT_GROUPS,
      items: [
        { character: "(...)", description: "Capturing group" },
        { character: "(?:...)", description: "Non-capturing group" },
        { character: "x|y", description: "Alternation (match x or y)" },
        { character: "(?<name>...)", description: "Named capturing group" },
        { character: "\\1", description: "Backreference to capture group 1" },
        { character: "\\k<name>", description: "Backreference to a named capture group" }
      ]
    },
    {
      category: CAT_ADVANCED,
      items: [
        { character: "(?=...)", description: "Positive lookahead" },
        { character: "(?!...)", description: "Negative lookahead" },
        { character: "(?<=...)", description: "Positive lookbehind" },
        { character: "(?<!...)", description: "Negative lookbehind" },
        { character: "\\p{RGI_Emoji}", description: "Unicode string property; requires 'v' flag" },
        { character: "[\\p{White_Space}&&\\p{ASCII}]", description: "Set intersection; requires 'v' flag" },
        { character: "[\\p{Decimal_Number}--[0-9]]", description: "Set subtraction; requires 'v' flag" },
        { character: "(?i:...)", description: "Scoped modifier: case-insensitive; requires runtime support for RegExp modifiers" },
        { character: "(?-i:...)", description: "Scoped modifier: disable case-insensitive; requires runtime support for RegExp modifiers" }
      ]
    }
  ],
  engine_examples: [
    {
      regex: "(?<IP>(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d))(/(\\d{1,2}))?(?:-(?<IP2>(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)))?(?::(?<port>\\d{1,5}))?",
      text: "This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255\n192.168.1.1-192.168.1.255:80\n192.168.1.0/24:80"
    }
  ]
};
