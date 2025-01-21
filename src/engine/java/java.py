"""
This module provides the JavaRegex class which integrates Java-based regex
functionality with Python.
"""

import hashlib
import json
import os
import subprocess

import requests

from project import Path, log
from src.engine.basic import BasicRegexEngine

_REGEX_CHEAT_SHEET_TEMPLATE_JAVA = [
    {
        "category": "Core Matching",
        "items": [
            {"character": ".", "description": "Any character (may or may not match line terminators)"},
            {"character": "[abc]", "description": "Any one character: a, b, or c"},
            {"character": "[^abc]", "description": "Any one character except: a, b, or c (negation)"},
            {"character": "[a-z]", "description": "Any one character in the range a-z (range)"},
            {"character": "[a-zA-Z]", "description": "Any one character in the range a-z or A-Z (range)"},
            {"character": "\\d", "description": "Any digit: [0-9]"},
            {"character": "\\D", "description": "Any non-digit: [^0-9]"},
            {"character": "\\s", "description": "Any whitespace character: [ \\t\\n\\x0B\\f\\r]"},
            {"character": "\\S", "description": "Any non-whitespace character: [^\\s]"},
            {"character": "\\w", "description": "Any word character: [a-zA-Z_0-9]"},
            {"character": "\\W", "description": "Any non-word character: [^\\w]"},
            {"character": "\\\\", "description": "Literal backslash"},
            {
                "character": "\\p{...}",
                "description": "Character with the specified Unicode property (e.g., \\p{Ll} for lowercase letters)",
            },
            {"character": "\\P{...}", "description": "Character without the specified Unicode property"},
            {
                "character": "[[:name:]]",
                "description": "POSIX character class (e.g., [[:alnum:]] for alphanumeric characters)",
            },
            {"character": "[^[:name:]]", "description": "Negated POSIX character class"},
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
            {"character": "\\k<name>", "description": "Backreference to a named capturing group"},
        ],
    },
    {
        "category": "Anchors and Lookarounds",
        "items": [
            {"character": "^", "description": "Matches the beginning of a line/string"},
            {"character": "$", "description": "Matches the end of a line/string"},
            {"character": "\\b", "description": "Matches a word boundary"},
            {"character": "\\B", "description": "Matches a non-word boundary"},
            {"character": "\\A", "description": "Matches the beginning of the string"},
            {"character": "\\Z", "description": "Matches the end of the string (or before the newline at the end)"},
            {"character": "\\z", "description": "Matches the absolute end of the string"},
            {"character": "\\G", "description": "The end of the previous match"},
            {"character": "(?= )", "description": "Positive lookahead assertion"},
            {"character": "(?! )", "description": "Negative lookahead assertion"},
            {"character": "(?<= )", "description": "Positive lookbehind assertion"},
            {"character": "(?<! )", "description": "Negative lookbehind assertion"},
            {
                "character": "(?> )",
                "description": "Atomic group: Once matched, the engine will not backtrack into this group.",
            },
            {
                "character": "*+",
                "description": "Possessive quantifier: Matches as many as possible, without giving back (no backtrackin"
                "g).",
            },
            {
                "character": "++",
                "description": "Possessive quantifier: Matches as many as possible, without giving back.",
            },
            {"character": "?+", "description": "Possessive quantifier: Matches one or none, without giving back."},
            {"character": "{n,}+", "description": "Possessive quantifier: Matches n or more, without giving back."},
            {
                "character": "{n,m}+",
                "description": "Possessive quantifier: Matches between n and m, without giving back.",
            },
        ],
    },
]

_REGEX_EXAMPLES_PYTHON_JAVA = {
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


class JavaRegex(BasicRegexEngine):
    """Class to handle Java-based regex operations."""

    def __init__(self):
        super().__init__()
        self.regex_cheat_sheet = _REGEX_CHEAT_SHEET_TEMPLATE_JAVA
        self.regex_examples = _REGEX_EXAMPLES_PYTHON_JAVA
        self.java_cli_path = os.path.join(Path.ENGINE_JAVA, "JavaRegexCLI.class")
        self.gson_jar_path = os.path.join(Path.ENGINE_JAVA, "gson-2.8.9.jar")
        self.java_cli_source = os.path.join(Path.ENGINE_JAVA, "JavaRegexCLI.java")
        self._download_gson_if_not_exists()
        self._compile_java_if_not_compiled()

    def _download_gson_if_not_exists(self):
        """Downloads gson jar if not exists."""
        if not os.path.exists(self.gson_jar_path):
            log.info(f"Gson jar not found. Downloading to {self.gson_jar_path}")
            check_sum = "8a432c1d6825781e21a02db2e2c33c5fde2833b9"
            urls = [
                "https://repo1.maven.org/maven2/com/google/code/gson/gson/2.8.9/gson-2.8.9.jar",
                "https://search.maven.org/remotecontent?filepath=com/google/code/gson/gson/2.8.9/gson-2.8.9.jar"
                "https://mvnrepository.com/artifact/com.google.code.gson/gson/2.8.9"
                "https://repo.spring.io/release/com/google/code/gson/gson/2.8.9/gson-2.8.9.jar",
            ]

            for url in urls:
                try:
                    response = requests.get(url, stream=True, timeout=10)
                    response.raise_for_status()

                    # Calculate checksum while downloading
                    sha1_hash = hashlib.sha1()
                    with open(self.gson_jar_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                            sha1_hash.update(chunk)
                    downloaded_checksum = sha1_hash.hexdigest()

                    # Verify checksum
                    if downloaded_checksum == check_sum:
                        log.info("Gson jar downloaded successfully and checksum verified.")
                        break
                    else:
                        log.error(
                            f"Checksum mismatch for Gson jar downloaded from {url}. Expected: {check_sum}, "
                            f"Downloaded: {downloaded_checksum}"
                        )
                        os.remove(self.gson_jar_path)  # Remove the corrupted file

                except requests.exceptions.RequestException as e:
                    log.error(f"Error downloading Gson jar from {url}: {e}")
                    if os.path.exists(self.gson_jar_path):
                        os.remove(self.gson_jar_path)  # Remove partially downloaded file
            else:
                log.error("Failed to download Gson jar from all provided URLs.")

    def _compile_java_if_not_compiled(self):
        """Compiles Java code if .class files are not present."""
        if not os.path.exists(self.java_cli_path):
            log.warning("Java class not found. Compiling now.")
            try:
                classpath = f".{os.pathsep}{self.gson_jar_path}"
                subprocess.check_call(["javac", "-cp", classpath, self.java_cli_source])
                log.info("Java code compiled successfully.")
            except subprocess.CalledProcessError as e:
                log.error(f"Error during Java compilation: {e}")

    def _set_name(self):
        return "Java"

    def _get_version(self) -> str:
        try:
            result = subprocess.run(["java", "-version"], capture_output=True, text=True, check=True)
            version_line = result.stderr.splitlines()[0]
            version = version_line.split('"')[1]
            return f"JDK - {version}"
        except subprocess.CalledProcessError as e:
            return f"Error retrieving JDK version: {str(e)}"

    def _match(self, pattern, text, flags) -> list[dict]:
        java_flags = self._convert_flags_to_java(flags)
        classpath = f"{os.path.dirname(self.java_cli_path)}{os.pathsep}{self.gson_jar_path}"
        java_args = [
            "java",
            "--add-opens=java.base/java.util.regex=ALL-UNNAMED",
            "-cp",
            classpath,
            "JavaRegexCLI",
            pattern,
            text,
            str(java_flags),
        ]

        with subprocess.Popen(java_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            stdout, stderr = process.communicate()
            if stderr:
                raise RuntimeError(f"Error from java CLI {stderr}")
            result = json.loads(stdout)
            matches = result.get("matches", [])
            return matches

    def _convert_flags_to_java(self, flags):
        """Convert flags from python to java"""
        java_flags = 0
        for flag_name, flag_value in self.get_available_flags().items():
            if flags & flag_value:
                java_flags |= self._get_java_flag(flag_name)
        return java_flags

    def _get_java_flag(self, flag_name):
        with subprocess.Popen(
            [
                "java",
                "-cp",
                os.path.dirname(self.java_cli_path),
                "JavaRegexCLI",
                "getFlag",
                flag_name,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as process:
            stdout, stderr = process.communicate()
            if stderr:
                log.error(f"Error from java CLI {stderr}")
            return int(stdout)

    def get_available_flags(self) -> dict:
        return {
            "CASE_INSENSITIVE": 2,
            "MULTILINE": 8,
            "DOTALL": 32,
            "UNICODE_CASE": 64,
            "COMMENTS": 4,
            "LITERAL": 16,
        }

    def _handle_exception(self, e) -> str:
        return str(e)
