from openregex_libs.models import EngineInfo, EngineCapabilities, EngineDocs, CheatSheetCategory, CheatSheetItem, EngineExample
from .common import (
    PYTHON_MAJOR_MINOR,
    CAT_CLASSES,
    CAT_ANCHORS,
    CAT_QUANTIFIERS,
    CAT_GROUPS,
    CAT_ADVANCED,
    build_engine_flags,
)

engine = EngineInfo(
    engine_id=f"python{PYTHON_MAJOR_MINOR}_re",
    engine_language_type="Python",
    engine_language_version=PYTHON_MAJOR_MINOR,
    engine_regex_lib="re",
    engine_regex_lib_version=PYTHON_MAJOR_MINOR,
    engine_label=f"Python {PYTHON_MAJOR_MINOR} (re module)",
    engine_capabilities=EngineCapabilities(
        flags=build_engine_flags("a", "i", "m", "s", "u", "x"),
        supports_lookaround=True,
        supports_backrefs=True),
    engine_docs=EngineDocs(
        trivia=[
            "It has been the standard regular expression module built into Python since version 1.5, replacing the older, deprecated 'regex' module.",
            "The Python standard library is distributed under the Python Software Foundation License (PSF).",
            "Uses a backtracking NFA (Non-deterministic Finite Automaton) engine, making it highly susceptible to ReDoS (Regular Expression Denial of Service) if patterns are not carefully constructed.",
            "Compiled regex patterns are cached internally to save on recompilation overhead.",
            "Python 3.11 added support for atomic grouping and possessive quantifiers: (?>...), *+, ++, ?+, and {m,n}+.",
            "A strict limitation of 're' is that lookbehinds (?<=...) and (?<!...) must be fixed-width. You cannot use variable-width quantifiers like * or + inside them.",
            "It includes a hidden gem: passing the 're.DEBUG' flag will print the internal compiled parse tree of your regex, which is invaluable for debugging complex patterns."
        ],
        cheat_sheet_url="https://docs.python.org/3/library/re.html"
    ),
    engine_cheat_sheet=[
        CheatSheetCategory(
            category=CAT_CLASSES,
            items=[
                CheatSheetItem(character=".", description="Any character except newline unless the 's' flag is set"),
                CheatSheetItem(character="\\w", description="Word character; Unicode by default for string patterns, ASCII-only if the 'a' flag is set"),
                CheatSheetItem(character="\\W", description="Non-word character; Unicode by default for string patterns, ASCII-only if the 'a' flag is set"),
                CheatSheetItem(character="\\d", description="Decimal digit; Unicode by default for string patterns, ASCII-only if the 'a' flag is set"),
                CheatSheetItem(character="\\D", description="Non-digit character; Unicode by default for string patterns, ASCII-only if the 'a' flag is set"),
                CheatSheetItem(character="\\s", description="Whitespace character; Unicode by default for string patterns, ASCII-only if the 'a' flag is set"),
                CheatSheetItem(character="\\S", description="Non-whitespace character; Unicode by default for string patterns, ASCII-only if the 'a' flag is set"),
                CheatSheetItem(character="[a-z]", description="Character class"),
                CheatSheetItem(character="[^a-z]", description="Negated character class"),
                CheatSheetItem(character="\\xHH", description="Hexadecimal character escape"),
                CheatSheetItem(character="\\uHHHH", description="Unicode character escape")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ANCHORS,
            items=[
                CheatSheetItem(character="^", description="Start of string, or start of line if the 'm' flag is set"),
                CheatSheetItem(character="$", description="End of string or before a trailing newline, and also before a newline at the end of a line if the 'm' flag is set"),
                CheatSheetItem(character="\\A", description="Absolute start of string; unaffected by the 'm' flag"),
                CheatSheetItem(character="\\Z", description="Absolute end of string; unaffected by the 'm' flag"),
                CheatSheetItem(character="\\b", description="Word boundary"),
                CheatSheetItem(character="\\B", description="Non-word boundary")
            ]
        ),
        CheatSheetCategory(
            category=CAT_QUANTIFIERS,
            items=[
                CheatSheetItem(character="*", description="0 or more times, greedy"),
                CheatSheetItem(character="+", description="1 or more times, greedy"),
                CheatSheetItem(character="?", description="0 or 1 time, greedy"),
                CheatSheetItem(character="{m}", description="Exactly m times"),
                CheatSheetItem(character="{m,n}", description="Between m and n times, greedy"),
                CheatSheetItem(character="*?", description="0 or more times, lazy"),
                CheatSheetItem(character="+?", description="1 or more times, lazy"),
                CheatSheetItem(character="??", description="0 or 1 time, lazy"),
                CheatSheetItem(character="{m,n}?", description="Between m and n times, lazy"),
                CheatSheetItem(character="*+", description="0 or more times, possessive; Python 3.11+"),
                CheatSheetItem(character="++", description="1 or more times, possessive; Python 3.11+"),
                CheatSheetItem(character="?+", description="0 or 1 time, possessive; Python 3.11+"),
                CheatSheetItem(character="{m,n}+", description="Between m and n times, possessive; Python 3.11+")
            ]
        ),
        CheatSheetCategory(
            category=CAT_GROUPS,
            items=[
                CheatSheetItem(character="(...)", description="Capturing group"),
                CheatSheetItem(character="(?:...)", description="Non-capturing group"),
                CheatSheetItem(character="x|y", description="Alternation (match x or y)"),
                CheatSheetItem(character="(?P<name>...)", description="Named capturing group"),
                CheatSheetItem(character="\\1", description="Backreference to capture group 1"),
                CheatSheetItem(character="(?P=name)", description="Backreference to a named group")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ADVANCED,
            items=[
                CheatSheetItem(character="(?=...)", description="Positive lookahead"),
                CheatSheetItem(character="(?!...)", description="Negative lookahead"),
                CheatSheetItem(character="(?<=...)", description="Positive lookbehind; must be fixed-width in 're'"),
                CheatSheetItem(character="(?<!...)", description="Negative lookbehind; must be fixed-width in 're'"),
                CheatSheetItem(character="(?>...)", description="Atomic grouping; prevents backtracking; Python 3.11+"),
                CheatSheetItem(character="(?a)", description="Inline flag: ASCII-only matching for \\w, \\W, \\b, \\B, \\d, \\D, \\s, and \\S in string patterns"),
                CheatSheetItem(character="(?i)", description="Inline flag: case-insensitive matching"),
                CheatSheetItem(character="(?m)", description="Inline flag: multiline mode; ^ and $ also match line boundaries"),
                CheatSheetItem(character="(?s)", description="Inline flag: dotall mode; . matches newline"),
                CheatSheetItem(character="(?u)", description="Inline flag: Unicode matching; redundant for string patterns in Python 3"),
                CheatSheetItem(character="(?x)", description="Inline flag: verbose mode; ignore unescaped whitespace and allow comments")
            ]
        )
    ],
    engine_examples=[
        EngineExample(
            regex=r"(?P<IP>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))(/(\d{1,2}))?(?:-(?P<IP2>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)))?(?::(?P<port>\d{1,5}))?",
            text="This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255\n192.168.1.1-192.168.1.255:80\n192.168.1.0/24:80"
        )
    ]
)
