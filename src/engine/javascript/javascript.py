"""
Module for JavaScript (Node.js) regex engine integration.
"""

import json
import os
import re
import subprocess

from project import Config, Path, log
from src.engine.basic import BasicRegexEngine

# Basic Cheat Sheet - JS Regex has differences (e.g., lookbehind support varies)
_REGEX_CHEAT_SHEET_TEMPLATE_JS = [
    {
        "category": "Core Matching",
        "items": [
            {"character": ".", "description": "Any character (except newline unless 's' flag)"},
            {"character": "[abc]", "description": "Any one character: a, b, or c"},
            {"character": "[^abc]", "description": "Any one character except: a, b, or c"},
            {"character": "[a-z]", "description": "Any one character in the range a-z"},
            {"character": "\\d", "description": "Any digit [0-9]"},
            {"character": "\\D", "description": "Any non-digit [^0-9]"},
            {"character": "\\s", "description": "Any whitespace character"},
            {"character": "\\S", "description": "Any non-whitespace character"},
            {"character": "\\w", "description": "Any word character [a-zA-Z0-9_]"},
            {"character": "\\W", "description": "Any non-word character"},
            {"character": "\\n", "description": "Newline"},
            {"character": "\\t", "description": "Tab"},
            {"character": "?", "description": "Zero or one"},
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
            {"character": "(?<name> )", "description": "Named capturing group (ES2018+)"},
            {"character": "|", "description": "OR operator"},
            {"character": "\\1, \\2", "description": "Backreference to captured group"},
            {"character": "\\k<name>", "description": "Backreference to named group (ES2018+)"},
        ],
    },
    {
        "category": "Anchors and Lookarounds",
        "items": [
            {"character": "^", "description": "Beginning of string (or line if 'm' flag)"},
            {"character": "$", "description": "End of string (or line if 'm' flag)"},
            {"character": "\\b", "description": "Word boundary"},
            {"character": "\\B", "description": "Non-word boundary"},
            {"character": "(?= )", "description": "Positive lookahead"},
            {"character": "(?! )", "description": "Negative lookahead"},
            {"character": "(?<= )", "description": "Positive lookbehind (ES2018+)"},
            {"character": "(?<! )", "description": "Negative lookbehind (ES2018+)"},
        ],
    },
    {
        "category": "Flags",
        "items": [
            {"character": "g", "description": "Global search (find all matches)"},
            {"character": "i", "description": "Case-insensitive search"},
            {"character": "m", "description": "Multiline mode (^ and $ match start/end of line)"},
            {"character": "s", "description": ". matches newline characters (dotAll, ES2018+)"},
            {"character": "u", "description": "Unicode mode (treat pattern as sequence of Unicode code points)"},
            {"character": "y", "description": "Sticky mode (match only from 'lastIndex' position)"},
            {"character": "d", "description": "Generate indices for substring matches (ES2022+)"},
        ],
    },
]

# Example matching JS comments
_REGEX_EXAMPLES_JS = {
    "input_regex": r"(?<IP>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]"
    r"\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))(/(\d{1,2}))?(?:-(?<IP2>(?:25[0-5]|2[0-4]"
    r"\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:"
    r"25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)))?(:(?<port>\d{1,5}))?",
    "input_text": r"""192.168.1.100
192.168.1.100:8080
127.0.0.1
192.168.1.0/24
192.168.1.1-192.168.1.255
192.168.1.1-192.168.1.255:80
192.168.1.0/24:80""",
}


class JavaScriptRegex(BasicRegexEngine):
    """
    JavaScript (Node.js) Regex engine class.
    Requires Node.js to be installed and in the system PATH.
    """

    FLAG_MAP = {
        re.IGNORECASE: "i",
        re.MULTILINE: "m",
        re.DOTALL: "s",
        re.UNICODE: "u",
    }
    # Reverse map for get_available_flags (using Python's values for consistency)
    AVAILABLE_FLAGS = {
        "IGNORECASE": re.IGNORECASE,
        "MULTILINE": re.MULTILINE,
        "DOTALL": re.DOTALL,  # Representing JS 's'
        "UNICODE": re.UNICODE,  # Representing JS 'u'
    }

    def __init__(self):
        self.regex_time_out = Config.regex_timeout + 5
        self.node_path = "node"  # Assumes node is in PATH
        self.script_path = os.path.join(Path.ENGINE_JAVASCRIPT, "node_regex_cli.js")
        self._check_node_exists()
        super().__init__()
        self.regex_cheat_sheet = _REGEX_CHEAT_SHEET_TEMPLATE_JS
        self.regex_examples = _REGEX_EXAMPLES_JS

    def _check_node_exists(self):
        try:
            subprocess.run([self.node_path, "--version"], capture_output=True, check=True, text=True, encoding="utf-8")
            log.info(f"Node.js found at: {self.node_path}")
        except FileNotFoundError:
            log.error(
                f"Error: '{self.node_path}' command not found. Please install Node.js and ensure it's in your PATH."
            )
            raise EnvironmentError("Node.js not found. Please install it.")
        except subprocess.CalledProcessError as e:
            log.error(f"Error checking Node.js version: {e}")

    def _set_name(self):
        return "JavaScript"

    def _get_version(self) -> str:
        try:
            result = subprocess.run(
                [self.node_path, "--version"], capture_output=True, text=True, check=True, encoding="utf-8"
            )
            version = result.stdout.strip()
            return f"Node.js - {version[1:]}"
        except Exception as e:
            log.error(f"Could not get Node.js version: {e}")
            return "Node.js version unknown"

    def _convert_flags_to_js(self, flags: int) -> str:
        js_flags = ""
        for py_flag, js_char in self.FLAG_MAP.items():
            if flags & py_flag:
                js_flags += js_char
        return js_flags

    def _match(self, pattern: str, text: str, flags: int) -> list[dict]:
        js_flags_str = self._convert_flags_to_js(flags)
        cmd = [self.node_path, self.script_path, pattern, text, js_flags_str]

        try:
            process = subprocess.run(
                cmd, capture_output=True, text=True, check=True, encoding="utf-8", timeout=self.regex_time_out
            )
            output = process.stdout
            stderr = process.stderr
            if stderr:
                log.warning(f"Node.js stderr: {stderr.strip()}")
            result = json.loads(output)
            if result.get("error"):
                raise ValueError(f"Node.js Regex Error: {result['error']}")
            processed_matches = []
            for match in result.get("matches", []):
                for group in match.get("groups", []):
                    if group.get("value") is None:
                        group["value"] = ""
                processed_matches.append(match)

            return processed_matches

        except subprocess.TimeoutExpired:
            log.error(f"Node.js script timed out after {self.regex_time_out} seconds.")
            raise TimeoutError("JavaScript regex execution timed out.")
        except subprocess.CalledProcessError as e:
            log.error(f"Node.js script execution failed with exit code {e.returncode}")
            log.error(f"Command: {' '.join(cmd)}")
            log.error(f"Stderr: {e.stderr.strip()}")
            log.error(f"Stdout: {e.stdout.strip()}")
        except Exception as e:
            log.error(f"An unexpected error occurred during JavaScript matching: {e}")
            raise e

    def get_available_flags(self) -> dict:
        """Returns a dictionary of available flags mappable from Python's re."""
        return {}

    def _handle_exception(self, e: Exception) -> str:

        return str(e)
