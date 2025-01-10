"""
This module provides a PythonRegex class that extends the BasicRegexEngine
to use the regex module for regular expression operations.
"""

import inspect

import regex

from src.engine.basic import BasicRegexEngine


class PythonRegex(BasicRegexEngine):
    """
    A regex engine implementation using the regex module.
    """

    def _set_name(self):
        return "Python - regex"

    def _get_version(self) -> str:
        return getattr(regex, "__version__", "unknown")

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

    def _match(self, pattern, text, flags):
        regex_obj = regex.compile(pattern, flags)
        matches = []
        for match in regex_obj.finditer(text):
            # Get groups, including unnamed ones
            groups = match.groups()

            # Get named group dict
            named_group_dict = regex_obj.groupindex

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

    def get_available_flags(self) -> dict:
        """Returns a dictionary of available flags in regex module."""
        flags_dict = {}
        for name, value in inspect.getmembers(regex):
            if isinstance(value, int) and name.isupper():
                flags_dict[name] = value
        return flags_dict

    def _handle_exception(self, e) -> str:
        return str(e)
