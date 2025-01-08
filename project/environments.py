"""
This module provides environment configuration and utility functions for the project.
"""

import os
import platform
import re
from dataclasses import dataclass


def _get_path_n_levels_up(path, n) -> str:
    """
    Get the path n levels up
    :param path: path to start from
    :param n: number of levels up
    :return: path n levels up
    """
    return os.path.normpath(os.path.join(path, *[".."] * n))


def _get_version():
    try:
        with open(os.path.join(_Path.PROJECT, "CHANGELOG.md"), "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        print("CHANGELOG.md not found.")
        return None, None
    pattern = re.compile(r"## \[(\d+\.\d+\.\d+(?:-[\w]+)?)] - (\d{4}-\d{2}-\d{2})")
    # Regular expression to match the version and release date
    match = re.search(pattern, content)
    if match:
        version = match.group(1)
        release_date = match.group(2)
        return version, release_date
    return None, None


@dataclass
class _Path:
    PROJECT = _get_path_n_levels_up(os.path.dirname(__file__), 1)
    ENGINE_CPP = os.path.join(PROJECT, "src", "engine", "cpp")
    ENGINE_JAVA = os.path.join(PROJECT, "src", "engine", "java")


@dataclass()
class _App:
    name = "OpenRegex "
    description = "OpenSource self hosted regex debug tool"
    version, release_date = _get_version()
    author = "Wojciech Cichoń"
    linkedin = "https://www.linkedin.com/in/wojciech-cicho%C5%84-421127141/"
    repository = "https://github.com/SunneV/OpenRegex"
    python_version = platform.python_version()


@dataclass()
class _Config:
    port = int(os.getenv("OPENREGEX_PORT", "5000"))
    log_level = os.getenv("OPENREGEX_LOG_LEVEL", "INFO").upper()
    regex_timeout = int(os.getenv("OPENREGEX_TIMEOUT_S", "5"))
    debug = log_level == "DEBUG"


def write_version_to_env(target_file):
    """Writes a version string to a specified target file in KEY=VALUE format."""

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(f"APP_VERSION={_App.version}\n")


if __name__ == "__main__":
    print(_App.version)