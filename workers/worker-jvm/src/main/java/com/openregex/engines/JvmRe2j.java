package com.openregex.engines;

import com.openregex.models.Models.*;
import java.util.List;

public class JvmRe2j {
    public static final EngineInfo ENGINE = new EngineInfo(
            "jvm_re2j",
            "Java",
            Common.JAVA_VERSION,
            "re2j",
            "1.7",
            "Java (RE2J)",
            new EngineCapabilities(
                    Common.flags("i", "m", "s", "U"),
                    false,
                    false
            ),
            new EngineDocs(
                    List.of(
                            "Google's RE2 implementation for the JVM.",
                            "RE2/J is distributed under a BSD-style license derived from the Go license.",
                            "Guarantees linear O(n) execution time relative to input size.",
                            "Strictly avoids backtracking, making it immune to ReDoS caused by catastrophic backtracking.",
                            "Does not support lookarounds, backreferences, atomic groups, or possessive quantifiers."
                    ),
                    "https://github.com/google/re2j"
            ),
            List.of(
                    new CheatSheetCategory(
                            Common.CAT_CLASSES,
                            List.of(
                                    new CheatSheetItem(".", "Any character (except newline unless 's' flag is set)"),
                                    new CheatSheetItem("\\w", "ASCII word character ([0-9A-Za-z_])"),
                                    new CheatSheetItem("\\W", "Non-ASCII-word character"),
                                    new CheatSheetItem("\\d", "ASCII decimal digit ([0-9])"),
                                    new CheatSheetItem("\\D", "Non-digit"),
                                    new CheatSheetItem("\\s", "ASCII whitespace character ([\\t\\n\\f\\r ])"),
                                    new CheatSheetItem("\\S", "Non-whitespace character"),
                                    new CheatSheetItem("[a-z]", "Character class (inclusive)"),
                                    new CheatSheetItem("[^a-z]", "Negated character class"),
                                    new CheatSheetItem("\\p{Greek}", "Unicode character class"),
                                    new CheatSheetItem("\\P{Greek}", "Negated Unicode character class")
                            )
                    ),
                    new CheatSheetCategory(
                            Common.CAT_ANCHORS,
                            List.of(
                                    new CheatSheetItem("^", "Start of text (or line if 'm' flag is set)"),
                                    new CheatSheetItem("$", "End of text (or line if 'm' flag is set)"),
                                    new CheatSheetItem("\\A", "Absolute start of text"),
                                    new CheatSheetItem("\\z", "Absolute end of text"),
                                    new CheatSheetItem("\\b", "ASCII word boundary"),
                                    new CheatSheetItem("\\B", "Non-ASCII-word boundary")
                            )
                    ),
                    new CheatSheetCategory(
                            Common.CAT_QUANTIFIERS,
                            List.of(
                                    new CheatSheetItem("*", "0 or more times (greedy)"),
                                    new CheatSheetItem("+", "1 or more times (greedy)"),
                                    new CheatSheetItem("?", "0 or 1 time (greedy)"),
                                    new CheatSheetItem("{m}", "Exactly m times"),
                                    new CheatSheetItem("{m,n}", "Between m and n times (greedy, with repetition bounds up to 1000)"),
                                    new CheatSheetItem("*?", "0 or more times (lazy)"),
                                    new CheatSheetItem("+?", "1 or more times (lazy)"),
                                    new CheatSheetItem("??", "0 or 1 time (lazy)"),
                                    new CheatSheetItem("{m,n}?", "Between m and n times (lazy, with repetition bounds up to 1000)")
                            )
                    ),
                    new CheatSheetCategory(
                            Common.CAT_GROUPS,
                            List.of(
                                    new CheatSheetItem("(...)", "Capturing group"),
                                    new CheatSheetItem("(?:...)", "Non-capturing group"),
                                    new CheatSheetItem("x|y", "Alternation (match x or y)"),
                                    new CheatSheetItem("(?P<name>...)", "Named capturing group"),
                                    new CheatSheetItem("(?<name>...)", "Named capturing group")
                            )
                    ),
                    new CheatSheetCategory(
                            Common.CAT_ADVANCED,
                            List.of(
                                    new CheatSheetItem("(?i)", "Inline flag: Case-insensitive"),
                                    new CheatSheetItem("(?m)", "Inline flag: Multiline"),
                                    new CheatSheetItem("(?s)", "Inline flag: Dot matches newline"),
                                    new CheatSheetItem("(?U)", "Inline flag: Ungreedy quantifiers"),
                                    new CheatSheetItem("(?i:...)", "Scoped inline flag: Case-insensitive"),
                                    new CheatSheetItem("(?-i:...)", "Scoped inline flag: Disable case-insensitive")
                            )
                    )
            ),
            List.of(
                    new EngineExample(
                            "(?P<IP>(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d))(/(\\d{1,2}))?(?:-(?P<IP2>(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)))?(?::(?P<port>\\d{1,5}))?",
                            "This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255\n192.168.1.1-192.168.1.255:80\n192.168.1.0/24:80"
                    )
            )
    );
}
