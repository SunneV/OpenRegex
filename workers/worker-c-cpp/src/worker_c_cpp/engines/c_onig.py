from openregex_libs.models import EngineInfo, EngineCapabilities, EngineDocs, CheatSheetCategory, CheatSheetItem, EngineExample
from .common import get_pkg_version, CAT_CLASSES, CAT_ANCHORS, CAT_QUANTIFIERS, CAT_GROUPS, CAT_ADVANCED, C_VERSION, build_engine_flags

ONIG_LIB_VER = get_pkg_version("oniguruma", "onig", "libonig-dev", "libonig5")

engine = EngineInfo(
    engine_id="c_onig",
    engine_language_type="C",
    engine_language_version=C_VERSION,
    engine_regex_lib="oniguruma",
    engine_regex_lib_version=ONIG_LIB_VER,
    engine_label="C (Oniguruma)",
    engine_capabilities=EngineCapabilities(
        flags=build_engine_flags("i", "m", "s", "x"),
        supports_lookaround=True,
        supports_backrefs=True
    ),
    engine_docs=EngineDocs(
        trivia=[
            "The default regular expression engine for Ruby, jq, and the syntax highlighting engines for VS Code and TextMate.",
            "Oniguruma is distributed under the BSD-2-Clause license.",
            "Features advanced multi-encoding support (UTF-8, EUC-JP, Shift_JIS, etc.) natively within the regex execution engine.",
            "Introduced the concept of 'Absent Functions' to match what is explicitly NOT there, avoiding complex negative lookaheads.",
            "Highly flexible capture group mechanics, allowing duplicate names for capture groups and robust subexpression calls (recursion)."
        ],
        cheat_sheet_url="https://github.com/kkos/oniguruma/blob/master/doc/RE"
    ),
    engine_cheat_sheet=[
        CheatSheetCategory(
            category=CAT_CLASSES,
            items=[
                CheatSheetItem(character=".", description="Any character (except newline unless 'm' / singleline flag is set)"),
                CheatSheetItem(character="\\w", description="Word character"),
                CheatSheetItem(character="\\W", description="Non-word character"),
                CheatSheetItem(character="\\d", description="Decimal digit"),
                CheatSheetItem(character="\\D", description="Non-digit"),
                CheatSheetItem(character="\\s", description="Whitespace character"),
                CheatSheetItem(character="\\S", description="Non-whitespace character"),
                CheatSheetItem(character="\\h", description="Hexadecimal digit"),
                CheatSheetItem(character="\\H", description="Non-hexadecimal digit"),
                CheatSheetItem(character="\\p{Property}", description="Unicode property/script class (e.g., \\p{Greek})"),
                CheatSheetItem(character="\\P{Property}", description="Negated Unicode property/script class"),
                CheatSheetItem(character="[a-z]", description="Character class (inclusive)"),
                CheatSheetItem(character="[^a-z]", description="Negated character class (exclusive)")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ANCHORS,
            items=[
                CheatSheetItem(character="^", description="Start of string (or line if multiline flag is set)"),
                CheatSheetItem(character="$", description="End of string (or line if multiline flag is set)"),
                CheatSheetItem(character="\\A", description="Absolute start of string"),
                CheatSheetItem(character="\\Z", description="End of string or before final newline"),
                CheatSheetItem(character="\\z", description="Absolute end of string"),
                CheatSheetItem(character="\\b", description="Word boundary"),
                CheatSheetItem(character="\\B", description="Non-word boundary"),
                CheatSheetItem(character="\\G", description="End of the previous match")
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
                CheatSheetItem(character="+?", description="1 or more times (lazy)"),
                CheatSheetItem(character="??", description="0 or 1 time (lazy)"),
                CheatSheetItem(character="{m,n}?", description="Between m and n times (lazy)"),
                CheatSheetItem(character="*+", description="0 or more times (possessive)"),
                CheatSheetItem(character="++", description="1 or more times (possessive)"),
                CheatSheetItem(character="?+", description="0 or 1 time (possessive)")
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
                CheatSheetItem(character="(?=...)", description="Positive lookahead"),
                CheatSheetItem(character="(?!...)", description="Negative lookahead"),
                CheatSheetItem(character="(?<=...)", description="Positive lookbehind"),
                CheatSheetItem(character="(?<!...)", description="Negative lookbehind"),
                CheatSheetItem(character="(?>...)", description="Atomic grouping"),
                CheatSheetItem(character="(?~...)", description="Absent repeater / absent function"),
                CheatSheetItem(character="\\g<name>", description="Subexpression call (evaluates the named group's pattern recursively)"),
                CheatSheetItem(character="\\g<0>", description="Recursive call to the entire regular expression"),
                CheatSheetItem(character="(?(cond)yes|no)", description="Conditional expression (cond can be a backreference or lookaround)")
            ]
        )
    ],
    engine_examples=[
        EngineExample(
            regex=r"(?<IP>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))",
            text="This is an example to get IP:\n\n192.168.1.100\n127.0.0.1"
        )
    ]
)
