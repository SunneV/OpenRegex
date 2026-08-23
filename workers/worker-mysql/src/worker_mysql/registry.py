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

WORKER_NAME = "worker-mysql"
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
    major_minor = ".".join(server_version.split(".")[:2])
    return EngineInfo(
        engine_id="mysql_icu",
        engine_language_type="SQL",
        engine_language_version=server_version,
        engine_regex_lib="ICU",
        engine_regex_lib_version=f"bundled with MySQL {server_version}",
        engine_label=f"MySQL {major_minor} (ICU)",
        engine_capabilities=EngineCapabilities(
            flags=build_engine_flags("c", "i", "m", "n", "u"),
            supports_lookaround=True,
            supports_backrefs=True,
        ),
        engine_docs=EngineDocs(
            trivia=[
                "MySQL 8.0 threw out the old Spencer engine and switched to ICU, so patterns written for MySQL 5.7 can behave differently on 8.0.",
                "MySQL is distributed under GPL-2.0 with the FOSS License Exception; ICU ships under the Unicode License.",
                "ICU regex is the same engine family behind Swift's NSRegularExpression and Java's ICU4J, so results here are a good proxy for those.",
                "MariaDB is NOT a drop-in twin here: it kept PCRE2 instead of moving to ICU, so the two forks disagree on syntax and semantics.",
                "The SQL surface exposes match positions (REGEXP_INSTR) but no capture-group positions, so this engine reports whole matches only.",
                "regexp_time_limit caps ICU's internal step count. Its default of 32 is so tight that even moderate patterns fail; this worker raises it and adds a wall-clock SLA on top.",
                "Case sensitivity follows the collation, not the pattern: with the default utf8mb4_0900_ai_ci everything matches case-insensitively. This worker forces an accent- and case-sensitive collation so the flags mean what they say.",
            ],
            cheat_sheet_url="https://dev.mysql.com/doc/refman/8.4/en/regexp.html",
        ),
        engine_cheat_sheet=[
            CheatSheetCategory(
                category=CAT_CLASSES,
                items=[
                    CheatSheetItem(character=".", description="Any character except newline unless the 'n' flag is set"),
                    CheatSheetItem(character="\\w", description="Word character (SQL string literals need the backslash doubled)"),
                    CheatSheetItem(character="\\W", description="Non-word character"),
                    CheatSheetItem(character="\\d", description="Decimal digit"),
                    CheatSheetItem(character="\\D", description="Non-digit"),
                    CheatSheetItem(character="\\s", description="Whitespace character"),
                    CheatSheetItem(character="\\S", description="Non-whitespace character"),
                    CheatSheetItem(character="\\p{L}", description="Unicode property class"),
                    CheatSheetItem(character="\\X", description="Extended grapheme cluster"),
                    CheatSheetItem(character="[[:alpha:]]", description="POSIX character class"),
                    CheatSheetItem(character="[a-z]", description="Character range"),
                    CheatSheetItem(character="[^a-z]", description="Negated character class"),
                    CheatSheetItem(character="[\\p{L}&&[^\\p{Lu}]]", description="Character class intersection (ICU set syntax)"),
                ],
            ),
            CheatSheetCategory(
                category=CAT_ANCHORS,
                items=[
                    CheatSheetItem(character="^", description="Start of string, or start of line under the 'm' flag"),
                    CheatSheetItem(character="$", description="End of string, or end of line under the 'm' flag"),
                    CheatSheetItem(character="\\A", description="Start of input"),
                    CheatSheetItem(character="\\z", description="End of input"),
                    CheatSheetItem(character="\\Z", description="End of input, ignoring a final line terminator"),
                    CheatSheetItem(character="\\b", description="Word boundary"),
                    CheatSheetItem(character="\\B", description="Non-word boundary"),
                    CheatSheetItem(character="\\G", description="Where the previous match ended"),
                ],
            ),
            CheatSheetCategory(
                category=CAT_QUANTIFIERS,
                items=[
                    CheatSheetItem(character="*", description="0 or more times, greedy"),
                    CheatSheetItem(character="+", description="1 or more times, greedy"),
                    CheatSheetItem(character="?", description="0 or 1 time, greedy"),
                    CheatSheetItem(character="{m,n}", description="Between m and n times, greedy"),
                    CheatSheetItem(character="*?", description="0 or more times, lazy"),
                    CheatSheetItem(character="+?", description="1 or more times, lazy"),
                    CheatSheetItem(character="*+", description="0 or more times, possessive"),
                    CheatSheetItem(character="++", description="1 or more times, possessive"),
                    CheatSheetItem(character="?+", description="0 or 1 time, possessive"),
                ],
            ),
            CheatSheetCategory(
                category=CAT_GROUPS,
                items=[
                    CheatSheetItem(character="(...)", description="Capturing group; MySQL cannot report its position"),
                    CheatSheetItem(character="(?:...)", description="Non-capturing group"),
                    CheatSheetItem(character="x|y", description="Alternation (match x or y)"),
                    CheatSheetItem(character="\\1", description="Backreference to capture group 1"),
                    CheatSheetItem(character="$1", description="Group reference inside a REGEXP_REPLACE replacement"),
                ],
            ),
            CheatSheetCategory(
                category=CAT_ADVANCED,
                items=[
                    CheatSheetItem(character="(?=...)", description="Positive lookahead"),
                    CheatSheetItem(character="(?!...)", description="Negative lookahead"),
                    CheatSheetItem(character="(?<=...)", description="Positive lookbehind"),
                    CheatSheetItem(character="(?<!...)", description="Negative lookbehind"),
                    CheatSheetItem(character="(?>...)", description="Atomic group"),
                    CheatSheetItem(character="(?i)", description="Inline flag: case-insensitive"),
                    CheatSheetItem(character="(?s)", description="Inline flag: dot matches newline"),
                    CheatSheetItem(character="(?m)", description="Inline flag: multi-line anchors"),
                    CheatSheetItem(character="(?x)", description="Inline flag: free-spacing"),
                    CheatSheetItem(character="(?i:...)", description="Scoped inline flag group"),
                ],
            ),
            CheatSheetCategory(
                category=CAT_SQL,
                items=[
                    CheatSheetItem(character="expr REGEXP pat", description="Boolean match operator"),
                    CheatSheetItem(character="expr RLIKE pat", description="Synonym for REGEXP"),
                    CheatSheetItem(character="REGEXP_LIKE(s, p, mt)", description="Boolean match test with an explicit match type"),
                    CheatSheetItem(character="REGEXP_INSTR(s, p, pos, occ, ret, mt)", description="1-based position of a match"),
                    CheatSheetItem(character="REGEXP_SUBSTR(s, p, pos, occ, mt)", description="Text of the occ-th match"),
                    CheatSheetItem(character="REGEXP_REPLACE(s, p, r, pos, occ, mt)", description="Replace matches; $1 refers to a group"),
                    CheatSheetItem(character="SET regexp_time_limit", description="ICU step budget guarding against runaway patterns"),
                    CheatSheetItem(character="SET regexp_stack_limit", description="Memory budget for the ICU match stack"),
                ],
            ),
        ],
        engine_examples=[
            EngineExample(
                regex=r"(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}(?::[0-9]{1,5})?",
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
