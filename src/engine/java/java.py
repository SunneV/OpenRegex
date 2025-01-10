"""
This module provides the JavaRegex class which integrates Java-based regex
functionality with Python.
"""

import json
import os
import subprocess

import requests

from project import Path, log
from src.engine.basic import BasicRegexEngine


class JavaRegex(BasicRegexEngine):
    """Class to handle Java-based regex operations."""

    def __init__(self):
        super().__init__()
        self.java_cli_path = os.path.join(Path.ENGINE_JAVA, "JavaRegexCLI.class")
        self.gson_jar_path = os.path.join(Path.ENGINE_JAVA, "gson-2.8.9.jar")
        self.java_cli_source = os.path.join(Path.ENGINE_JAVA, "JavaRegexCLI.java")
        self._download_gson_if_not_exists()
        self._compile_java_if_not_compiled()

    def _download_gson_if_not_exists(self):
        """Downloads gson jar if not exists."""
        if not os.path.exists(self.gson_jar_path):
            log.info(f"Gson jar not found. Downloading to {self.gson_jar_path}")
            url = "https://repo1.maven.org/maven2/com/google/code/gson/gson/2.8.9/gson-2.8.9.jar"
            try:
                response = requests.get(url, stream=True, timeout=10)
                response.raise_for_status()
                with open(self.gson_jar_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                log.info("Gson jar downloaded successfully.")
            except requests.exceptions.RequestException as e:
                log.error(f"Error downloading Gson jar: {e}")

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
