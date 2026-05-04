from openregex_libs.models import EngineInfo, EngineCapabilities, EngineDocs, CheatSheetCategory, CheatSheetItem, EngineExample
from .common import (
    get_pkg_version,
    CAT_CLASSES,
    CAT_ANCHORS,
    CAT_QUANTIFIERS,
    CPP_VERSION,
    build_engine_flags,
)

HS_LIB_VER = get_pkg_version("libhs", "libhs-dev")

engine = EngineInfo(
    engine_id="cpp_hyperscan",
    engine_language_type="C++",
    engine_language_version=CPP_VERSION,
    engine_regex_lib="hyperscan",
    engine_regex_lib_version=HS_LIB_VER,
    engine_label="C++ (Hyperscan)",
    engine_capabilities=EngineCapabilities(
        flags=build_engine_flags("i", "m", "s", "u", "e", "v", "b", "w"),
        supports_lookaround=False,
        supports_backrefs=False
    ),
    engine_docs=EngineDocs(
        trivia=[
            "High-performance multiple regex matching library developed by Intel.",
            "Hyperscan is distributed under a BSD-3-Clause license.",
            "Executes using automata-based algorithms designed for deep packet inspection and network scanning.",
            "Hyperscan does not support sub-capturing groups or backreferences. It only returns the overall match boundaries.",
            "Operates in block mode by default but supports streaming and vectored modes (not exposed here).",
            "Strictly operates in $O(n)$ time complexity, ensuring absolute immunity to ReDoS attacks."
        ],
        cheat_sheet_url="https://intel.github.io/hyperscan/dev-reference/compilation.html#semantics"
    ),
    engine_cheat_sheet=[
        CheatSheetCategory(
            category=CAT_CLASSES,
            items=[
                CheatSheetItem(character=".", description="Any character (except newline unless 's' flag is set)"),
                CheatSheetItem(character="\\w", description="Word character"),
                CheatSheetItem(character="\\d", description="Decimal digit"),
                CheatSheetItem(character="\\s", description="Whitespace character"),
                CheatSheetItem(character="[a-z]", description="Character class (inclusive)"),
                CheatSheetItem(character="[^a-z]", description="Negated character class (exclusive)")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ANCHORS,
            items=[
                CheatSheetItem(character="^", description="Start of string (or line if 'm' flag is set)"),
                CheatSheetItem(character="$", description="End of string (or line if 'm' flag is set)"),
                CheatSheetItem(character="\\A", description="Absolute start of string"),
                CheatSheetItem(character="\\z", description="Absolute end of string"),
                CheatSheetItem(character="\\b", description="Word boundary")
            ]
        ),
        CheatSheetCategory(
            category=CAT_QUANTIFIERS,
            items=[
                CheatSheetItem(character="*", description="0 or more times (greedy)"),
                CheatSheetItem(character="+", description="1 or more times (greedy)"),
                CheatSheetItem(character="?", description="0 or 1 time (greedy)"),
                CheatSheetItem(character="{m}", description="Exactly m times"),
                CheatSheetItem(character="{m,n}", description="Between m and n times (greedy)")
            ]
        ),
        CheatSheetCategory(
            category="Composites",
            items=[
                CheatSheetItem(character="x|y", description="Alternation (match x or y)")
            ]
        )
    ],
    engine_examples=[
        EngineExample(
            regex=r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)",
            text="This is an example to get IP:\n\n192.168.1.100\n10.0.0.1"
        )
    ]
)
