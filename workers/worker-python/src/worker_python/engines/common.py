import os
import platform
import regex as py_regex
from openregex_libs.models import EngineFlag

WORKER_VERSION = os.environ.get("WORKER_VERSION", "Unknown")
WORKER_RELEASE_DATE = os.environ.get("WORKER_RELEASE_DATE", "Unreleased")

_py_ver = platform.python_version_tuple()
PYTHON_MAJOR_MINOR = f"{_py_ver[0]}.{_py_ver[1]}"
REGEX_VERSION = py_regex.__version__

CAT_CLASSES = "Character Classes & Escapes"
CAT_ANCHORS = "Anchors & Boundaries"
CAT_QUANTIFIERS = "Quantifiers"
CAT_GROUPS = "Grouping & Backreferences"
CAT_ADVANCED = "Lookarounds & Advanced"

FLAG_METADATA: dict[str, tuple[str, str]] = {
    "i": ("Case-insensitive matching.", "Basic"),
    "m": ("Multiline mode. Makes ^ and $ work per line.", "Basic"),
    "s": ("DotAll mode. Makes . match newline.", "Basic"),
    "x": ("Verbose mode. Ignores unescaped whitespace and allows comments.", "Basic"),
    "u": ("Unicode mode for character classes and case operations.", "Basic"),
    "a": ("ASCII-only matching for character classes and boundaries.", "Advance"),
    "f": ("Full Unicode case-folding for case-insensitive matching.", "Advance"),
    "w": ("Unicode word-boundary behavior.", "Advance"),
    "b": ("Best fuzzy match mode.", "Unique"),
    "e": ("Enhanced fuzzy matching mode.", "Unique"),
    "p": ("POSIX leftmost-longest matching mode.", "Advance"),
    "r": ("Reverse/right-to-left matching mode.", "Unique"),
}

def build_engine_flags(*flag_names: str) -> list[EngineFlag]:
    flags: list[EngineFlag] = []
    for name in flag_names:
        description, group = FLAG_METADATA.get(name, (f"Flag ({name})", "Basic"))
        flags.append(EngineFlag(name=name, description=description, group=group))
    return flags
