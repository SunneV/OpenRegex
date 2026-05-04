from openregex_libs.models import EngineInfo, EngineCapabilities, EngineDocs, CheatSheetCategory, CheatSheetItem, EngineExample
from .common import (
    get_pkg_version,
    CAT_CLASSES,
    CAT_ANCHORS,
    CAT_QUANTIFIERS,
    CAT_GROUPS,
    CAT_ADVANCED,
    CPP_VERSION,
    build_engine_flags,
)

BOOST_LIB_VER = get_pkg_version("boost", "libboost-regex-dev", "libboost-dev")

engine = EngineInfo(
    engine_id="cpp_boost",
    engine_language_type="C++",
    engine_language_version=CPP_VERSION,
    engine_regex_lib="boost",
    engine_regex_lib_version=BOOST_LIB_VER,
    engine_label="C++ (Boost.Regex)",
    engine_capabilities=EngineCapabilities(
        flags=build_engine_flags("i", "s", "x"),
        supports_lookaround=True,
        supports_backrefs=True,
    ),
    engine_docs=EngineDocs(
        trivia=[
            "The predecessor to std::regex, developed by John Maddock. The C++11 std::regex was heavily based on this library.",
            "Boost.Regex is distributed under the Boost Software License 1.0 (BSL-1.0).",
            "Often faster and more memory-efficient than many std::regex implementations, depending on the compiler.",
            "Supports Perl-like regular expression syntax (similar to PCRE), but is a distinct engine.",
            "Includes advanced features such as lookbehind assertions and conditionals, though not as extensive as full PCRE engines.",
            "Offers a 'Partial Match' feature, useful for streaming text where a match may complete with more input.",
            "Notepad++ uses the Boost.Regex engine for its regular expression searches."
        ],
        cheat_sheet_url="https://www.boost.org/doc/libs/release/libs/regex/doc/html/boost_regex/syntax/perl_syntax.html"
    ),
    engine_cheat_sheet=[
        CheatSheetCategory(
            category=CAT_CLASSES,
            items=[
                CheatSheetItem(character=".", description="Any character (except newline unless 's' flag is set)"),
                CheatSheetItem(character="\\w", description="Word character (alphanumeric + underscore)"),
                CheatSheetItem(character="\\W", description="Non-word character"),
                CheatSheetItem(character="\\d", description="Decimal digit"),
                CheatSheetItem(character="\\D", description="Non-digit"),
                CheatSheetItem(character="\\s", description="Whitespace character (space, tab, newline)"),
                CheatSheetItem(character="\\S", description="Non-whitespace character"),
                CheatSheetItem(character="[a-z]", description="Character class (inclusive)"),
                CheatSheetItem(character="[^a-z]", description="Negated character class (exclusive)"),
                CheatSheetItem(character="[[:alpha:]]", description="POSIX character class support")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ANCHORS,
            items=[
                CheatSheetItem(character="^", description="Start of string (or line if 'm' flag is set)"),
                CheatSheetItem(character="$", description="End of string (or line if 'm' flag is set)"),
                CheatSheetItem(character="\\A", description="Absolute start of string"),
                CheatSheetItem(character="\\z", description="Absolute end of string"),
                CheatSheetItem(character="\\Z", description="End of string or before final newline"),
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
                CheatSheetItem(character="*+", description="0 or more times (possessive / no backtracking)"),
                CheatSheetItem(character="++", description="1 or more times (possessive / no backtracking)"),
                CheatSheetItem(character="?+", description="0 or 1 time (possessive / no backtracking)")
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
                CheatSheetItem(character="\\k<name>", description="Backreference to a named capture group")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ADVANCED,
            items=[
                CheatSheetItem(character="(?=...)", description="Positive lookahead"),
                CheatSheetItem(character="(?!...)", description="Negative lookahead"),
                CheatSheetItem(character="(?<=...)", description="Positive lookbehind"),
                CheatSheetItem(character="(?<!...)", description="Negative lookbehind"),
                CheatSheetItem(character="(?>...)", description="Atomic grouping (prevents backtracking inside the group)"),
                CheatSheetItem(character="(?i)", description="Inline flag: Case-insensitive"),
                CheatSheetItem(character="(?x)", description="Inline flag: Ignore whitespace"),
                CheatSheetItem(character="\\K", description="Match reset (discards everything matched up to this point)"),
                CheatSheetItem(character="(?(condition)yes|no)", description="Conditional matching")
            ]
        )
    ],
    engine_examples=[
        EngineExample(
            regex=r"(?<IP>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))(/(\d{1,2}))?(?:-(?<IP2>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)))?(:(?<port>\d{1,5}))?",
            text="This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255\n192.168.1.1-192.168.1.255:80\n192.168.1.0/24:80"
        )
    ]
)
