import re

import pytest

from src.engine.java.java import JavaRegex


@pytest.fixture
def engine():
    return JavaRegex()


class TestJavaRegex:
    def test_version(self, engine):
        assert re.match(r"JDK - \d+\.\d+\.\d+$", engine.version)  # Ensure version follows X.Y.Z pattern

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
            "Error from java CLI Error during regex match: Unknown inline modifier near index 3\n"
            "(?s<word>[A-Z]\\w+)\\W\n"
            "   ^\n",
        )
        result = engine.match(pattern=pattern, text=text, flags=0)
        assert result == expected_result

    def test_get_available_flags(self, engine):
        flags = engine.get_available_flags()
        assert "CASE_INSENSITIVE" in flags
        assert "MULTILINE" in flags
        assert "DOTALL" in flags
