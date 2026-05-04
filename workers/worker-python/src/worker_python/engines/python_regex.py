from openregex_libs.models import EngineInfo, EngineCapabilities, EngineDocs, CheatSheetCategory, CheatSheetItem, EngineExample
from .common import (
    PYTHON_MAJOR_MINOR,
    REGEX_VERSION,
    CAT_CLASSES,
    CAT_ANCHORS,
    CAT_QUANTIFIERS,
    CAT_GROUPS,
    CAT_ADVANCED,
    build_engine_flags,
)

engine = EngineInfo(
    engine_id=f"python{PYTHON_MAJOR_MINOR}_regex",
    engine_language_type="Python",
    engine_language_version=PYTHON_MAJOR_MINOR,
    engine_regex_lib="regex",
    engine_regex_lib_version=REGEX_VERSION,
    engine_label=f"Python {PYTHON_MAJOR_MINOR} (regex PyPI)",
    engine_capabilities=EngineCapabilities(
        flags=build_engine_flags("i", "m", "s", "x", "a", "f", "w", "b", "e", "p", "r"),
        supports_lookaround=True,
        supports_backrefs=True
    ),
    engine_docs=EngineDocs(
        trivia=[
            "Created by Matthew Barnett as a powerful, drop-in alternative to the standard 're' module, aiming to fix its historical limitations.",
            "The regex package is published under Apache-2.0 AND CNRI-Python licensing terms.",
            "Unlike 're', it supports variable-length lookbehinds (e.g., (?<=a+) is perfectly valid here).",
            "Fully supports Unicode properties (like \\p{Sc} for currency symbols), making it vastly superior for internationalization and complex parsing tasks.",
            "It uniquely allows for approximate 'fuzzy' matching, detecting errors in text based on edit distance (insertions, deletions, and substitutions).",
            "Supports a dual API: 'V0' behavior (strictly backwards compatible with the standard 're' module) and 'V1' behavior (enables new standard behaviors).",
            "Provides the \\X escape sequence, which matches a Unicode grapheme cluster (a user-perceived character, regardless of how many combining marks it has)."
        ],
        cheat_sheet_url="https://pypi.org/project/regex/"
    ),
    engine_cheat_sheet=[
        CheatSheetCategory(
            category=CAT_CLASSES,
            items=[
                CheatSheetItem(character=".", description="Any character except a line break unless the 's' flag is set"),
                CheatSheetItem(character="\\w", description="Word character (Unicode alphanumeric + underscore by default; ASCII-only with 'a' flag)"),
                CheatSheetItem(character="\\W", description="Non-word character"),
                CheatSheetItem(character="\\d", description="Decimal digit (Unicode by default; [0-9] with 'a' flag)"),
                CheatSheetItem(character="\\D", description="Non-digit"),
                CheatSheetItem(character="\\s", description="Whitespace character"),
                CheatSheetItem(character="\\S", description="Non-whitespace character"),
                CheatSheetItem(character="[a-z]", description="Character class (inclusive)"),
                CheatSheetItem(character="[^a-z]", description="Negated character class (exclusive)"),
                CheatSheetItem(character="\\p{L}", description="Any kind of letter from any language (Unicode property)"),
                CheatSheetItem(character="\\P{L}", description="Negated Unicode property"),
                CheatSheetItem(character="\\X", description="Match a full Unicode grapheme cluster")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ANCHORS,
            items=[
                CheatSheetItem(character="^", description="Start of string, or start of line if 'm' flag is set"),
                CheatSheetItem(character="$", description="End of string or before a final newline, or end of line if 'm' flag is set"),
                CheatSheetItem(character="\\A", description="Start of string only"),
                CheatSheetItem(character="\\Z", description="End of string only"),
                CheatSheetItem(character="\\G", description="Position where the current search started"),
                CheatSheetItem(character="\\b", description="Word boundary"),
                CheatSheetItem(character="\\B", description="Non-word boundary"),
                CheatSheetItem(character="\\m", description="Start of word"),
                CheatSheetItem(character="\\M", description="End of word")
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
                CheatSheetItem(character="*+", description="0 or more times (possessive / no backtracking)"),
                CheatSheetItem(character="++", description="1 or more times (possessive / no backtracking)"),
                CheatSheetItem(character="?+", description="0 or 1 time (possessive / no backtracking)"),
                CheatSheetItem(character="{m,n}+", description="Between m and n times (possessive / no backtracking)")
            ]
        ),
        CheatSheetCategory(
            category=CAT_GROUPS,
            items=[
                CheatSheetItem(character="(...)", description="Capturing group"),
                CheatSheetItem(character="(?:...)", description="Non-capturing group"),
                CheatSheetItem(character="x|y", description="Alternation (match x or y)"),
                CheatSheetItem(character="(?P<name>...)", description="Named capturing group"),
                CheatSheetItem(character="(?<name>...)", description="Named capturing group"),
                CheatSheetItem(character="\\1", description="Backreference to capture group 1"),
                CheatSheetItem(character="(?P=name)", description="Backreference to a named group"),
                CheatSheetItem(character="\\g<name>", description="Backreference to a named group"),
                CheatSheetItem(character="(?&name)", description="Call a named group subroutine"),
                CheatSheetItem(character="(?1)", description="Call the subroutine for capturing group 1"),
                CheatSheetItem(character="(?R)", description="Recursive call to the entire pattern")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ADVANCED,
            items=[
                CheatSheetItem(character="(?=...)", description="Positive lookahead"),
                CheatSheetItem(character="(?!...)", description="Negative lookahead"),
                CheatSheetItem(character="(?<=...)", description="Positive lookbehind (variable-length supported)"),
                CheatSheetItem(character="(?<!...)", description="Negative lookbehind (variable-length supported)"),
                CheatSheetItem(character="(?>...)", description="Atomic grouping (prevents backtracking inside the group)"),
                CheatSheetItem(character="(?flags-flags:...)", description="Scoped inline flags for a non-capturing group"),
                CheatSheetItem(character="(?a)", description="Inline flag: ASCII character categories for \\w, \\W, \\b, \\B, \\d, and \\D"),
                CheatSheetItem(character="(?b)", description="Inline flag: Best fuzzy match instead of first fuzzy match"),
                CheatSheetItem(character="(?e)", description="Inline flag: Enhance the fit after finding the first fuzzy match"),
                CheatSheetItem(character="(?f)", description="Inline flag: Full Unicode case-folding when case-insensitive matching is active"),
                CheatSheetItem(character="(?i)", description="Inline flag: Case-insensitive matching"),
                CheatSheetItem(character="(?L)", description="Inline flag: Locale-dependent character categories for bytes patterns"),
                CheatSheetItem(character="(?m)", description="Inline flag: Multiline anchors (^ and $ match line boundaries)"),
                CheatSheetItem(character="(?p)", description="Inline flag: POSIX leftmost-longest matching"),
                CheatSheetItem(character="(?r)", description="Inline flag: Reverse search direction"),
                CheatSheetItem(character="(?s)", description="Inline flag: Dot matches line breaks"),
                CheatSheetItem(character="(?u)", description="Inline flag: Unicode character categories"),
                CheatSheetItem(character="(?V0)", description="Inline flag: Version 0 legacy behavior"),
                CheatSheetItem(character="(?V1)", description="Inline flag: Version 1 enhanced behavior"),
                CheatSheetItem(character="(?w)", description="Inline flag: Unicode word boundaries and Unicode line-break handling"),
                CheatSheetItem(character="(?x)", description="Inline flag: Ignore unescaped whitespace and allow comments"),
                CheatSheetItem(character="\\K", description="Match reset (discards everything matched up to this point from the final match)"),
                CheatSheetItem(character="(?|...|...)", description="Branch reset: Capturing groups in alternatives share numbers"),
                CheatSheetItem(character="(?:...){e<=N}", description="Fuzzy matching with up to N total errors"),
                CheatSheetItem(character="(?:...){s<=N}", description="Fuzzy matching with up to N substitutions"),
                CheatSheetItem(character="(?:...){i<=N}", description="Fuzzy matching with up to N insertions"),
                CheatSheetItem(character="(?:...){d<=N}", description="Fuzzy matching with up to N deletions")
            ]
        )
    ],
    engine_examples=[
        EngineExample(
            regex=r"(?P<IP>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))(/(\d{1,2}))?(?:-(?P<IP2>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)))?(:(?P<port>\d{1,5}))?",
            text="This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255\n192.168.1.1-192.168.1.255:80\n192.168.1.0/24:80"
        )
    ]
)
