import logging
import re

import pytest

from project import log
from src.engine.javascript.javascript import JavaScriptRegex


@pytest.fixture(scope="session", autouse=True)
def set_log_level():
    log.setLevel(logging.DEBUG)


@pytest.fixture
def engine():
    return JavaScriptRegex()


class TestJavaScriptRegex:
    def test_version(self, engine):
        assert re.match(r"Node.js - \d+\.\d+\.\d+$", engine.version)  # Ensure version follows X.Y.Z pattern

    def test_match(self, engine):
        pattern = r"[A-Z]\w+"
        text = "Hello, World!"
        expected_result = (
            [{"match": "Hello", "index": [0, 5], "groups": []}, {"match": "World", "index": [7, 12], "groups": []}],
            "",
        )
        result = engine.match(pattern=pattern, text=text, flags=0)
        assert result == expected_result

    def test_match_group(self, engine):
        pattern = r"([A-Z]\w+)\W"
        text = "Hello, World!"
        expected_result = (
            [
                {"match": "Hello,", "index": [0, 6], "groups": [{"name": "", "value": "Hello", "index": [0, 5]}]},
                {"match": "World!", "index": [7, 13], "groups": [{"name": "", "value": "World", "index": [7, 12]}]},
            ],
            "",
        )
        result = engine.match(pattern=pattern, text=text, flags=0)
        assert result == expected_result

    def test_match_group_name(self, engine):
        pattern = r"(?<word>[A-Z]\w+)\W"
        text = "Hello, World!"
        expected_result = (
            [
                {"match": "Hello,", "index": [0, 6], "groups": [{"name": "word", "value": "Hello", "index": [0, 5]}]},
                {"match": "World!", "index": [7, 13], "groups": [{"name": "word", "value": "World", "index": [7, 12]}]},
            ],
            "",
        )
        result = engine.match(pattern=pattern, text=text, flags=0)
        assert result == expected_result

    def test_no_match(self, engine):
        pattern = r"(?<name>\d+)\W"
        text = "Hello, World!"
        expected_result = ([], "")
        result = engine.match(pattern=pattern, text=text, flags=0)
        assert result == expected_result

    def test_error_match(self, engine):
        pattern = r"(?s<word>[A-Z]\w+)\W"
        text = "Hello, World!"
        expected_result = (
            [],
            r"Node.js Regex Error: Invalid regular expression: /(?s<word>[A-Z]\w+)\W/g: Invalid group",
        )
        result = engine.match(pattern=pattern, text=text, flags=0)
        assert result == expected_result
