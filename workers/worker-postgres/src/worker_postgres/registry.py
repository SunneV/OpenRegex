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

WORKER_NAME = "worker-postgres"
WORKER_VERSION = os.environ.get("WORKER_VERSION", "Unknown")
WORKER_RELEASE_DATE = os.environ.get("WORKER_RELEASE_DATE", "Unreleased")

CAT_CLASSES = "Character Classes & Escapes"
CAT_ANCHORS = "Anchors & Boundaries"
CAT_QUANTIFIERS = "Quantifiers"
CAT_GROUPS = "Grouping & Backreferences"
CAT_ADVANCED = "Lookarounds & Advanced"
CAT_SQL = "SQL Surface"


def build_engine_flags(*names: str) -> list[EngineFlag]:
    flags: list[EngineFlag] = []
    for name in names:
        description, group = FLAG_METADATA.get(name, (f"Flag ({name})", "Basic"))
        flags.append(EngineFlag(name=name, description=description, group=group))
    return flags


def build_engine(server_version: str) -> EngineInfo:
    major = server_version.split(".")[0]
    return EngineInfo(
        engine_id="postgres_spencer",
        engine_language_type="SQL",
        engine_language_version=server_version,
        engine_regex_lib="Spencer ARE",
        engine_regex_lib_version=server_version,
        engine_label=f"PostgreSQL {major} (Spencer ARE)",
        engine_capabilities=EngineCapabilities(
            flags=build_engine_flags("i", "c", "n", "m", "s", "p", "w", "x", "t", "q", "b", "e"),
            supports_lookaround=True,
            supports_backrefs=True,
        ),
        engine_docs=EngineDocs(
            trivia=[
                "PostgreSQL uses Henry Spencer's Advanced Regular Expression package, the same lineage as Tcl's regex engine - not PCRE.",
                "PostgreSQL is distributed under the PostgreSQL License, a permissive BSD/MIT-style license.",
                "The engine is a hybrid: it runs a DFA to find the match extent and only falls back to backtracking when capture groups or backreferences are involved.",
                "Matching is leftmost-longest by default, so 'a|ab' matches 'ab' - the opposite of the Perl family's leftmost-first rule.",
                "A single pattern can switch dialects mid-flight: the b and e flags reinterpret the rest as POSIX BRE or ERE.",
                "The x flag has an explicit opposite here, t (tight syntax), which most engines do not offer.",
                "This worker runs each pattern with statement_timeout as its ReDoS guard; there is no in-engine backtrack limit.",
                "regexp_instr, regexp_count, regexp_like and regexp_substr arrived in PostgreSQL 15, largely for Oracle compatibility.",
            ],
            cheat_sheet_url="https://www.postgresql.org/docs/current/functions-matching.html",
        ),
        engine_cheat_sheet=[
            CheatSheetCategory(
                category=CAT_CLASSES,
                items=[
                    CheatSheetItem(character=".", description="Any character; stops at newline only under the n, p or w flag"),
                    CheatSheetItem(character="\\w", description="Word character (alphanumeric plus underscore)"),
                    CheatSheetItem(character="\\W", description="Non-word character"),
                    CheatSheetItem(character="\\d", description="Decimal digit"),
                    CheatSheetItem(character="\\D", description="Non-digit"),
                    CheatSheetItem(character="\\s", description="Whitespace character"),
                    CheatSheetItem(character="\\S", description="Non-whitespace character"),
                    CheatSheetItem(character="[[:alpha:]]", description="POSIX character class inside a bracket expression"),
                    CheatSheetItem(character="[[:<:]]", description="Start-of-word constraint, an ARE speciality"),
                    CheatSheetItem(character="[[:>:]]", description="End-of-word constraint, an ARE speciality"),
                    CheatSheetItem(character="[a-z]", description="Character range"),
                    CheatSheetItem(character="[^a-z]", description="Negated bracket expression"),
                    CheatSheetItem(character="\\uHHHH", description="Unicode code point escape"),
                ],
            ),
            CheatSheetCategory(
                category=CAT_ANCHORS,
                items=[
                    CheatSheetItem(character="^", description="Start of string, or start of line under the n or w flag"),
                    CheatSheetItem(character="$", description="End of string, or end of line under the n or w flag"),
                    CheatSheetItem(character="\\A", description="Start of string, always"),
                    CheatSheetItem(character="\\Z", description="End of string, always"),
                    CheatSheetItem(character="\\m", description="Start of a word"),
                    CheatSheetItem(character="\\M", description="End of a word"),
                    CheatSheetItem(character="\\y", description="Word boundary"),
                    CheatSheetItem(character="\\Y", description="Non-word boundary"),
                ],
            ),
            CheatSheetCategory(
                category=CAT_QUANTIFIERS,
                items=[
                    CheatSheetItem(character="*", description="0 or more times, greedy"),
                    CheatSheetItem(character="+", description="1 or more times, greedy"),
                    CheatSheetItem(character="?", description="0 or 1 time, greedy"),
                    CheatSheetItem(character="{m,n}", description="Between m and n times, greedy"),
                    CheatSheetItem(character="*?", description="0 or more times, non-greedy"),
                    CheatSheetItem(character="+?", description="1 or more times, non-greedy"),
                    CheatSheetItem(character="??", description="0 or 1 time, non-greedy"),
                    CheatSheetItem(character="{m,n}?", description="Between m and n times, non-greedy"),
                ],
            ),
            CheatSheetCategory(
                category=CAT_GROUPS,
                items=[
                    CheatSheetItem(character="(...)", description="Capturing group"),
                    CheatSheetItem(character="(?:...)", description="Non-capturing group"),
                    CheatSheetItem(character="x|y", description="Alternation; the longest overall match wins"),
                    CheatSheetItem(character="\\1", description="Backreference to capture group 1"),
                    CheatSheetItem(character="(?#...)", description="Inline comment"),
                ],
            ),
            CheatSheetCategory(
                category=CAT_ADVANCED,
                items=[
                    CheatSheetItem(character="(?=...)", description="Positive lookahead"),
                    CheatSheetItem(character="(?!...)", description="Negative lookahead"),
                    CheatSheetItem(character="(?<=...)", description="Positive lookbehind (9.5+)"),
                    CheatSheetItem(character="(?<!...)", description="Negative lookbehind (9.5+)"),
                    CheatSheetItem(character="(?i)", description="Inline flag: case-insensitive"),
                    CheatSheetItem(character="(?n)", description="Inline flag: newline-sensitive matching"),
                    CheatSheetItem(character="(?x)", description="Inline flag: expanded syntax"),
                    CheatSheetItem(character="***:", description="Director prefix forcing ARE interpretation"),
                    CheatSheetItem(character="***=", description="Director prefix: treat the rest as a literal string"),
                ],
            ),
            CheatSheetCategory(
                category=CAT_SQL,
                items=[
                    CheatSheetItem(character="text ~ 'pat'", description="Case-sensitive match operator"),
                    CheatSheetItem(character="text ~* 'pat'", description="Case-insensitive match operator"),
                    CheatSheetItem(character="text !~ 'pat'", description="Negated match operator"),
                    CheatSheetItem(character="regexp_like(s, p, f)", description="Boolean match test (15+)"),
                    CheatSheetItem(character="regexp_count(s, p, 1, f)", description="Number of matches (15+)"),
                    CheatSheetItem(character="regexp_instr(s, p, 1, n, 0, f, k)", description="1-based position of the n-th match or its k-th group (15+)"),
                    CheatSheetItem(character="regexp_substr(s, p, 1, n, f, k)", description="Text of the n-th match or its k-th group (15+)"),
                    CheatSheetItem(character="regexp_replace(s, p, r, 'g')", description="Replace matches; \\1 refers to a group"),
                    CheatSheetItem(character="regexp_matches(s, p, 'g')", description="Set of capture-group arrays"),
                    CheatSheetItem(character="substring(s from 'p')", description="SQL-standard extraction of the first match"),
                ],
            ),
        ],
        engine_examples=[
            EngineExample(
                regex=r"((?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))(?:/([0-9]{1,2}))?(?::([0-9]{1,5}))?",
                text="This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255",
            )
        ],
    )


def build_worker_info(server_version: str) -> WorkerInfo:
    return WorkerInfo(
        worker_name=WORKER_NAME,
        worker_version=WORKER_VERSION,
        worker_release_date=WORKER_RELEASE_DATE,
        worker_schema_version=WORKER_SCHEMA_VERSION,
        engines=[build_engine(server_version)],
    )


def register_engines(redis_client, worker_info: WorkerInfo) -> None:
    redis_client.hset("openregex:workers", worker_info.worker_name, worker_info.model_dump_json())
    print(f"[Worker] Registered '{worker_info.worker_name}' with {len(worker_info.engines)} engines.", flush=True)
