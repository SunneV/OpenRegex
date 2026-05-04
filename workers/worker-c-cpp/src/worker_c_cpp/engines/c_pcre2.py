from openregex_libs.models import EngineInfo, EngineCapabilities, EngineDocs, CheatSheetCategory, CheatSheetItem, EngineExample
from .common import get_pkg_version, CAT_CLASSES, CAT_ANCHORS, CAT_QUANTIFIERS, \
    CAT_GROUPS, CAT_ADVANCED, C_VERSION, build_engine_flags

PCRE2_LIB_VER = get_pkg_version("libpcre2-8", "pcre2", "libpcre2-dev")

engine = EngineInfo(
    engine_id="c_pcre2",
    engine_language_type="C",
    engine_language_version=C_VERSION,
    engine_regex_lib="pcre2",
    engine_regex_lib_version=PCRE2_LIB_VER,
    engine_label="C (PCRE2)",
    engine_capabilities=EngineCapabilities(
        flags=build_engine_flags("i", "m", "s", "x", "U", "J", "n"),
        supports_lookaround=True,
        supports_backrefs=True
    ),
    engine_docs=EngineDocs(
        trivia=[
            "PCRE2 is the revised API for Perl-Compatible Regular Expressions, widely used across the industry.",
            "PCRE2 is distributed under BSD-3-Clause licensing with the PCRE2 exception.",
            "It replaced the original PCRE library and introduced a more powerful, flexible execution engine.",
            "Supports advanced functionality such as JIT compilation, lookbehind assertions, and atomic groups.",
            "Highly compatible with Perl 5 syntax and serves as the baseline behavior expected by most modern developers."
        ],
        cheat_sheet_url="https://pcre.org/current/doc/html/pcre2syntax.html"
    ),
    engine_cheat_sheet=[
        CheatSheetCategory(
            category=CAT_CLASSES,
            items=[
                CheatSheetItem(character=".", description="Any character except newline (any character if 's' flag is set)"),
                CheatSheetItem(character="\\w", description="Word character (ASCII alphanumeric + underscore by default; Unicode-aware with (*UCP))"),
                CheatSheetItem(character="\\W", description="Non-word character"),
                CheatSheetItem(character="\\d", description="Decimal digit (ASCII by default; Unicode-aware with (*UCP))"),
                CheatSheetItem(character="\\D", description="Non-digit"),
                CheatSheetItem(character="\\s", description="Whitespace character (ASCII by default; Unicode-aware with (*UCP))"),
                CheatSheetItem(character="\\S", description="Non-whitespace character"),
                CheatSheetItem(character="\\R", description="Any line break sequence"),
                CheatSheetItem(character="\\X", description="Extended grapheme cluster"),
                CheatSheetItem(character="[a-z]", description="Character class"),
                CheatSheetItem(character="[^a-z]", description="Negated character class")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ANCHORS,
            items=[
                CheatSheetItem(character="^", description="Start of string (and after internal newlines if 'm' flag is set)"),
                CheatSheetItem(character="$", description="End of string or before a final newline (and before internal newlines if 'm' flag is set)"),
                CheatSheetItem(character="\\A", description="Start of string (ignores 'm' flag)"),
                CheatSheetItem(character="\\Z", description="End of string or before a final newline (ignores 'm' flag)"),
                CheatSheetItem(character="\\z", description="Absolute end of string (ignores 'm' flag)"),
                CheatSheetItem(character="\\b", description="Word boundary"),
                CheatSheetItem(character="\\B", description="Non-word boundary")
            ]
        ),
        CheatSheetCategory(
            category=CAT_QUANTIFIERS,
            items=[
                CheatSheetItem(character="*", description="0 or more times (greedy)"),
                CheatSheetItem(character="+", description="1 or more times (greedy)"),
                CheatSheetItem(character="?", description="0 or 1 time (greedy)"),
                CheatSheetItem(character="{m}", description="Exactly m times"),
                CheatSheetItem(character="{m,n}", description="Between m and n times (greedy)"),
                CheatSheetItem(character="*?", description="0 or more times (lazy)"),
                CheatSheetItem(character="*+", description="0 or more times (possessive)")
            ]
        ),
        CheatSheetCategory(
            category=CAT_GROUPS,
            items=[
                CheatSheetItem(character="(...)", description="Capturing group"),
                CheatSheetItem(character="(?:...)", description="Non-capturing group"),
                CheatSheetItem(character="x|y", description="Alternation (match x or y)"),
                CheatSheetItem(character="(?<name>...)", description="Named capturing group"),
                CheatSheetItem(character="\\1", description="Backreference to capture group 1"),
                CheatSheetItem(character="\\k<name>", description="Backreference to named group")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ADVANCED,
            items=[
                CheatSheetItem(character="(?i)", description="Case-insensitive mode"),
                CheatSheetItem(character="(?m)", description="Multiline mode (^ and $ also match line boundaries)"),
                CheatSheetItem(character="(?s)", description="Dotall mode (. matches newlines)"),
                CheatSheetItem(character="(?x)", description="Extended mode (ignores unescaped whitespace and # comments outside character classes)"),
                CheatSheetItem(character="(?U)", description="Ungreedy mode (quantifiers are lazy by default)"),
                CheatSheetItem(character="(?J)", description="Allow duplicate named capture groups"),
                CheatSheetItem(character="(?n)", description="No auto-capture mode (plain (...) groups do not capture)"),
                CheatSheetItem(character="(?=...)", description="Positive lookahead"),
                CheatSheetItem(character="(?!...)", description="Negative lookahead"),
                CheatSheetItem(character="(?<=...)", description="Positive lookbehind"),
                CheatSheetItem(character="(?<!...)", description="Negative lookbehind"),
                CheatSheetItem(character="(?>...)", description="Atomic grouping"),
                CheatSheetItem(character="\\K", description="Match reset (discards everything matched up to this point)")
            ]
        )
    ],
    engine_examples=[
        EngineExample(
            regex=r"(?<IP>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))(?:/(?<CIDR>3[0-2]|[12]?\d))?(?:-(?<IP2>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)))?(?::(?<port>\d{1,5}))?",
            text="This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1"
        )
    ]
)
