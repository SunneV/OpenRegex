"""Executes patterns on a real Vim, driven through a scratch buffer.

Vim has no library binding, so every request spawns `vim -es` running
engine.vim. Vim reports byte offsets, which are translated to Unicode code point
indices here.

Vim's script API can report where a match starts and ends but has no way to ask
for the position of a capture group, so this engine reports whole matches only.
"""

import json
import os
import subprocess
import tempfile
from array import array
from itertools import accumulate

from openregex_libs.models import MatchItem, MatchRequest
from openregex_libs.runtime import MAX_MATCHES, TIMEOUT_MS

ENGINE_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine.vim")
VIM_BINARY = os.environ.get("VIM_BINARY", "vim")
TIMEOUT_S = TIMEOUT_MS / 1000.0

# Vim's magic-level and case atoms are prefixes, so the flags are simply
# prepended to the pattern the user typed.
FLAG_METADATA: dict[str, tuple[str, str]] = {
    "i": ("Case-insensitive matching; prepends the \\c atom.", "Basic"),
    "I": ("Force case-sensitive matching; prepends the \\C atom.", "Basic"),
    "v": ("Very magic: most punctuation is a metacharacter, like other engines.", "Unique"),
    "m": ("Magic (Vim's default): some metacharacters need a backslash.", "Unique"),
    "M": ("Nomagic: only ^ and $ keep their special meaning.", "Unique"),
    "V": ("Very nomagic: everything but the backslash is literal.", "Unique"),
}

FLAG_ATOMS = {
    "i": "\\c",
    "I": "\\C",
    "v": "\\v",
    "m": "\\m",
    "M": "\\M",
    "V": "\\V",
}

_UTF8_START_TABLE = bytes(0 if 0x80 <= b < 0xC0 else 1 for b in range(256))


def _byte_to_char_map(text: str):
    if text.isascii():
        return None
    starts = text.encode("utf-8").translate(_UTF8_START_TABLE)
    return array("I", accumulate(starts, initial=0))


def vim_version() -> str:
    try:
        result = subprocess.run([VIM_BINARY, "--version"], capture_output=True, text=True, timeout=10)
        first_line = result.stdout.splitlines()[0] if result.stdout else ""
        # "VIM - Vi IMproved 9.1 (2024 Jan 02, compiled ...)"
        parts = first_line.split()
        for index, token in enumerate(parts):
            if token == "IMproved" and index + 1 < len(parts):
                return parts[index + 1]
        return first_line.strip() or "unknown"
    except Exception:
        return "unknown"


def build_pattern(pattern: str, flags: list[str]) -> str:
    prefix = ""
    for flag in flags:
        flag = flag.strip()
        if not flag:
            continue
        if flag not in FLAG_ATOMS:
            raise ValueError(f"Unsupported flag '{flag}' for the Vim engine")
        prefix += FLAG_ATOMS[flag]
    return prefix + pattern


def _invoke(request: dict, engine_id: str) -> dict:
    in_fd, in_path = tempfile.mkstemp(prefix="openregex-vim-in-", suffix=".json")
    out_fd, out_path = tempfile.mkstemp(prefix="openregex-vim-out-", suffix=".json")
    os.close(in_fd)
    os.close(out_fd)

    try:
        with open(in_path, "w", encoding="utf-8") as handle:
            json.dump(request, handle)

        command = [
            VIM_BINARY, "-es",
            "-u", "NONE", "-i", "NONE", "-n",
            "--cmd", "set nocompatible encoding=utf-8",
            "-S", ENGINE_SCRIPT,
        ]
        environment = {**os.environ, "OPENREGEX_IN": in_path, "OPENREGEX_OUT": out_path,
                       "LC_ALL": "C.UTF-8", "LANG": "C.UTF-8"}

        try:
            result = subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=TIMEOUT_S,
                env=environment,
            )
        except subprocess.TimeoutExpired as exc:
            raise ValueError(f"TIMEOUT: {engine_id} execution exceeded {TIMEOUT_MS}ms SLA.") from exc
        except FileNotFoundError as exc:
            raise ValueError(f"Engine binary missing from the worker image: {VIM_BINARY}") from exc

        with open(out_path, encoding="utf-8") as handle:
            raw = handle.read().strip()

        if not raw:
            message = result.stderr.decode("utf-8", "replace").strip()
            raise ValueError(message or "Vim exited without producing a result.")

        return json.loads(raw)
    finally:
        for path in (in_path, out_path):
            try:
                os.unlink(path)
            except OSError:
                pass


def execute(req: MatchRequest) -> list[MatchItem]:
    payload = _invoke({
        "regex": build_pattern(req.regex, req.flags),
        "text": req.text,
        "max_matches": MAX_MATCHES + 1,
    }, req.engine_id)

    if payload.get("error"):
        raise ValueError(str(payload["error"]).strip())

    spans = payload.get("matches", [])
    if len(spans) > MAX_MATCHES:
        raise ValueError(f"Exceeded maximum allowed matches ({MAX_MATCHES}).")

    b2c = _byte_to_char_map(req.text)
    last = (len(b2c) - 1) if b2c is not None else 0

    def to_char(byte_index: int) -> int:
        return byte_index if b2c is None else b2c[min(byte_index, last)]

    matches: list[MatchItem] = []
    for index, (byte_start, byte_end) in enumerate(spans):
        start = to_char(byte_start)
        end = to_char(byte_end)
        matches.append(MatchItem(
            match_id=index,
            full_match=req.text[start:end],
            start=start,
            end=end,
            groups=[],
        ))
    return matches
