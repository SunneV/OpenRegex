from openregex_libs.models import EngineInfo, EngineCapabilities, EngineDocs, CheatSheetCategory, CheatSheetItem, EngineExample
from .common import get_pkg_version, CAT_CLASSES, CAT_GROUPS, CAT_ADVANCED, C_VERSION, build_engine_flags

ONIG_LIB_VER = get_pkg_version("oniguruma", "onig", "libonig-dev", "libonig5")

engine = EngineInfo(
    engine_id="c_onig",
    engine_language_type="C",
    engine_language_version=C_VERSION,
    engine_regex_lib="oniguruma",
    engine_regex_lib_version=ONIG_LIB_VER,
    engine_label="C (Oniguruma)",
    engine_capabilities=EngineCapabilities(
        flags=build_engine_flags("i", "m", "x"),
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
                CheatSheetItem(character=".", description="Any character (except newline unless 'm' flag is set)"),
                CheatSheetItem(character="\\w", description="Word character"),
                CheatSheetItem(character="\\d", description="Decimal digit"),
                CheatSheetItem(character="\\p{Property}", description="Unicode property/script class (e.g., \\p{Greek})")
            ]
        ),
        CheatSheetCategory(
            category=CAT_GROUPS,
            items=[
                CheatSheetItem(character="(...)", description="Capturing group"),
                CheatSheetItem(character="(?<name>...)", description="Named capturing group"),
                CheatSheetItem(character="\\k<name>", description="Backreference to named group")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ADVANCED,
            items=[
                CheatSheetItem(character="(?=...)", description="Positive lookahead"),
                CheatSheetItem(character="(?!...)", description="Negative lookahead"),
                CheatSheetItem(character="(?<=...)", description="Positive lookbehind (fixed-width pattern only)"),
                CheatSheetItem(character="(?<!...)", description="Negative lookbehind (fixed-width pattern only)"),
                CheatSheetItem(character="(?~...)", description="Absent repeater / absent function"),
                CheatSheetItem(character="\\g<name>", description="Subexpression call (evaluates the named group's pattern recursively)")
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
