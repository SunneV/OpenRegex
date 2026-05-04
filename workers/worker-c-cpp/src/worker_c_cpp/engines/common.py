import subprocess
import os
from openregex_libs.models import EngineFlag

WORKER_VERSION = os.environ.get("WORKER_VERSION", "Unknown")
WORKER_RELEASE_DATE = os.environ.get("WORKER_RELEASE_DATE", "Unreleased")


def get_pkg_version(*pkg_names: str) -> str:
    for pkg in pkg_names:
        try:
            res = subprocess.run(["pkg-config", "--modversion", pkg], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
    for pkg in pkg_names:
        try:
            res = subprocess.run(["dpkg-query", "-W", "-f=${Version}", pkg], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
    return "system"

def _detect_c_version() -> str:
    try:
        res = subprocess.run(["gcc", "-dM", "-E", "-x", "c", "/dev/null"], capture_output=True, text=True)
        if "201710L" in res.stdout: return "18"
        if "201112L" in res.stdout: return "11"
        if "199901L" in res.stdout: return "99"
        return "89" # ANSI C
    except Exception:
        return "Unknown"

def _detect_cpp_version() -> str:
    try:
        res = subprocess.run(["g++", "-dM", "-E", "-x", "c++", "/dev/null"], capture_output=True, text=True)
        if "202302L" in res.stdout: return "23"
        if "202002L" in res.stdout: return "20"
        if "201703L" in res.stdout: return "17"
        if "201402L" in res.stdout: return "14"
        if "201103L" in res.stdout: return "11"
        return "03"
    except Exception:
        return "Unknown"

# Allow environment variable overrides during build time, fallback to compiler detection
C_VERSION = os.environ.get("C_STANDARD_VERSION", _detect_c_version())
CPP_VERSION = os.environ.get("CPP_STANDARD_VERSION", _detect_cpp_version())

CAT_CLASSES = "Character Classes & Escapes"
CAT_ANCHORS = "Anchors & Boundaries"
CAT_QUANTIFIERS = "Quantifiers"
CAT_GROUPS = "Grouping & Backreferences"
CAT_ADVANCED = "Lookarounds & Advanced"

FLAG_METADATA: dict[str, tuple[str, str]] = {
    "i": ("Case-insensitive matching.", "Basic"),
    "m": ("Multiline mode. Makes ^ and $ work per line.", "Basic"),
    "s": ("DotAll mode. Makes . match newline.", "Basic"),
    "x": ("Extended/free-spacing mode. Ignores unescaped whitespace.", "Basic"),
    "u": ("Unicode or UTF mode, engine-specific behavior.", "Basic"),
    "U": ("Ungreedy mode, engine-specific behavior.", "Advance"),
    "J": ("Allow duplicate named capture groups.", "Unique"),
    "n": ("No auto-capture mode for plain (...).", "Advance"),
    "v": ("Allow invalid UTF in byte-mode matching (engine-specific).", "Advance"),
    "e": ("Allow empty matches to be reported (engine-specific).", "Unique"),
    "b": ("Treat input as raw bytes mode (engine-specific).", "Unique"),
    "w": ("Unicode word-boundary behavior (engine-specific).", "Advance"),
    "a": ("ASCII-only matching mode.", "Advance"),
    "f": ("Full Unicode case-folding mode.", "Advance"),
    "p": ("POSIX leftmost-longest matching mode.", "Advance"),
    "r": ("Reverse/right-to-left matching mode.", "Unique"),
}

def build_engine_flags(*flag_names: str) -> list[EngineFlag]:
    flags: list[EngineFlag] = []
    for name in flag_names:
        description, group = FLAG_METADATA.get(name, (f"Flag ({name})", "Basic"))
        flags.append(EngineFlag(name=name, description=description, group=group))
    return flags
