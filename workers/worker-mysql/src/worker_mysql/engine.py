"""Executes patterns on a live MySQL server (ICU regex engine).

MySQL 8.0 replaced the old Spencer engine with ICU, which is the same library
behind Swift's NSRegularExpression and Java's ICU4J. The SQL surface exposes
match positions through REGEXP_INSTR but has no way to ask for capture-group
positions, so this engine reports whole matches only.
"""

import os
import threading

import pymysql
from openregex_libs.models import MatchItem, MatchRequest
from openregex_libs.runtime import MAX_MATCHES, TIMEOUT_MS

MYSQL_HOST = os.environ.get("MYSQL_HOST", "mysql")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "openregex")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "openregex")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "openregex")

# ICU aborts a match once it burns through this many steps; it is the closest
# thing MySQL has to a backtrack limit, and the default of 32 is far too tight
# for anything but trivial patterns.
REGEXP_TIME_LIMIT = int(os.environ.get("MYSQL_REGEXP_TIME_LIMIT", 200000))

FLAG_METADATA: dict[str, tuple[str, str]] = {
    "c": ("Case-sensitive matching.", "Basic"),
    "i": ("Case-insensitive matching.", "Basic"),
    "m": ("Multi-line mode. Makes ^ and $ match at line boundaries.", "Basic"),
    "n": ("Makes . match newline as well.", "Basic"),
    "u": ("Unix-only line endings: only newline is recognised as a line terminator.", "Unique"),
}

_local = threading.local()

_MATCH_SQL = """
WITH RECURSIVE occurrences (n, match_start, match_end) AS (
    SELECT 1,
           REGEXP_INSTR(%(subject)s, %(pattern)s, 1, 1, 0, %(match_type)s),
           REGEXP_INSTR(%(subject)s, %(pattern)s, 1, 1, 1, %(match_type)s)
    UNION ALL
    SELECT n + 1,
           REGEXP_INSTR(%(subject)s, %(pattern)s, 1, n + 1, 0, %(match_type)s),
           REGEXP_INSTR(%(subject)s, %(pattern)s, 1, n + 1, 1, %(match_type)s)
    FROM occurrences
    WHERE match_start > 0 AND n <= %(limit)s
)
SELECT n, match_start, match_end
FROM occurrences
WHERE match_start > 0
ORDER BY n
"""


def connect() -> pymysql.connections.Connection:
    """Thread-local connection; the runtime dispatches tasks across a thread pool."""
    connection = getattr(_local, "connection", None)
    if connection is not None:
        try:
            connection.ping(reconnect=True)
            return connection
        except Exception:
            connection = None

    connection = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset="utf8mb4",
        autocommit=True,
    )
    with connection.cursor() as cursor:
        # The server default collation is accent- and case-insensitive, which
        # would silently make every pattern case-insensitive.
        cursor.execute("SET NAMES utf8mb4 COLLATE utf8mb4_0900_as_cs")
        # regexp_time_limit only exists as a global, so the compose file passes
        # --regexp-time-limit to the server. Raising it from here as well keeps
        # a stand-alone server usable, but needs SUPER and is optional.
        try:
            cursor.execute("SET GLOBAL regexp_time_limit = %s", (REGEXP_TIME_LIMIT,))
        except pymysql.MySQLError:
            pass
        # Wall-clock SLA for every read-only statement in this session.
        cursor.execute("SET SESSION max_execution_time = %s", (TIMEOUT_MS,))
        cursor.execute("SET SESSION cte_max_recursion_depth = %s", (MAX_MATCHES + 2,))
    _local.connection = connection
    return connection


def server_version() -> str:
    with connect().cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        return str(cursor.fetchone()[0])


def build_match_type(flags: list[str]) -> str:
    resolved = ""
    for flag in flags:
        flag = flag.strip()
        if not flag:
            continue
        if flag not in FLAG_METADATA:
            raise ValueError(f"Unsupported flag '{flag}' for the MySQL engine")
        resolved += flag
    return resolved


def execute(req: MatchRequest) -> list[MatchItem]:
    match_type = build_match_type(req.flags)
    connection = connect()

    try:
        with connection.cursor() as cursor:
            cursor.execute(_MATCH_SQL, {
                "subject": req.text,
                "pattern": req.regex,
                "match_type": match_type,
                "limit": MAX_MATCHES,
            })
            rows = cursor.fetchall()
    except pymysql.err.OperationalError as exc:
        code = exc.args[0] if exc.args else 0
        # 1317 = query interrupted, 3024 = statement execution timeout,
        # 3699 = ICU step budget (regexp_time_limit) exhausted.
        if code in (1317, 3024, 3699):
            raise ValueError(
                f"TIMEOUT: {req.engine_id} execution exceeded {TIMEOUT_MS}ms SLA."
            ) from exc
        raise ValueError(str(exc.args[-1]).strip()) from exc
    except pymysql.err.MySQLError as exc:
        raise ValueError(str(exc.args[-1]).strip()) from exc

    if len(rows) > MAX_MATCHES:
        raise ValueError(f"Exceeded maximum allowed matches ({MAX_MATCHES}).")

    matches: list[MatchItem] = []
    for index, (_, start, end) in enumerate(rows):
        start -= 1
        end -= 1
        matches.append(MatchItem(
            match_id=index,
            full_match=req.text[start:end],
            start=start,
            end=end,
            groups=[],
        ))
    return matches
