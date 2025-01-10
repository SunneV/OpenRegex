import pytest

from src.engine import CppRegex, JavaRegex, PythonRe, PythonRegex
from src.engine_manager import EngineManager


@pytest.fixture
def engine_manager():
    """Fixture to create an EngineManager instance before each test."""
    return EngineManager()


class TestEngineManager:
    def test_init_engine(self, engine_manager):
        """Test if all engines are initialized correctly."""
        assert len(engine_manager.engine) == 4
        assert "Python - re" in engine_manager.engine
        assert "Python - regex" in engine_manager.engine
        assert "Java" in engine_manager.engine
        assert "C++" in engine_manager.engine
        assert isinstance(engine_manager.engine["Python - re"], PythonRe)
        assert isinstance(engine_manager.engine["Python - regex"], PythonRegex)
        assert isinstance(engine_manager.engine["Java"], JavaRegex)
        assert isinstance(engine_manager.engine["C++"], CppRegex)

    def test_get_engine_list(self, engine_manager):
        """Test if get_engine_list returns the correct list of engine names."""
        engine_list = engine_manager.get_engine_list()
        assert len(engine_list) == 4
        assert "Python - re" in engine_list
        assert "Python - regex" in engine_list
        assert "Java" in engine_list
        assert "C++" in engine_list

    def test_get_engine_existing(self, engine_manager):
        """Test if get_engine returns an existing engine correctly."""
        python_re_engine = engine_manager.get_engine("Python - re")
        assert isinstance(python_re_engine, PythonRe)

    def test_get_engine_nonexistent(self, engine_manager):
        """Test if get_engine returns None for a nonexistent engine."""
        nonexistent_engine = engine_manager.get_engine("nonexistent_engine")
        assert nonexistent_engine is None

    def test_match_python_re(self, engine_manager):
        pattern = r"(?P<name>\w+)\W"
        text = "Hello, World!"
        expected_result = [
            {"match": "Hello,", "index": [0, 6], "groups": [{"name": "name", "value": "Hello", "index": [0, 5]}]},
            {"match": "World!", "index": [7, 13], "groups": [{"name": "name", "value": "World", "index": [7, 12]}]},
        ]
        matches, error, execution_time = engine_manager.match("Python - re", pattern, text, flags=0)
        assert matches == expected_result
        assert error == ""

    def test_match_timeout(self, engine_manager, monkeypatch):
        """Test if the timeout mechanism works correctly."""
        # Shorten the timeout for the test
        monkeypatch.setattr(engine_manager, "timeout", 3.00)
        pattern = r"(a+)+$"
        text = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!"
        matches, error, execution_time = engine_manager.match("Python - re", pattern, text)
        assert matches == []
        assert error == f"Timeout exceeded: {3.00} seconds"

    def test_match_no_timeout(self, engine_manager, monkeypatch):
        """Test if the regex matching works correctly when there's no timeout."""
        # Mock time.sleep to make it instant
        monkeypatch.setattr(engine_manager, "timeout", 1000)
        pattern = r"^a.*h$"
        text = "abcdefgh"
        matches, error, execution_time = engine_manager.match("Python - re", pattern, text)
        assert error == ""
        assert matches[0]["match"] == "abcdefgh"
