import {
    LANGUAGE_VERSION,
    CAT_CLASSES,
    CAT_ANCHORS,
    CAT_QUANTIFIERS,
    CAT_GROUPS,
    buildEngineFlags
} from './common.js';

export const engine = {
    engine_id: "v8_re2",
    engine_language_type: "JavaScript",
    engine_language_version: LANGUAGE_VERSION,
    engine_regex_lib: "re2",
    engine_regex_lib_version: "1.24.0",
    engine_label: "JavaScript (RE2)",
    engine_capabilities: {
        flags: buildEngineFlags("g", "i", "m", "s", "u", "y", "d"),
        supports_lookaround: false,
        supports_backrefs: false
    },
    engine_docs: {
        trivia: [
            "Wraps Google's RE2 C++ library for Node.js.",
            "The node-re2 package and RE2 are distributed under BSD-3-Clause licenses.",
            "Guarantees linear-time matching, making it safe against catastrophic-backtracking ReDoS.",
            "RE2 always operates in Unicode mode in node-re2; the 'u' flag is accepted and added implicitly.",
            "Does not support lookarounds, backreferences, atomic groups, or possessive quantifiers."
        ],
        cheat_sheet_url: "https://github.com/uhop/node-re2"
    },
    engine_cheat_sheet: [
        {
            category: CAT_CLASSES,
            items: [
                {character: ".", description: "Any character except line terminators unless 's' flag is set"},
                {character: "\\w", description: "ASCII word character ([0-9A-Za-z_])"},
                {character: "\\W", description: "Non-ASCII-word character"},
                {character: "\\d", description: "ASCII decimal digit ([0-9])"},
                {character: "\\D", description: "Non-digit"},
                {character: "\\s", description: "Whitespace character"},
                {character: "\\S", description: "Non-whitespace character"},
                {character: "\\p{L}", description: "Unicode letter property"},
                {character: "\\P{L}", description: "Negated Unicode letter property"},
                {character: "[a-z]", description: "Character class"},
                {character: "[^a-z]", description: "Negated character class"}
            ]
        },
        {
            category: CAT_ANCHORS,
            items: [
                {character: "^", description: "Start of input, or start of line if 'm' flag is set"},
                {character: "$", description: "End of input, or end of line if 'm' flag is set"},
                {character: "\\b", description: "ASCII word boundary"},
                {character: "\\B", description: "Non-ASCII-word boundary"}
            ]
        },
        {
            category: CAT_QUANTIFIERS,
            items: [
                {character: "*", description: "0 or more times, greedy"},
                {character: "+", description: "1 or more times, greedy"},
                {character: "?", description: "0 or 1 time, greedy"},
                {character: "{m}", description: "Exactly m times"},
                {character: "{m,n}", description: "Between m and n times, greedy"},
                {character: "*?", description: "0 or more times, lazy"},
                {character: "+?", description: "1 or more times, lazy"},
                {character: "??", description: "0 or 1 time, lazy"},
                {character: "{m,n}?", description: "Between m and n times, lazy"}
            ]
        },
        {
            category: CAT_GROUPS,
            items: [
                {character: "(...)", description: "Capturing group"},
                {character: "(?:...)", description: "Non-capturing group"},
                {character: "x|y", description: "Alternation (match x or y)"},
                {character: "(?<name>...)", description: "Named capturing group"}
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
