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

RE2_LIB_VER = get_pkg_version("re2", "libre2-dev", "libre2-9", "libre2-11")

engine = EngineInfo(
    engine_id="cpp_re2",
    engine_language_type="C++",
    engine_language_version=CPP_VERSION,
    engine_regex_lib="re2",
    engine_regex_lib_version=RE2_LIB_VER,
    engine_label="C++ (RE2)",
    engine_capabilities=EngineCapabilities(
        flags=build_engine_flags("i", "m", "s"),
        supports_lookaround=False,
        supports_backrefs=False,
    ),
    engine_docs=EngineDocs(
        trivia=[
            "Designed by Russ Cox at Google specifically to eliminate Regular Expression Denial of Service (ReDoS) vulnerabilities.",
            "RE2 is distributed under the BSD-3-Clause license.",
            "Executes in guaranteed linear time O(n) relative to the length of the input string by utilizing deterministic finite automata (DFA) instead of backtracking.",
            "To maintain this strict mathematical guarantee, RE2 completely abandons backreferences and lookaround assertions.",
            "Allows setting a 'max_mem' budget; if compiling the DFA state machine exceeds this memory limit, it gracefully falls back to an NFA simulation.",
            "RE2 is heavily used as the default engine under the hood in systems like Go's 'regexp' module, Rust's 'regex' crate, and the Envoy proxy.",
            "Supports a subset of PCRE syntax but parses it completely differently to ensure safe execution bounds."
        ],
        cheat_sheet_url="https://github.com/google/re2/wiki/Syntax"
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
                CheatSheetItem(character="\\pN", description="Unicode character class (e.g., N for numbers)")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ANCHORS,
            items=[
                CheatSheetItem(character="^", description="Start of string (or line if 'm' flag is set)"),
                CheatSheetItem(character="$", description="End of string (or line if 'm' flag is set)"),
                CheatSheetItem(character="\\A", description="Absolute start of string (ignores 'm' flag)"),
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
                CheatSheetItem(character="(?P<name>...)", description="Named capturing group (Python/RE2 syntax)")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ADVANCED,
            items=[
                CheatSheetItem(character="(?i) / (?-i)",
                               description="Inline flag: turn case-insensitive matching on / off"),
                CheatSheetItem(character="(?m) / (?-m)", description="Inline flag: turn multi-line matching on / off"),
                CheatSheetItem(character="(?s) / (?-s)", description="Inline flag: turn dot-matches-all on / off")
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
