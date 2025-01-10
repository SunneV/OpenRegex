import logging
import re

import pytest

from project import log
from src.engine.python_re import PythonRe


@pytest.fixture(scope="session", autouse=True)
def set_log_level():
    log.setLevel(logging.DEBUG)


@pytest.fixture
def engine():
    return PythonRe()


class TestPythonRe:
    def test_version(self, engine):
        assert re.match(r"^\d+\.\d+\.\d+$", engine.version)  # Update to the actual version of the `re` module

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
        pattern = r"(?P<word>[A-Z]\w+)\W"
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
        pattern = r"(?P<name>\d+)\W"
        text = "Hello, World!"
        expected_result = ([], "")
        result = engine.match(pattern=pattern, text=text, flags=0)
        assert result == expected_result

    def test_error_match(self, engine):
        pattern = r"(?s<word>[A-Z]\w+)\W"
        text = "Hello, World!"
        expected_result = ([], "missing -, : or ) at position 3")
        result = engine.match(pattern=pattern, text=text, flags=0)
        assert result == expected_result

    def test_get_available_flags(self, engine):
        flags = engine.get_available_flags()
        assert "IGNORECASE" in flags
        assert "MULTILINE" in flags
        assert "DOTALL" in flags
