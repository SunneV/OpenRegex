"""Drives the GNU userland regex tools: grep, sed and awk.

These are the engines every shell user actually argues about - why `\\+` is a
quantifier in grep but a literal plus in `grep -E`, why sed needs `\\(` for a
group, why awk has no BRE mode at all. None of them has a library binding, so
each request shells out to the real binary and the offsets are reconstructed
from what the tool prints.

Reporting rules per tool:
* grep -o -b prints the byte offset and text of every match, but has no way to
  report capture groups, so groups come back empty.
* sed cannot report positions at all, so the match is wrapped in two sentinel
  control characters and the offsets are recovered by diffing the output
  against the subject. Groups are likewise unavailable.
* gawk's three-argument match() fills an array with per-group start and length
  in characters, so this is the only tool here with full group support.

All three are line-based: a pattern can never match across a newline.
"""

import os
import subprocess
from array import array
from itertools import accumulate

from openregex_libs.models import MatchGroup, MatchItem, MatchRequest
from openregex_libs.pattern import count_capture_groups
from openregex_libs.runtime import MAX_GROUPS, MAX_MATCHES, TIMEOUT_MS

TIMEOUT_S = TIMEOUT_MS / 1000.0

# Sentinels used to fence sed matches; control characters that no sane subject
# contains, and the request is rejected outright when it does.
SED_OPEN = "\x01"
SED_CLOSE = "\x02"

TOOL_ENV = {**os.environ, "LC_ALL": "C.UTF-8", "LANG": "C.UTF-8"}

FLAG_METADATA: dict[str, tuple[str, str]] = {
    "i": ("Case-insensitive matching (-i in grep and sed, IGNORECASE in awk).", "Basic"),
    "w": ("Match only whole words (grep -w).", "Unique"),
    "x": ("Match only whole lines (grep -x).", "Unique"),
}

GREP_FLAGS = {"i": "-i", "w": "-w", "x": "-x"}

# gawk builds every match position in characters, so nothing needs converting.
AWK_PROGRAM = r"""
BEGIN { offset = 0; pattern = ENVIRON["OPENREGEX_PATTERN"] }
{
    line = $0
    start = 1
    while (start <= length(line) + 1) {
        rest = substr(line, start)
        if (! match(rest, pattern, groups)) break

        base = offset + start - 2
        printf "%d %d", base + RSTART, base + RSTART + RLENGTH
        for (g = 1; g <= ngroups; g++) {
            if ((g, "start") in groups && groups[g, "start"] > 0)
                printf " %d %d", base + groups[g, "start"], base + groups[g, "start"] + groups[g, "length"]
            else
                printf " -1 -1"
        }
        printf "\n"

        start = start + RSTART - 1 + (RLENGTH > 0 ? RLENGTH : 1)
    }
    offset += length(line) + 1
}
"""

_UTF8_START_TABLE = bytes(0 if 0x80 <= b < 0xC0 else 1 for b in range(256))


def _byte_to_char_map(text: str):
    """Prefix map converting UTF-8 byte offsets to code point indices.

    Returns None for pure-ASCII text, where the two already coincide.
    """
    if text.isascii():
        return None
    starts = text.encode("utf-8").translate(_UTF8_START_TABLE)
    return array("I", accumulate(starts, initial=0))


def _run(command: list[str], subject: bytes, engine_id: str, extra_env: dict | None = None):
    env = TOOL_ENV if extra_env is None else {**TOOL_ENV, **extra_env}
    try:
        return subprocess.run(
            command,
            input=subject,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT_S,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError(f"TIMEOUT: {engine_id} execution exceeded {TIMEOUT_MS}ms SLA.") from exc
    except FileNotFoundError as exc:
        raise ValueError(f"Engine binary missing from the worker image: {command[0]}") from exc


def _tool_error(result, fallback: str) -> str:
    message = result.stderr.decode("utf-8", "replace").strip()
    return message or fallback


def _split_flags(flags: list[str], supported: set[str], engine_name: str) -> list[str]:
    resolved = []
    for flag in flags:
        flag = flag.strip()
        if not flag:
            continue
        if flag not in supported:
            raise ValueError(f"Unsupported flag '{flag}' for the {engine_name} engine")
        resolved.append(flag)
    return resolved


# --- grep -----------------------------------------------------------------

def _run_grep(req: MatchRequest, extended: bool) -> list[MatchItem]:
    flags = _split_flags(req.flags, set(GREP_FLAGS), "grep")
    command = ["grep", "-o", "-b", "-a", "-E" if extended else "-G"]
    command.extend(GREP_FLAGS[flag] for flag in flags)
    command.extend(["-e", req.regex])

    result = _run(command, req.text.encode("utf-8"), req.engine_id)
    if result.returncode == 1:
        return []
    if result.returncode != 0:
        raise ValueError(_tool_error(result, "grep failed to execute the pattern."))

    b2c = _byte_to_char_map(req.text)
    last = (len(b2c) - 1) if b2c is not None else 0

    def to_char(byte_index: int) -> int:
        return byte_index if b2c is None else b2c[min(byte_index, last)]

    matches: list[MatchItem] = []
    for line in result.stdout.split(b"\n"):
        if not line:
            continue
        offset_bytes, _, matched = line.partition(b":")
        if not offset_bytes.isdigit():
            continue
        if len(matches) >= MAX_MATCHES:
            raise ValueError(f"Exceeded maximum allowed matches ({MAX_MATCHES}).")

        byte_start = int(offset_bytes)
        start = to_char(byte_start)
        end = to_char(byte_start + len(matched))
        matches.append(MatchItem(
            match_id=len(matches),
            full_match=req.text[start:end],
            start=start,
            end=end,
            groups=[],
        ))
    return matches


# --- sed ------------------------------------------------------------------

def _run_sed(req: MatchRequest, extended: bool) -> list[MatchItem]:
    flags = _split_flags(req.flags, {"i"}, "sed")

    if SED_OPEN in req.text or SED_CLOSE in req.text:
        raise ValueError("Subject contains the U+0001/U+0002 control characters this engine uses to fence matches.")
    if "\x1f" in req.regex:
        raise ValueError("Pattern contains U+001F, which this engine uses as the s/// delimiter.")

    modifiers = "g" + ("I" if "i" in flags else "")
    script = f"s\x1f{req.regex}\x1f{SED_OPEN}&{SED_CLOSE}\x1f{modifiers}"

    command = ["sed"]
    if extended:
        command.append("-E")
    command.extend(["-e", script])

    result = _run(command, req.text.encode("utf-8"), req.engine_id)
    if result.returncode != 0:
        raise ValueError(_tool_error(result, "sed failed to execute the pattern."))

    marked = result.stdout.decode("utf-8", "replace")

    clean_parts: list[str] = []
    matches: list[MatchItem] = []
    position = 0
    open_at = None

    for chunk in marked:
        if chunk == SED_OPEN:
            open_at = position
            continue
        if chunk == SED_CLOSE:
            if open_at is None:
                continue
            if len(matches) >= MAX_MATCHES:
                raise ValueError(f"Exceeded maximum allowed matches ({MAX_MATCHES}).")
            matches.append(MatchItem(
                match_id=len(matches),
                full_match="".join(clean_parts[open_at:position]),
                start=open_at,
                end=position,
                groups=[],
            ))
            open_at = None
            continue
        clean_parts.append(chunk)
        position += 1

    clean = "".join(clean_parts)
    # sed always terminates the last line, even when the subject did not.
    if clean != req.text and clean == req.text + "\n":
        clean = req.text
    if clean != req.text:
        raise ValueError("sed output could not be aligned with the subject; offsets would be unreliable.")

    return matches


# --- awk ------------------------------------------------------------------

def _run_awk(req: MatchRequest) -> list[MatchItem]:
    flags = _split_flags(req.flags, {"i"}, "awk")
    groups = min(count_capture_groups(req.regex), MAX_GROUPS)

    command = ["gawk", "-v", f"ngroups={groups}"]
    if "i" in flags:
        command.extend(["-v", "IGNORECASE=1"])
    command.extend(["--", AWK_PROGRAM])

    result = _run(command, req.text.encode("utf-8"), req.engine_id,
                  extra_env={"OPENREGEX_PATTERN": req.regex})
    if result.returncode != 0:
        raise ValueError(_tool_error(result, "gawk failed to execute the pattern."))

    matches: list[MatchItem] = []
    for line in result.stdout.decode("utf-8", "replace").splitlines():
        if not line:
            continue
        if len(matches) >= MAX_MATCHES:
            raise ValueError(f"Exceeded maximum allowed matches ({MAX_MATCHES}).")

        numbers = [int(value) for value in line.split()]
        start, end = numbers[0], numbers[1]

        match_groups: list[MatchGroup] = []
        for index, offset in enumerate(range(2, len(numbers) - 1, 2), start=1):
            group_start, group_end = numbers[offset], numbers[offset + 1]
            if group_start < 0:
                continue
            match_groups.append(MatchGroup(
                group_id=index,
                name=None,
                content=req.text[group_start:group_end],
                start=group_start,
                end=group_end,
            ))

        matches.append(MatchItem(
            match_id=len(matches),
            full_match=req.text[start:end],
            start=start,
            end=end,
            groups=match_groups,
        ))
    return matches


ENGINES = {
    "gnu_grep_bre": lambda req: _run_grep(req, extended=False),
    "gnu_grep_ere": lambda req: _run_grep(req, extended=True),
    "gnu_sed_bre": lambda req: _run_sed(req, extended=False),
    "gnu_sed_ere": lambda req: _run_sed(req, extended=True),
    "gnu_awk_ere": _run_awk,
}


def execute(req: MatchRequest) -> list[MatchItem]:
    runner = ENGINES.get(req.engine_id)
    if runner is None:
        raise ValueError(f"Unknown engine target routed to the POSIX worker: {req.engine_id}")
    return runner(req)
