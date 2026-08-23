import os

from openregex_libs.models import (
    CheatSheetCategory,
    CheatSheetItem,
    EngineCapabilities,
    EngineDocs,
    EngineExample,
    EngineFlag,
    EngineInfo,
    WorkerInfo,
    WORKER_SCHEMA_VERSION,
)

from .engine import FLAG_METADATA

WORKER_NAME = "worker-vim"
WORKER_VERSION = os.environ.get("WORKER_VERSION", "Unknown")
WORKER_RELEASE_DATE = os.environ.get("WORKER_RELEASE_DATE", "Unreleased")

CAT_CLASSES = "Character Classes & Escapes"
CAT_ANCHORS = "Anchors & Boundaries"
CAT_QUANTIFIERS = "Quantifiers"
CAT_GROUPS = "Grouping & Backreferences"
CAT_ADVANCED = "Magic Levels & Advanced"


def build_engine_flags(*names: str) -> list[EngineFlag]:
    flags: list[EngineFlag] = []
    for name in names:
        description, group = FLAG_METADATA.get(name, (f"Flag ({name})", "Basic"))
        flags.append(EngineFlag(name=name, description=description, group=group))
    return flags


def build_engine(vim_version: str) -> EngineInfo:
    return EngineInfo(
        engine_id="vim_standard",
        engine_language_type="Vim",
        engine_language_version=vim_version,
        engine_regex_lib="Vim pattern engine",
        engine_regex_lib_version=vim_version,
        engine_label=f"Vim {vim_version} (pattern)",
        engine_capabilities=EngineCapabilities(
            flags=build_engine_flags("i", "I", "v", "m", "M", "V"),
            supports_lookaround=True,
            supports_backrefs=True,
        ),
        engine_docs=EngineDocs(
            trivia=[
                "Vim's pattern syntax is its own dialect, born long before PCRE and shaped by the needs of a line editor rather than a programming language.",
                "Vim is distributed under the Vim License, a charityware license compatible with GPL-2.0.",
                "The 'magic' option decides how much punctuation is special. \\v (very magic) is closest to what every other engine calls normal, \\V (very nomagic) makes everything literal.",
                "Non-greedy is spelled \\{-} here, not *? - and it is the only engine in OpenRegex that spells it that way.",
                "\\zs and \\ze move the reported start and end of the match, which is how Vim does lookaround without lookaround.",
                "Patterns are buffer-oriented: ^ and $ are line anchors, \\%^ and \\%$ anchor to the whole file, and \\n matches a real line break.",
                "By default Vim has two engines: an NFA backtracker and an older backtracking engine, selectable with the 'regexpengine' option.",
                "Vim's script API can report where a match begins and ends but not where its groups are, so OpenRegex reports whole matches only for this engine.",
            ],
            cheat_sheet_url="https://vimhelp.org/pattern.txt.html",
        ),
        engine_cheat_sheet=[
            CheatSheetCategory(
                category=CAT_CLASSES,
                items=[
                    CheatSheetItem(character=".", description="Any character except a line break"),
                    CheatSheetItem(character="\\_.", description="Any character, line breaks included"),
                    CheatSheetItem(character="\\d", description="Digit [0-9]"),
                    CheatSheetItem(character="\\D", description="Non-digit"),
                    CheatSheetItem(character="\\w", description="Word character [0-9A-Za-z_]"),
                    CheatSheetItem(character="\\W", description="Non-word character"),
                    CheatSheetItem(character="\\s", description="Whitespace: space or tab only"),
                    CheatSheetItem(character="\\S", description="Non-whitespace"),
                    CheatSheetItem(character="\\a", description="Alphabetic character"),
                    CheatSheetItem(character="\\l", description="Lower case letter"),
                    CheatSheetItem(character="\\u", description="Upper case letter"),
                    CheatSheetItem(character="\\x", description="Hexadecimal digit"),
                    CheatSheetItem(character="\\_s", description="Whitespace or a line break"),
                    CheatSheetItem(character="[[:alpha:]]", description="POSIX character class inside a collection"),
                    CheatSheetItem(character="\\%d65", description="Character by decimal code point"),
                ],
            ),
            CheatSheetCategory(
                category=CAT_ANCHORS,
                items=[
                    CheatSheetItem(character="^", description="Start of line; only special at the start of the pattern"),
                    CheatSheetItem(character="$", description="End of line; only special at the end of the pattern"),
                    CheatSheetItem(character="\\%^", description="Start of the file"),
                    CheatSheetItem(character="\\%$", description="End of the file"),
                    CheatSheetItem(character="\\<", description="Start of a word"),
                    CheatSheetItem(character="\\>", description="End of a word"),
                    CheatSheetItem(character="\\zs", description="Set where the reported match starts"),
                    CheatSheetItem(character="\\ze", description="Set where the reported match ends"),
                    CheatSheetItem(character="\\%23l", description="Only in line 23"),
                    CheatSheetItem(character="\\%>23c", description="Only after column 23"),
                    CheatSheetItem(character="\\%V", description="Only inside the Visual selection"),
                ],
            ),
            CheatSheetCategory(
                category=CAT_QUANTIFIERS,
                items=[
                    CheatSheetItem(character="*", description="0 or more times, greedy"),
                    CheatSheetItem(character="\\+", description="1 or more times, greedy (bare + under \\v)"),
                    CheatSheetItem(character="\\=", description="0 or 1 time (also spelled \\?)"),
                    CheatSheetItem(character="\\{n,m}", description="Between n and m times, greedy"),
                    CheatSheetItem(character="\\{-}", description="0 or more times, non-greedy"),
                    CheatSheetItem(character="\\{-n,m}", description="Between n and m times, non-greedy"),
                    CheatSheetItem(character="\\{-1,}", description="1 or more times, non-greedy"),
                ],
            ),
            CheatSheetCategory(
                category=CAT_GROUPS,
                items=[
                    CheatSheetItem(character="\\(...\\)", description="Capturing group (bare parentheses under \\v)"),
                    CheatSheetItem(character="\\%(...\\)", description="Non-capturing group"),
                    CheatSheetItem(character="\\|", description="Alternation; the leftmost alternative wins"),
                    CheatSheetItem(character="\\1", description="Backreference to capture group 1"),
                    CheatSheetItem(character="\\9", description="Backreferences stop at 9"),
                    CheatSheetItem(character="~", description="Matches the last substituted string"),
                ],
            ),
            CheatSheetCategory(
                category=CAT_ADVANCED,
                items=[
                    CheatSheetItem(character="\\v", description="Very magic: ( ) | + ? { } are special without a backslash"),
                    CheatSheetItem(character="\\m", description="Magic: Vim's default level"),
                    CheatSheetItem(character="\\M", description="Nomagic: only ^ and $ stay special"),
                    CheatSheetItem(character="\\V", description="Very nomagic: only the backslash stays special"),
                    CheatSheetItem(character="\\c", description="Case-insensitive, wherever it appears in the pattern"),
                    CheatSheetItem(character="\\C", description="Case-sensitive, wherever it appears in the pattern"),
                    CheatSheetItem(character="\\@=", description="Positive lookahead, written after the group"),
                    CheatSheetItem(character="\\@!", description="Negative lookahead, written after the group"),
                    CheatSheetItem(character="\\@<=", description="Positive lookbehind, written after the group"),
                    CheatSheetItem(character="\\@<!", description="Negative lookbehind, written after the group"),
                    CheatSheetItem(character="\\@>", description="Atomic group, written after the group"),
                    CheatSheetItem(character="\\%[abc]", description="Optional sequence: matches a, ab or abc"),
                ],
            ),
        ],
        engine_examples=[
            EngineExample(
                regex=r"\v(\d{1,3}\.){3}\d{1,3}(:\d{1,5})?",
                text="This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255",
            )
        ],
    )


def build_worker_info(vim_version: str) -> WorkerInfo:
    return WorkerInfo(
        worker_name=WORKER_NAME,
        worker_version=WORKER_VERSION,
        worker_release_date=WORKER_RELEASE_DATE,
        worker_schema_version=WORKER_SCHEMA_VERSION,
        engines=[build_engine(vim_version)],
    )


def register_engines(redis_client, worker_info: WorkerInfo) -> None:
    redis_client.hset("openregex:workers", worker_info.worker_name, worker_info.model_dump_json())
    print(f"[Worker] Registered '{worker_info.worker_name}' with {len(worker_info.engines)} engines.", flush=True)
