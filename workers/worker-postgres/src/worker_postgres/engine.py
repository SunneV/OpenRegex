"""Executes patterns on a live PostgreSQL server (Spencer ARE engine).

There is no way to embed Postgres' regex engine in-process, so the worker talks
to a real server. Offsets come straight from regexp_instr(), which reports
1-based *character* positions - the platform contract wants 0-based Unicode code
point indices, so the only conversion needed is the -1 shift.
"""

import os
import threading

import psycopg
from openregex_libs.models import MatchGroup, MatchItem, MatchRequest
from openregex_libs.pattern import count_capture_groups
from openregex_libs.runtime import MAX_GROUPS, MAX_MATCHES, TIMEOUT_MS

POSTGRES_DSN = os.environ.get(
    "POSTGRES_DSN", "postgresql://openregex:openregex@postgres:5432/openregex"
)

# Flags accepted by the regexp_* functions. 'g' is deliberately excluded: it is
# only meaningful for regexp_replace/regexp_matches and rejected here.
FLAG_METADATA: dict[str, tuple[str, str]] = {
    "i": ("Case-insensitive matching.", "Basic"),
    "c": ("Case-sensitive matching (the default).", "Basic"),
    "n": ("Newline-sensitive matching: . and negated classes stop at newlines, ^/$ match at them.", "Advance"),
    "m": ("Historical synonym for 'n'.", "Unique"),
    "s": ("Non-newline-sensitive matching (the default).", "Basic"),
    "p": ("Partially newline-sensitive: . stops at newlines, but ^/$ do not match at them.", "Unique"),
    "w": ("Inverse partially newline-sensitive: ^/$ match at newlines, but . does not stop.", "Unique"),
    "x": ("Expanded syntax: whitespace and # comments are ignored.", "Basic"),
    "t": ("Tight syntax (the default): whitespace inside the pattern is significant.", "Advance"),
    "q": ("Literal: the whole pattern is a plain string, no metacharacters.", "Unique"),
    "b": ("Rest of the pattern is a POSIX Basic Regular Expression.", "Unique"),
    "e": ("Rest of the pattern is a POSIX Extended Regular Expression.", "Unique"),
}

_local = threading.local()

_MATCH_SQL = """
SELECT g.i AS match_index,
       k.k AS subexpr,
       regexp_instr(%(subject)s, %(pattern)s, 1, g.i, 0, %(flags)s, k.k) AS match_start,
       regexp_instr(%(subject)s, %(pattern)s, 1, g.i, 1, %(flags)s, k.k) AS match_end
FROM generate_series(1, %(total)s) AS g(i),
     generate_series(0, %(groups)s) AS k(k)
ORDER BY g.i, k.k
"""


def connect() -> psycopg.Connection:
    """Thread-local connection; the runtime dispatches tasks across a thread pool."""
    connection = getattr(_local, "connection", None)
    if connection is None or connection.closed:
        connection = psycopg.connect(POSTGRES_DSN, autocommit=True)
        with connection.cursor() as cursor:
            # The server-side statement timeout is this engine's ReDoS guard.
            cursor.execute("SELECT set_config('statement_timeout', %s, false)", (str(TIMEOUT_MS),))
        _local.connection = connection
    return connection


def server_version() -> str:
    with connect().cursor() as cursor:
        cursor.execute("SHOW server_version")
        return str(cursor.fetchone()[0])


def build_flags(flags: list[str]) -> str:
    resolved = ""
    for flag in flags:
        flag = flag.strip()
        if not flag:
            continue
        if flag not in FLAG_METADATA:
            raise ValueError(f"Unsupported flag '{flag}' for the PostgreSQL engine")
        resolved += flag
    return resolved


def _collect(rows, subject: str) -> list[MatchItem]:
    matches: dict[int, MatchItem] = {}

    for match_index, subexpr, start, end in rows:
        # regexp_instr reports 0 for a group that did not participate.
        if not start:
            continue
        start -= 1
        end -= 1

        if subexpr == 0:
            matches[match_index] = MatchItem(
                match_id=match_index - 1,
                full_match=subject[start:end],
                start=start,
                end=end,
                groups=[],
            )
            continue

        item = matches.get(match_index)
        if item is None:
            continue
        if len(item.groups) >= MAX_GROUPS:
            raise ValueError(f"Exceeded maximum allowed groups per match ({MAX_GROUPS}).")
        item.groups.append(MatchGroup(
            group_id=subexpr,
            name=None,
            content=subject[start:end],
            start=start,
            end=end,
        ))

    return [matches[key] for key in sorted(matches)]


def _run(connection: psycopg.Connection, req: MatchRequest, flags: str, groups: int) -> list[MatchItem]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT regexp_count(%(subject)s, %(pattern)s, 1, %(flags)s)",
            {"subject": req.text, "pattern": req.regex, "flags": flags},
        )
        total = cursor.fetchone()[0] or 0
        if total > MAX_MATCHES:
            raise ValueError(f"Exceeded maximum allowed matches ({MAX_MATCHES}).")
        if total == 0:
            return []

        cursor.execute(_MATCH_SQL, {
            "subject": req.text,
            "pattern": req.regex,
            "flags": flags,
            "total": total,
            "groups": groups,
        })
        return _collect(cursor.fetchall(), req.text)


def execute(req: MatchRequest) -> list[MatchItem]:
    flags = build_flags(req.flags)
    declared_groups = min(count_capture_groups(req.regex), MAX_GROUPS)
    connection = connect()

    # The group count is derived from the pattern text; if the server disagrees
    # (an exotic construct the scanner miscounted), fall back to whole matches
    # rather than failing the request outright.
    for groups in (declared_groups, 0):
        try:
            return _run(connection, req, flags, groups)
        except psycopg.errors.QueryCanceled as exc:
            raise ValueError(
                f"TIMEOUT: {req.engine_id} execution exceeded {TIMEOUT_MS}ms SLA."
            ) from exc
        except psycopg.Error as exc:
            if groups == 0 or "subexpr" not in str(exc):
                raise ValueError(str(exc).strip()) from exc

    return []
