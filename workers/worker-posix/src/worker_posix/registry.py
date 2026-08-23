import os
import re
import subprocess

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

WORKER_NAME = "worker-posix"
WORKER_VERSION = os.environ.get("WORKER_VERSION", "Unknown")
WORKER_RELEASE_DATE = os.environ.get("WORKER_RELEASE_DATE", "Unreleased")

CAT_CLASSES = "Character Classes & Escapes"
CAT_ANCHORS = "Anchors & Boundaries"
CAT_QUANTIFIERS = "Quantifiers"
CAT_GROUPS = "Grouping & Backreferences"
CAT_USAGE = "Command Line Usage"

EXAMPLE_TEXT = (
    "This is an example to get IP:\n\n"
    "192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255"
)


def tool_version(binary: str) -> str:
    """First line of `<tool> --version` carries the GNU release number."""
    try:
        result = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=5)
        first_line = result.stdout.splitlines()[0] if result.stdout else ""
        found = re.search(r"(\d+\.\d+(?:\.\d+)?)", first_line)
        return found.group(1) if found else (first_line.strip() or "system")
    except Exception:
        return "system"


def build_engine_flags(*names: str) -> list[EngineFlag]:
    flags: list[EngineFlag] = []
    for name in names:
        description, group = FLAG_METADATA.get(name, (f"Flag ({name})", "Basic"))
        flags.append(EngineFlag(name=name, description=description, group=group))
    return flags


def _shared_classes() -> CheatSheetCategory:
    return CheatSheetCategory(
        category=CAT_CLASSES,
        items=[
            CheatSheetItem(character=".", description="Any character except newline; input is always processed line by line"),
            CheatSheetItem(character="[a-z]", description="Bracket expression"),
            CheatSheetItem(character="[^a-z]", description="Negated bracket expression"),
            CheatSheetItem(character="[[:alpha:]]", description="POSIX class: letters"),
            CheatSheetItem(character="[[:digit:]]", description="POSIX class: digits"),
            CheatSheetItem(character="[[:alnum:]]", description="POSIX class: letters and digits"),
            CheatSheetItem(character="[[:space:]]", description="POSIX class: whitespace"),
            CheatSheetItem(character="[[:punct:]]", description="POSIX class: punctuation"),
            CheatSheetItem(character="[[:upper:]]", description="POSIX class: upper case letters"),
            CheatSheetItem(character="\\w", description="GNU extension: word character, equivalent to [[:alnum:]_]"),
            CheatSheetItem(character="\\W", description="GNU extension: non-word character"),
            CheatSheetItem(character="\\s", description="GNU extension: whitespace character"),
            CheatSheetItem(character="\\S", description="GNU extension: non-whitespace character"),
        ],
    )


def _anchors(word_escapes: bool) -> CheatSheetCategory:
    items = [
        CheatSheetItem(character="^", description="Start of line"),
        CheatSheetItem(character="$", description="End of line"),
    ]
    if word_escapes:
        items.extend([
            CheatSheetItem(character="\\<", description="GNU extension: start of a word"),
            CheatSheetItem(character="\\>", description="GNU extension: end of a word"),
            CheatSheetItem(character="\\b", description="GNU extension: word boundary"),
            CheatSheetItem(character="\\B", description="GNU extension: non-word boundary"),
        ])
    else:
        items.extend([
            CheatSheetItem(character="\\y", description="gawk: word boundary"),
            CheatSheetItem(character="\\B", description="gawk: non-word boundary"),
            CheatSheetItem(character="\\<", description="gawk: start of a word"),
            CheatSheetItem(character="\\>", description="gawk: end of a word"),
            CheatSheetItem(character="\\`", description="gawk: start of the whole record"),
            CheatSheetItem(character="\\'", description="gawk: end of the whole record"),
        ])
    return CheatSheetCategory(category=CAT_ANCHORS, items=items)


def _bre_quantifiers() -> CheatSheetCategory:
    return CheatSheetCategory(
        category=CAT_QUANTIFIERS,
        items=[
            CheatSheetItem(character="*", description="0 or more times - the only quantifier BRE spells without a backslash"),
            CheatSheetItem(character="\\+", description="1 or more times; a bare + is a literal plus in BRE"),
            CheatSheetItem(character="\\?", description="0 or 1 time; a bare ? is a literal question mark in BRE"),
            CheatSheetItem(character="\\{m\\}", description="Exactly m times"),
            CheatSheetItem(character="\\{m,n\\}", description="Between m and n times"),
            CheatSheetItem(character="\\{m,\\}", description="At least m times"),
        ],
    )


def _ere_quantifiers() -> CheatSheetCategory:
    return CheatSheetCategory(
        category=CAT_QUANTIFIERS,
        items=[
            CheatSheetItem(character="*", description="0 or more times"),
            CheatSheetItem(character="+", description="1 or more times"),
            CheatSheetItem(character="?", description="0 or 1 time"),
            CheatSheetItem(character="{m}", description="Exactly m times"),
            CheatSheetItem(character="{m,n}", description="Between m and n times"),
            CheatSheetItem(character="{m,}", description="At least m times"),
        ],
    )


def _bre_groups() -> CheatSheetCategory:
    return CheatSheetCategory(
        category=CAT_GROUPS,
        items=[
            CheatSheetItem(character="\\(...\\)", description="Capturing group; bare parentheses are literal in BRE"),
            CheatSheetItem(character="\\|", description="GNU extension: alternation; a bare | is a literal pipe in BRE"),
            CheatSheetItem(character="\\1", description="Backreference to capture group 1"),
            CheatSheetItem(character="\\9", description="Backreferences stop at 9 - POSIX defines no more"),
        ],
    )


def _ere_groups(backrefs: bool) -> CheatSheetCategory:
    items = [
        CheatSheetItem(character="(...)", description="Capturing group"),
        CheatSheetItem(character="x|y", description="Alternation (match x or y)"),
    ]
    if backrefs:
        items.append(CheatSheetItem(character="\\1", description="GNU extension: backreference to capture group 1; not part of POSIX ERE"))
    else:
        items.append(CheatSheetItem(character="\\1", description="Not available: awk has no backreferences in patterns"))
    return CheatSheetCategory(category=CAT_GROUPS, items=items)


def _usage(items: list[tuple[str, str]]) -> CheatSheetCategory:
    return CheatSheetCategory(
        category=CAT_USAGE,
        items=[CheatSheetItem(character=character, description=description) for character, description in items],
    )


def _grep(grep_version: str, extended: bool) -> EngineInfo:
    dialect = "ERE" if extended else "BRE"
    return EngineInfo(
        engine_id=f"gnu_grep_{dialect.lower()}",
        engine_language_type="Shell",
        engine_language_version=f"GNU grep {grep_version}",
        engine_regex_lib=f"GNU regex ({dialect})",
        engine_regex_lib_version=grep_version,
        engine_label=f"GNU grep {dialect}" + ("" if extended else " (default)"),
        engine_capabilities=EngineCapabilities(
            flags=build_engine_flags("i", "w", "x"),
            supports_lookaround=False,
            supports_backrefs=not extended,
        ),
        engine_docs=EngineDocs(
            trivia=[
                "grep is line-oriented: a pattern can never match across a newline, no matter what you write.",
                "GNU grep is distributed under GPL-3.0-or-later.",
                f"This engine runs the real binary as `grep -o -b {'-E' if extended else '-G'}`, so what you see is exactly what your shell would print.",
                "BRE and ERE differ only in punctuation: BRE needs \\+, \\?, \\{m,n\\}, \\( and \\| where ERE writes +, ?, {m,n}, ( and |.",
                "POSIX matching is leftmost-longest, so alternation picks the longest branch instead of the first one.",
                "grep -o cannot print capture groups, so OpenRegex reports whole matches only for this engine.",
                "grep -P switches to PCRE entirely; that dialect is covered by the PCRE2 engine in the C/C++ worker.",
            ]
            + (["POSIX ERE has no backreferences; GNU grep supports \\1 anyway as an extension, but the DFA fast path is disabled when you use it."]
               if extended else
               ["Backreferences like \\1 are part of BRE and force grep onto its slower backtracking matcher."]),
            cheat_sheet_url="https://www.gnu.org/software/grep/manual/grep.html",
        ),
        engine_cheat_sheet=[
            _shared_classes(),
            _anchors(word_escapes=True),
            _ere_quantifiers() if extended else _bre_quantifiers(),
            _ere_groups(backrefs=True) if extended else _bre_groups(),
            _usage([
                ("grep -E 'pat' file" if extended else "grep 'pat' file", "Print matching lines"),
                ("grep -o", "Print only the matched parts, one per line"),
                ("grep -b", "Prefix output with the byte offset of the match"),
                ("grep -i", "Case-insensitive matching"),
                ("grep -w", "Match only whole words"),
                ("grep -x", "Match only whole lines"),
                ("grep -v", "Invert: print non-matching lines"),
                ("grep -c", "Count matching lines"),
                ("grep -F", "Treat the pattern as a fixed string, no metacharacters"),
                ("grep -P", "Switch to the PCRE engine instead of POSIX"),
            ]),
        ],
        engine_examples=[
            EngineExample(
                regex=r"([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?" if extended
                else r"\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}\(:[0-9]\{1,5\}\)\?",
                text=EXAMPLE_TEXT,
            )
        ],
    )


def _sed(sed_version: str, extended: bool) -> EngineInfo:
    dialect = "ERE" if extended else "BRE"
    return EngineInfo(
        engine_id=f"gnu_sed_{dialect.lower()}",
        engine_language_type="Shell",
        engine_language_version=f"GNU sed {sed_version}",
        engine_regex_lib=f"GNU regex ({dialect})",
        engine_regex_lib_version=sed_version,
        engine_label=f"GNU sed {dialect}" + ("" if extended else " (default)"),
        engine_capabilities=EngineCapabilities(
            flags=build_engine_flags("i"),
            supports_lookaround=False,
            supports_backrefs=True,
        ),
        engine_docs=EngineDocs(
            trivia=[
                "sed processes one line at a time; the pattern space holds a single line unless you splice lines together with N.",
                "GNU sed is distributed under GPL-3.0-or-later.",
                f"This engine runs `sed {'-E ' if extended else ''}s///g` with the match fenced by two control characters, then recovers the offsets by diffing the result against your subject.",
                "sed itself can never tell you where a match was - substitution is the only observable, which is why this engine reports no capture groups.",
                "In the replacement, & stands for the whole match and \\1..\\9 for capture groups.",
                "GNU sed adds \\U, \\L, \\u, \\l and \\E to change the case of replacement text, which POSIX sed does not have.",
                "-E (or -r) selects ERE. Old scripts often use -r; -E is the portable spelling that BSD sed understands too.",
            ],
            cheat_sheet_url="https://www.gnu.org/software/sed/manual/sed.html",
        ),
        engine_cheat_sheet=[
            _shared_classes(),
            _anchors(word_escapes=True),
            _ere_quantifiers() if extended else _bre_quantifiers(),
            _ere_groups(backrefs=True) if extended else _bre_groups(),
            _usage([
                ("sed -E 's/pat/rep/g'" if extended else "sed 's/pat/rep/g'", "Replace every match on each line"),
                ("sed -n 's/pat/rep/p'", "Print only the lines that changed"),
                ("s/pat/rep/I", "Case-insensitive substitution (GNU extension)"),
                ("s/pat/rep/2", "Replace only the second match on the line"),
                ("&", "The whole match, inside the replacement"),
                ("\\1", "Capture group 1, inside the replacement"),
                ("\\U&", "Upper-case the whole match (GNU extension)"),
                ("s|pat|rep|", "Any character can serve as the delimiter"),
                ("sed -i", "Edit files in place"),
            ]),
        ],
        engine_examples=[
            EngineExample(
                regex=r"([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?" if extended
                else r"\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}\(:[0-9]\{1,5\}\)\?",
                text=EXAMPLE_TEXT,
            )
        ],
    )


def _awk(awk_version: str) -> EngineInfo:
    return EngineInfo(
        engine_id="gnu_awk_ere",
        engine_language_type="Shell",
        engine_language_version=f"GNU awk {awk_version}",
        engine_regex_lib="gawk ERE",
        engine_regex_lib_version=awk_version,
        engine_label="GNU awk ERE",
        engine_capabilities=EngineCapabilities(
            flags=build_engine_flags("i"),
            supports_lookaround=False,
            supports_backrefs=False,
        ),
        engine_docs=EngineDocs(
            trivia=[
                "awk has exactly one dialect: ERE. There is no BRE mode and no backreference support in patterns.",
                "GNU awk is distributed under GPL-3.0-or-later.",
                "gawk's three-argument match(str, re, arr) fills an array with the text, start and length of every capture group - the only tool in this worker that can report groups.",
                "Case-insensitivity is not a pattern flag here but a variable: setting IGNORECASE=1 changes every regexp operation in the program.",
                "Records are lines by default, but RS accepts a regular expression in gawk, which lets one pattern split the input in ways sed and grep cannot.",
                "A string used where a regexp is expected becomes a dynamic regexp, and escape sequences in a string constant are processed twice - the classic source of \\\\\\\\ confusion in awk scripts.",
                "gawk interprets patterns as characters, not bytes, in a UTF-8 locale, so match offsets line up with code points already.",
            ],
            cheat_sheet_url="https://www.gnu.org/software/gawk/manual/gawk.html#Regexp",
        ),
        engine_cheat_sheet=[
            _shared_classes(),
            _anchors(word_escapes=False),
            _ere_quantifiers(),
            _ere_groups(backrefs=False),
            _usage([
                ("awk '/pat/ { print }'", "Print records matching the pattern"),
                ("awk '$0 ~ /pat/'", "Explicit match operator"),
                ("awk '$0 !~ /pat/'", "Negated match operator"),
                ("match(s, re)", "Sets RSTART and RLENGTH for the first match"),
                ("match(s, re, arr)", "gawk: also fills arr with groups and their positions"),
                ("arr[1, \"start\"]", "gawk: 1-based start of capture group 1"),
                ("gsub(re, rep)", "Replace every match in the record"),
                ("sub(re, rep)", "Replace the first match in the record"),
                ("split(s, arr, re)", "Split a string on a regular expression"),
                ("IGNORECASE=1", "gawk: make all regexp operations case-insensitive"),
                ("RS=\"re\"", "gawk: use a regular expression as the record separator"),
            ]),
        ],
        engine_examples=[
            EngineExample(
                regex=r"([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?",
                text=EXAMPLE_TEXT,
            )
        ],
    )


def build_worker_info() -> WorkerInfo:
    grep_version = tool_version("grep")
    sed_version = tool_version("sed")
    awk_version = tool_version("gawk")

    return WorkerInfo(
        worker_name=WORKER_NAME,
        worker_version=WORKER_VERSION,
        worker_release_date=WORKER_RELEASE_DATE,
        worker_schema_version=WORKER_SCHEMA_VERSION,
        engines=[
            _grep(grep_version, extended=False),
            _grep(grep_version, extended=True),
            _sed(sed_version, extended=False),
            _sed(sed_version, extended=True),
            _awk(awk_version),
        ],
    )


def register_engines(redis_client, worker_info: WorkerInfo) -> None:
    redis_client.hset("openregex:workers", worker_info.worker_name, worker_info.model_dump_json())
    print(f"[Worker] Registered '{worker_info.worker_name}' with {len(worker_info.engines)} engines.", flush=True)
