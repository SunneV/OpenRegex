import re

import pytest

from src.engine import CppRegex


@pytest.fixture
def engine():
    return CppRegex()


class TestCppRegex:
    def test_version(self, engine):
        assert re.match(r"^g\+\+ - \d+\.\d+\.\d+$", engine.version)

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

    def test_error_match(self, engine):
        pattern = r"(?s<word>[A-Z]\w+)\W"
        text = "Hello, World!"
        expected_result = ([], "Invalid '(?...)' zero-width assertion in regular expression")
        result = engine.match(pattern=pattern, text=text, flags=0)
        assert result == expected_result
