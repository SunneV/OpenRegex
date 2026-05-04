from openregex_libs.models import EngineInfo, EngineCapabilities, EngineDocs, CheatSheetCategory, CheatSheetItem, \
    EngineExample
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

_std_lib_raw = get_pkg_version("libstdc++6", "libstdc++-dev")
STD_LIB_VER = f"libstdc++ {_std_lib_raw}" if _std_lib_raw != "system" else "system"

engine = EngineInfo(
    engine_id="cpp_std",
    engine_language_type="C++",
    engine_language_version=CPP_VERSION,
    engine_regex_lib="std::regex",
    engine_regex_lib_version=STD_LIB_VER,
    engine_label="C++ (std::regex)",
    engine_capabilities=EngineCapabilities(
        flags=build_engine_flags("i"),
        supports_lookaround=True,
        supports_backrefs=True,
    ),
    engine_docs=EngineDocs(
        trivia=[
            "Standardized in C++11 (originally appearing in TR1), commonly implemented as a backtracking NFA.",
            "The std::regex implementation license follows the active C++ standard library build (for example, GNU libstdc++ uses GPLv3 with the GCC Runtime Library Exception).",
            "Supports 6 different grammar flavors: ECMAScript, basic, extended, awk, grep, and egrep.",
            "ECMAScript is the default grammar. However, it's strictly based on the ES3 specification, meaning it totally lacks modern regex features like lookbehinds.",
            "Implementation performance varies wildly depending on the compiler (GCC, Clang, and MSVC all have vastly different optimizations).",
            "Due to its backtracking architecture, it is susceptible to ReDoS attacks and can easily freeze a server on deeply nested quantifiers.",
            "Generally considered the slowest of the major C++ regex libraries; Boost.Regex or RE2 are usually preferred for heavy workloads."
        ],
        cheat_sheet_url="https://en.cppreference.com/w/cpp/regex/ecmascript"
    ),
    engine_cheat_sheet=[
        CheatSheetCategory(
            category=CAT_CLASSES,
            items=[
                CheatSheetItem(character=".", description="Any character (except newline)"),
                CheatSheetItem(character="\\w", description="Word character (alphanumeric + underscore)"),
                CheatSheetItem(character="\\W", description="Non-word character"),
                CheatSheetItem(character="\\d", description="Decimal digit"),
                CheatSheetItem(character="\\D", description="Non-digit"),
                CheatSheetItem(character="\\s", description="Whitespace character (space, tab, newline)"),
                CheatSheetItem(character="\\S", description="Non-whitespace character"),
                CheatSheetItem(character="[a-z]", description="Character class (inclusive)"),
                CheatSheetItem(character="[^a-z]", description="Negated character class (exclusive)")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ANCHORS,
            items=[
                CheatSheetItem(character="^", description="Start of string"),
                CheatSheetItem(character="$", description="End of string"),
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
                CheatSheetItem(character="+?", description="1 or more times (lazy)"),
                CheatSheetItem(character="??", description="0 or 1 time (lazy)"),
                CheatSheetItem(character="{m,n}?", description="Between m and n times (lazy)")
            ]
        ),
        CheatSheetCategory(
            category=CAT_GROUPS,
            items=[
                CheatSheetItem(character="(...)", description="Capturing group"),
                CheatSheetItem(character="(?:...)", description="Non-capturing group"),
                CheatSheetItem(character="x|y", description="Alternation (match x or y)"),
                CheatSheetItem(character="\\1", description="Backreference to capture group 1")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ADVANCED,
            items=[
                CheatSheetItem(character="(?=...)", description="Positive lookahead"),
                CheatSheetItem(character="(?!...)", description="Negative lookahead")
            ]
        )
    ],
    engine_examples=[
        EngineExample(
            regex=r"((?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))(/(\d{1,2}))?(?:-((?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)))?(:(\d{1,5}))?",
            text="This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255\n192.168.1.1-192.168.1.255:80\n192.168.1.0/24:80"
        )
    ]
)
