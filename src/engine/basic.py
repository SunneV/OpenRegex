import traceback
from abc import ABC, abstractmethod

from project import Config, log

# pattern for sheet template
_REGEX_CHEAT_SHEET_TEMPLATE = [
    {
        "category": "",
        "items": [
            {
                "character": r"",
                "description": "",
            }
        ],
    },
]

_REGEX_EXAMPLES_TEMPLATE = {
    "input_regex": r"",
    "input_text": r"",
}


class BasicRegexEngine(ABC):
    """Abstract base class for regex engines.

    This class defines the common interface for all regex engines.
    Subclasses must implement the abstract methods `_get_version`, `_match`,
    `get_available_flags`, and `_handle_exception`.
    """

    regex_cheat_sheet = _REGEX_CHEAT_SHEET_TEMPLATE
    regex_examples = _REGEX_EXAMPLES_TEMPLATE

    def __init__(self):
        """Initializes the BasicRegexEngine.

        Sets the name and version of the engine using the abstract methods
        `_set_name` and `_get_version`.
        """
        self.name: str = self._set_name()
        self.version: str = self._get_version()

    def _set_name(self) -> str:
        """Sets the name of the engine.

        :return: The name of the engine (defaults to the class name).
        :rtype: str
        """
        return self.__class__.__name__

    def match(self, pattern: str, text: str, flags: int = 0) -> tuple[list[dict], str]:
        """Matches a pattern against a text using the engine's implementation.

        :param pattern: The regular expression pattern.
        :type pattern: str
        :param text: The text to search.
        :type text: str
        :param flags: Flags to control the matching behavior. Defaults to 0.
        :type flags: int, optional
        :raises Exception: If an error occurs during matching.
        :return: A tuple containing a list of match dictionaries and an error string.
                The list of dictionaries represents the matches found. Each dictionary has the following structure:
                {
                    'match': The matched substring,
                    'index': A list containing the start and end indices of the match,
                    'groups': A list of dictionaries representing the captured groups. Each group dictionary has the
                                following structure:
                    {
                        'name': The name of the group (if defined),
                        'value': The value of the group,
                        'index': A list containing the start and end indices of the group
                    }
                }
                The error string will be empty if no error occurred, or contain an error message otherwise.
        :rtype: tuple[list[dict], str]

        :examples:
            >>> engine = SomeRegexEngine()  # Replace SomeRegexEngine with an actual subclass
            >>> pattern = r'(?P<name>\\w+)\\W'
            >>> text = 'Hello, World!'
            >>> matches, error = engine.match(pattern, text)
            >>> matches
            [
                {
                    'match': 'Hello,',
                    'index': [0, 6],
                    'groups': [{
                        'name': 'name',
                        'value': 'Hello',
                        'index': [0, 5]
                    }]
                },
                {
                    'match': 'World!',
                    'index': [7, 13],
                    'groups': [{
                        'name': 'name',
                        'value': 'World',
                        'index': [7, 12]
                    }]
                }
            ]
            >>> error
            ''
        """
        error: str = ""
        try:
            log.debug(f"{self.__class__.__name__} -> Matching pattern: {pattern} in text: {text}")
            result: list[dict] = self._match(pattern, text, flags)
            log.debug(f"{self.__class__.__name__} -> Matched result: {result}")
        except Exception as e:
            result: list[dict] = []
            error = self._handle_exception(e)
            if Config.log_level == "DEBUG":
                detailed_error = f"{self.__class__.__name__} -> Matched result: {error}\n{traceback.format_exc()}"
                log.error(detailed_error)
        return result, error

    @abstractmethod
    def _get_version(self) -> str:
        """Gets the version of the regex engine.

        :return: The version of the engine.
        :rtype: str
        """
        raise NotImplementedError("This method should be implemented in the child class.")

    @abstractmethod
    def _match(self, pattern: str, text: str, flags: int) -> list[dict]:
        """Performs the actual regex matching.

        This method must be implemented by each subclass to provide the specific matching logic.

        :param pattern: The regular expression pattern.
        :type pattern: str
        :param text: The text to search.
        :type text: str
        :param flags: Flags to control the matching behavior.
        :type flags: int
        :return: A list of match dictionaries. See `match` method for the structure of the dictionaries.
        :rtype: list[dict]
        """
        raise NotImplementedError("This method should be implemented in the child class.")

    @abstractmethod
    def get_available_flags(self) -> dict:
        """Gets the available flags for the regex engine.

        :return: A dictionary where keys are flag names and values are their corresponding values.
        :rtype: dict
        """
        raise NotImplementedError("This method should be implemented in the child class.")

    @abstractmethod
    def _handle_exception(self, e: Exception) -> str:
        """Handles exceptions raised during matching.

        :param e: The exception that was raised.
        :type e: Exception
        :return: A string representation of the exception. It can also return custom error message
        :rtype: str
        """
        return str(e)
