"""
This module provides the PythonRe class which integrates Python's re module
functionality with a custom regex engine.
"""

import inspect
import re

from src.engine.basic import BasicRegexEngine


class PythonRe(BasicRegexEngine):
    """Class to handle Python's re module operations."""

    def _set_name(self):
        return "Python - re"

    def _get_version(self) -> str:
        return re.__version__

    def _match(self, pattern, text, flags):
        regex = re.compile(pattern, flags)
        matches = []
        for match in regex.finditer(text):
            # Get groups, including unnamed ones
            groups = match.groups()

            # Get named group dict
            named_group_dict = regex.groupindex

            # build all groups dict
            group_list = []

            for i, group_val in enumerate(groups):
                group_list.append(self._get_group_data(match, i + 1, group_val, named_group_dict))

            matches.append(
                {
                    "match": match.group(0),
                    "index": [match.start(), match.end()],
                    "groups": group_list,
                }
            )
        return matches

    @staticmethod
    def _get_group_data(match, group_index, group_val, named_group_dict):
        group_start = match.start(group_index)
        group_end = match.end(group_index)
        group_name = [name for name, index in named_group_dict.items() if index == group_index]

        return {
            "name": group_name[0] if group_name else "",
            "value": group_val if group_val else "",
            "index": [group_start, group_end] if group_val else [],
        }

    def get_available_flags(self) -> dict:
        """Returns a dictionary of available flags in re module."""
        flags_dict = {}
        for name, value in inspect.getmembers(re):
            if isinstance(value, int) and name.isupper():
                flags_dict[name] = value
        return flags_dict

    def _handle_exception(self, e) -> str:
        return str(e)
