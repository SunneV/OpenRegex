from abc import ABC, abstractmethod

from project import Config, log


class BasicRegexEngine(ABC):
    def __init__(self):
        self.name = self._set_name()
        self.version = self._get_version()

    def _set_name(self):
        return self.__class__.__name__

    def match(self, pattern, text, flags=0) -> tuple[list[dict], str]:
        r"""Return regex matches.

        Examples of the expected output:
        pattern = r'(?<name>\w+)\W'
        text = 'Hello, World!'
        expected_result = ([
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
                           ], '')
        """
        error = ""
        try:
            log.debug(f"Matching pattern: {pattern} in text: {text}")
            result = self._match(pattern, text, flags)
            log.debug(f"Matched result: {result}")
        except Exception as e:
            result = []
            error = self._handle_exception(e)
            if Config.log_level == "DEBUG":
                log.error(f"Matched result: {error}")
        return result, error

    @abstractmethod
    def _get_version(self) -> str:
        """Return the version of the regex engine."""
        raise NotImplementedError("This method should be implemented in the child class.")

    @abstractmethod
    def _match(self, pattern, text, flags) -> list[dict]:
        r"""
        Placeholder for the implementation of the regex matching logic.
        pattern = r'(?<name>\w+)\W'
        text = 'Hello, World!'
        expected_result = [
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
        """
        raise NotImplementedError("This method should be implemented in the child class.")

    @abstractmethod
    def get_available_flags(self) -> dict:
        """Return a dictionary of available flags."""
        raise NotImplementedError("This method should be implemented in the child class.")

    @abstractmethod
    def _handle_exception(self, e) -> str:
        raise NotImplementedError("This method should be implemented in the child class.")
