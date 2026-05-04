from openregex_libs.models import EngineInfo, EngineCapabilities, EngineDocs, CheatSheetCategory, CheatSheetItem, EngineExample
from .common import get_pkg_version, CAT_CLASSES, CAT_ANCHORS, CAT_QUANTIFIERS, \
    CAT_GROUPS, C_VERSION, build_engine_flags

LIBC_VER = get_pkg_version("libc6", "libc-dev")

engine = EngineInfo(
    engine_id="c_posix",
    engine_language_type="C",
    engine_language_version=C_VERSION,
    engine_regex_lib="regex.h",
    engine_regex_lib_version=LIBC_VER,
    engine_label="C (POSIX regex.h)",
    engine_capabilities=EngineCapabilities(
        flags=build_engine_flags("i", "m"),
        supports_lookaround=False,
        supports_backrefs=True,
    ),
    engine_docs=EngineDocs(
        trivia=[
            "Native C POSIX Regular Expression library built into the standard C library (libc/glibc).",
            "Licensing follows the host C library build (for example, glibc is LGPL-2.1-or-later).",
            "Executes using the standard regcomp/regexec functions under the hood.",
            "OpenRegex strictly uses the REG_EXTENDED flag to enable modern POSIX Extended Regular Expressions (ERE) over basic ones.",
            "Lacks many modern PCRE features like lookarounds, non-capturing groups, and specific character class escapes like \\d or \\w.",
            "Standard POSIX ERE formally does NOT support backreferences (\\1). However, GNU libc provides them as a non-standard extension."
        ],
        cheat_sheet_url="https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap09.html"
    ),
    engine_cheat_sheet=[
        CheatSheetCategory(
            category=CAT_CLASSES,
            items=[
                CheatSheetItem(character=".", description="Any character except NUL; with m/REG_NEWLINE enabled, any character except newline"),
                CheatSheetItem(character="[a-z]", description="Character class (inclusive)"),
                CheatSheetItem(character="[^a-z]", description="Negated character class (exclusive); with m/REG_NEWLINE enabled, does not match newline unless newline is explicitly included"),
                CheatSheetItem(character="[[:alnum:]]", description="POSIX class: alphanumeric characters"),
                CheatSheetItem(character="[[:digit:]]", description="POSIX class: digits"),
                CheatSheetItem(character="[[:space:]]", description="POSIX class: whitespace")
            ]
        ),
        CheatSheetCategory(
            category=CAT_ANCHORS,
            items=[
                CheatSheetItem(character="^", description="Start of string; with m/REG_NEWLINE enabled, also start of line after newline"),
                CheatSheetItem(character="$", description="End of string; with m/REG_NEWLINE enabled, also end of line before newline")
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
            category=CAT_GROUPS,
            items=[
                CheatSheetItem(character="(...)", description="Capturing group"),
                CheatSheetItem(character="x|y", description="Alternation (match x or y)"),
                CheatSheetItem(character="\\1", description="Backreference to capture group 1 (GNU libc extension; not portable POSIX ERE)", engine_cheat=True)
            ]
        )
    ],
    engine_examples=[
        EngineExample(
            regex=r"([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})",
            text="This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1"
        )
    ]
)
