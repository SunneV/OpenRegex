"""
Module for C++ regex engine integration using ctypes.
"""

import ctypes
import os
import re
import subprocess
from ctypes import POINTER, Structure, c_char_p, c_size_t

from project import Path, log
from src.engine.basic import BasicRegexEngine

_REGEX_CHEAT_SHEET_TEMPLATE_CPP = [
    {
        "category": "Core Matching",
        "items": [
            {"character": ".", "description": "Any character (except newline)"},
            {"character": "[abc]", "description": "Any one character: a, b, or c"},
            {"character": "[^abc]", "description": "Any one character except: a, b, or c"},
            {"character": "[a-z]", "description": "Any one character in the range a-z"},
            {"character": "[a-zA-Z]", "description": "Any one character in the range a-z or A-Z"},
            {"character": "\\d", "description": "Any digit (equivalent to [0-9])"},
            {"character": "\\D", "description": "Any non-digit (equivalent to [^0-9])"},
            {"character": "\\s", "description": "Any whitespace character"},
            {"character": "\\S", "description": "Any non-whitespace character"},
            {"character": "\\w", "description": "Any word character (alphanumeric and underscore)"},
            {"character": "\\W", "description": "Any non-word character"},
            {"character": "\\\\", "description": "Literal backslash"},
            {"character": "\\ooo", "description": "Character with octal value ooo (up to three digits)"},
            {"character": "\\xhh", "description": "Character with hexadecimal value hh (two digits)"},
            {"character": "\\uhhhh", "description": "Character with Unicode hexadecimal value hhhh (four digits)"},
            {"character": "\\n", "description": "Newline character"},
            {"character": "\\r", "description": "Carriage return character"},
            {"character": "\\t", "description": "Tab character"},
            {"character": "\\f", "description": "Form feed character"},
            {"character": "\\v", "description": "Vertical tab character"},
            {"character": "?", "description": "Zero or one (optional)"},
            {"character": "*", "description": "Zero or more"},
            {"character": "+", "description": "One or more"},
            {"character": "{n}", "description": "Exactly n"},
            {"character": "{n,}", "description": "n or more"},
            {"character": "{n,m}", "description": "Between n and m"},
        ],
    },
    {
        "category": "Grouping and Logic",
        "items": [
            {"character": "( )", "description": "Capturing group"},
            {"character": "(?: )", "description": "Non-capturing group"},
            {"character": "|", "description": "OR operator (match either the expression before or after)"},
            {
                "character": "\\1, \\2, ...",
                "description": "Backreference to captured group (numbered from left to right)",
            },
        ],
    },
    {
        "category": "Anchors and Lookarounds",
        "items": [
            {"character": "^", "description": "Matches the beginning of a line/string"},
            {"character": "$", "description": "Matches the end of a line/string"},
            {"character": "\\b", "description": "Matches a word boundary"},
            {"character": "\\B", "description": "Matches a non-word boundary"},
            {"character": "(?= )", "description": "Positive lookahead assertion"},
            {"character": "(?! )", "description": "Negative lookahead assertion"},
            {"character": "(?<= )", "description": "Positive lookbehind assertion"},
            {"character": "(?<! )", "description": "Negative lookbehind assertion"},
        ],
    },
]

_REGEX_EXAMPLES_PYTHON_CPP = {
    "input_regex": r"((?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d"
    r"\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))(/(\d{1,2}))?(?:-((?:25[0-5]|2[0-4]\d|1\d\d|[1-9"
    r"]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]"
    r"\d|1\d\d|[1-9]?\d)))?(:(\d{1,5}))?",
    "input_text": r"""192.168.1.100
192.168.1.100:8080
127.0.0.1
192.168.1.0/24
192.168.1.1-192.168.1.255
192.168.1.1-192.168.1.255:80
192.168.1.0/24:80""",
}


class Match(Structure):
    """
    Structure to hold a single regex match.
    """

    _fields_ = [
        ("match", c_char_p),
        ("start", c_size_t),
        ("group_count", c_size_t),
        ("groups", POINTER(c_char_p)),
        ("group_positions", POINTER(c_size_t)),
    ]


class MatchResult(Structure):
    """
    Structure to hold the result of regex matches.
    """

    _fields_ = [
        ("matches", POINTER(Match)),
        ("match_count", c_size_t),
        ("error_message", c_char_p),
    ]


class CppRegex(BasicRegexEngine):
    """
    C++ Regex engine class.
    """

    def __init__(self):
        if os.name == "nt":
            lib_name = "CppRegex.dll"
        else:  # Assume Linux or other UNIX-like OS
            lib_name = "CppRegex.so"
        self.cpp_path = os.path.join(Path.ENGINE_CPP, "CppRegex.cpp")
        self.lib_path = os.path.join(Path.ENGINE_CPP, lib_name)
        self._compile_dll_if_not_compiled()
        super().__init__()
        self.regex_cheat_sheet = _REGEX_CHEAT_SHEET_TEMPLATE_CPP
        self.regex_examples = _REGEX_EXAMPLES_PYTHON_CPP

    def _compile_dll_if_not_compiled(self):
        if not os.path.exists(self.lib_path):
            if os.name == "nt":
                compiler = "g++"
                compile_cmd = [
                    compiler,
                    "-shared",
                    "-o",
                    self.lib_path,
                    self.cpp_path,
                    "-static-libgcc",
                    "-static-libstdc++",
                    "-fPIC",
                ]
            else:
                compiler = "g++"
                compile_cmd = [
                    compiler,
                    "-shared",
                    "-o",
                    self.lib_path,
                    self.cpp_path,
                    "-fPIC",
                ]
            try:
                log.info(f"Compiling {self.cpp_path} for {os.name}...")
                subprocess.run(compile_cmd, check=True)
                log.info(f"Successfully compiled: {self.lib_path}")
            except subprocess.CalledProcessError as e:
                log.error(f"Compilation failed with error: {e}")
            except FileNotFoundError:
                log.error(f"Error: {compiler} not found. Ensure you have g++ installed.")

    def _set_name(self):
        return "C++"

    def _get_version(self) -> str:
        try:
            result = subprocess.run(["g++", "--version"], capture_output=True, text=True, check=True)
            output = result.stdout
            version_match = re.search(r"g\+\+.*?(\d+\.\d+\.\d+)", output)
            if version_match:
                version = version_match.group(1)
                return f"g++ - {version}"
            return "g++ version not found"
        except subprocess.CalledProcessError as e:
            return f"Error retrieving G++ version: {str(e)}"

    def _load_library(self):
        try:
            return ctypes.CDLL(self.lib_path, winmode=0)
        except OSError as e:
            log.critical(f"Failed to load library {self.lib_path}: {str(e)}")
            raise RuntimeError(f"Failed to load library {self.lib_path}: {str(e)}") from e

    def _match(self, pattern, text, flags):
        lib = self._load_library()
        lib.find_matches.argtypes = [c_char_p, c_char_p]
        lib.find_matches.restype = POINTER(MatchResult)
        lib.free_match_result.argtypes = [POINTER(MatchResult)]

        result = lib.find_matches(text.encode(), pattern.encode())
        if not result:
            raise RuntimeError("Regex timeout")

        if result.contents.error_message:
            error = result.contents.error_message.decode()
            lib.free_match_result(result)
            raise RuntimeError(error)

        matches = []
        for i in range(result.contents.match_count):
            match = result.contents.matches[i]
            full_match = match.match.decode()
            start = match.start
            groups = [(match.groups[j].decode(), match.group_positions[j]) for j in range(match.group_count)]
            matches.append((full_match, start, groups))

        lib.free_match_result(result)
        final_matches = self._process_matches(matches)
        return final_matches

    @staticmethod
    def _process_matches(matches: list) -> list:
        output_matches = []
        for match in matches:
            full_match = match[0]
            index_start = match[1]
            index_end = match[1] + len(match[0])
            groups = []
            for group in match[2]:
                group_start = group[1]
                group_end = group[1] + len(group[0])
                groups.append({"name": "", "value": group[0], "index": [group_start, group_end]})
            output_matches.append(
                {
                    "match": full_match,
                    "index": [index_start, index_end],
                    "groups": groups,
                }
            )
        return output_matches

    def _handle_exception(self, e) -> str:
        return str(e)

    def get_available_flags(self) -> dict:
        return {}
