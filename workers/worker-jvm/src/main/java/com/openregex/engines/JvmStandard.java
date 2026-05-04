package com.openregex.engines;

import com.openregex.models.Models.*;
import java.util.List;

public class JvmStandard {
    public static final EngineInfo ENGINE = new EngineInfo(
            "jvm_standard",
            "Java",
            Common.JAVA_VERSION,
            "java.util.regex",
            Common.JAVA_VERSION,
            "Java (java.util.regex)",
            new EngineCapabilities(
                    Common.flags("i", "m", "s", "d", "u", "x", "U"),
                    true,
                    true
            ),
            new EngineDocs(
                    List.of(
                            "Standard NFA-based Java engine built into the JDK.",
                            "In OpenJDK builds, java.util.regex is part of code distributed under GPL-2.0 with the Classpath Exception.",
                            "Supports advanced features like possessive quantifiers and intersection of character classes.",
                            "Lookbehinds in Java must have an obvious maximum length (e.g., variable length is partially supported but unbounded like '*' is not).",
                            "Vulnerable to catastrophic backtracking (ReDoS) on highly nested quantifiers."
                    ),
                    "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/regex/Pattern.html"
            ),
            List.of(
                    new CheatSheetCategory(
                            Common.CAT_CLASSES,
                            List.of(
                                    new CheatSheetItem(".", "Any character (except newline unless 's' flag is set)"),
                                    new CheatSheetItem("\\w", "Word character (ASCII alphanumeric + underscore unless 'U' flag is set)"),
                                    new CheatSheetItem("\\W", "Non-word character"),
                                    new CheatSheetItem("\\d", "Decimal digit (ASCII digit unless 'U' flag is set)"),
                                    new CheatSheetItem("\\D", "Non-digit"),
                                    new CheatSheetItem("\\s", "Whitespace character"),
                                    new CheatSheetItem("\\S", "Non-whitespace character"),
                                    new CheatSheetItem("[a-z]", "Character class (inclusive)"),
                                    new CheatSheetItem("[^a-z]", "Negated character class")
                            )
                    ),
                    new CheatSheetCategory(
                            Common.CAT_ANCHORS,
                            List.of(
                                    new CheatSheetItem("^", "Start of string (or line if 'm' flag is set)"),
                                    new CheatSheetItem("$", "End of string (or line if 'm' flag is set)"),
                                    new CheatSheetItem("\\A", "Absolute start of string"),
                                    new CheatSheetItem("\\z", "Absolute end of string"),
                                    new CheatSheetItem("\\Z", "End of string or before final terminator"),
                                    new CheatSheetItem("\\b", "Word boundary"),
                                    new CheatSheetItem("\\B", "Non-word boundary"),
                                    new CheatSheetItem("\\G", "End of the previous match")
                            )
                    ),
                    new CheatSheetCategory(
                            Common.CAT_QUANTIFIERS,
                            List.of(
                                    new CheatSheetItem("*", "0 or more times (greedy)"),
                                    new CheatSheetItem("+", "1 or more times (greedy)"),
                                    new CheatSheetItem("?", "0 or 1 time (greedy)"),
                                    new CheatSheetItem("{m}", "Exactly m times"),
                                    new CheatSheetItem("{m,n}", "Between m and n times (greedy)"),
                                    new CheatSheetItem("*?", "0 or more times (lazy)"),
                                    new CheatSheetItem("+?", "1 or more times (lazy)"),
                                    new CheatSheetItem("??", "0 or 1 time (lazy)"),
                                    new CheatSheetItem("*+", "0 or more times (possessive)"),
                                    new CheatSheetItem("++", "1 or more times (possessive)"),
                                    new CheatSheetItem("?+", "0 or 1 time (possessive)"),
                                    new CheatSheetItem("{m,n}+", "Between m and n times (possessive)")
                            )
                    ),
                    new CheatSheetCategory(
                            Common.CAT_GROUPS,
                            List.of(
                                    new CheatSheetItem("(...)", "Capturing group"),
                                    new CheatSheetItem("(?:...)", "Non-capturing group"),
                                    new CheatSheetItem("x|y", "Alternation (match x or y)"),
                                    new CheatSheetItem("(?<name>...)", "Named capturing group"),
                                    new CheatSheetItem("\\1", "Backreference to capture group 1"),
                                    new CheatSheetItem("\\k<name>", "Backreference to named group")
                            )
                    ),
                    new CheatSheetCategory(
                            Common.CAT_ADVANCED,
                            List.of(
                                    new CheatSheetItem("(?=...)", "Positive lookahead"),
                                    new CheatSheetItem("(?!...)", "Negative lookahead"),
                                    new CheatSheetItem("(?<=...)", "Positive lookbehind (obvious max length)"),
                                    new CheatSheetItem("(?<!...)", "Negative lookbehind (obvious max length)"),
                                    new CheatSheetItem("(?>...)", "Atomic grouping"),
                                    new CheatSheetItem("(?i)", "Inline flag: Case-insensitive"),
                                    new CheatSheetItem("(?m)", "Inline flag: Multiline"),
                                    new CheatSheetItem("(?s)", "Inline flag: Dotall"),
                                    new CheatSheetItem("(?d)", "Inline flag: Unix lines"),
                                    new CheatSheetItem("(?u)", "Inline flag: Unicode-aware case folding"),
                                    new CheatSheetItem("(?x)", "Inline flag: Comments / free-spacing"),
                                    new CheatSheetItem("(?U)", "Inline flag: Unicode character classes")
                            )
                    )
            ),
            List.of(
                    new EngineExample(
                            "(?<IP>(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d))(/(\\d{1,2}))?(?:-(?<IP2>(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)))?(?::(?<port>\\d{1,5}))?",
                            "This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255\n192.168.1.1-192.168.1.255:80\n192.168.1.0/24:80"
                    )
            )
    );
}
