"""
This module provides a PythonRegex class that extends the BasicRegexEngine
to use the regex module for regular expression operations.
"""

import inspect

import regex

from src.engine.basic import BasicRegexEngine

_REGEX_CHEAT_SHEET_TEMPLATE_PYTHON_REGEX = [
    {
        "category": "Core Matching",
        "items": [
            {"character": ".", "description": "Any character (except newline, by default)"},
            {"character": "[abc]", "description": "Any one character: a, b, or c"},
            {"character": "[^abc]", "description": "Any one character except: a, b, or c"},
            {"character": "[a-z]", "description": "Any one character in the range a-z"},
            {"character": "[a-zA-Z]", "description": "Any one character in the range a-z or A-Z"},
            {"character": "\\d", "description": "Any digit (equivalent to [0-9] in ASCII mode)"},
            {"character": "\\D", "description": "Any non-digit"},
            {"character": "\\s", "description": "Any whitespace character"},
            {"character": "\\S", "description": "Any non-whitespace character"},
            {"character": "\\w", "description": "Any word character (alphanumeric and underscore)"},
            {"character": "\\W", "description": "Any non-word character"},
            {"character": "\\\\", "description": "Literal backslash"},
            {
                "character": "\\p{...}",
                "description": "Character with the specified Unicode property (e.g., \\p{Ll} for lowercase letters)",
            },
            {"character": "\\P{...}", "description": "Character without the specified Unicode property"},
            {
                "character": "[[:name:]]",
                "description": "POSIX character class (e.g., [[:alnum:]] for alphanumeric characters)",
            },
            {"character": "[^[:name:]]", "description": "Negated POSIX character class"},
            {"character": "\\ooo", "description": "Character with octal value ooo (up to three digits)"},
            {"character": "\\xhh", "description": "Character with hexadecimal value hh (two digits)"},
            {"character": "\\uhhhh", "description": "Character with Unicode hexadecimal value hhhh (four digits)"},
            {
                "character": "\\Uhhhhhhhh",
                "description": "Character with Unicode hexadecimal value hhhhhhhh (eight digits)",
            },
            {"character": "\\n", "description": "Newline character"},
            {"character": "\\r", "description": "Carriage return character"},
            {"character": "\\t", "description": "Tab character"},
            {"character": "\\f", "description": "Form feed character"},
            {"character": "\\v", "description": "Vertical tab character"},
            {"character": "?", "description": "Zero or one (optional)"},
            {"character": "*", "description": "Zero or more"},
            {"character": "+", "description": "One or more"},
            {"character": "{n}", "description": "Exactly n"},
            {"character": "{n,}", "description": "n or more"},
            {"character": "{n,m}", "description": "Between n and m"},
        ],
    },
    {
        "category": "Grouping and Logic",
        "items": [
            {"character": "( )", "description": "Capturing group"},
            {"character": "(?: )", "description": "Non-capturing group"},
            {"character": "|", "description": "OR operator (match either the expression before or after)"},
            {
                "character": "\\1, \\2, ...",
                "description": "Backreference to captured group (numbered from left to right)",
            },
            {"character": "(?P=name)", "description": "Backreference to a named capturing group"},
            {"character": "\\g<0>", "description": "Entire matched string"},
            {"character": "(?(n)...|...)", "description": "Conditional expression based on capture group n"},
            {"character": "(?(<name>)...|...)", "description": "Conditional expression based on named capture group"},
            {"character": "(?(R)...|...)", "description": "Conditional expression based on recursion level"},
            {"character": "(?&name)", "description": "Recursion to a named group"},
            {"character": "(?0)", "description": "Recursion to the whole pattern"},
            {
                "character": "(?|...|...)",
                "description": "Branch reset: Capture groups within each branch have the same number",
            },
        ],
    },
    {
        "category": "Anchors and Lookarounds",
        "items": [
            {"character": "^", "description": "Matches the beginning of a line/string"},
            {"character": "$", "description": "Matches the end of a line/string"},
            {
                "character": "\\b",
                "description": "Matches a word boundary when outside a character class. (V1 behaviour)",
            },
            {
                "character": "\\B",
                "description": "Matches a non-word boundary when outside a character class. (V1 behaviour)",
            },
            {"character": "\\A", "description": "Matches the beginning of the string"},
            {"character": "\\Z", "description": "Matches the end of the string (or before the newline at the end)"},
            {"character": "\\z", "description": "Matches the absolute end of the string"},
            {"character": "(?= )", "description": "Positive lookahead assertion"},
            {"character": "(?! )", "description": "Negative lookahead assertion"},
            {"character": "(?<= )", "description": "Positive lookbehind assertion"},
            {"character": "(?<! )", "description": "Negative lookbehind assertion"},
            {
                "character": "(?> )",
                "description": "Atomic group: Once matched, the engine will not backtrack into this group.",
            },
            {
                "character": "*+",
                "description": "Possessive quantifier: Matches as many as possible, without giving back (no backtrackin"
                "g).",
            },
            {
                "character": "++",
                "description": "Possessive quantifier: Matches as many as possible, without giving back.",
            },
            {"character": "?+", "description": "Possessive quantifier: Matches one or none, without giving back."},
            {"character": "{n,}+", "description": "Possessive quantifier: Matches n or more, without giving back."},
            {
                "character": "{n,m}+",
                "description": "Possessive quantifier: Matches between n and m, without giving back.",
            },
        ],
    },
]

_REGEX_EXAMPLES_PYTHON_REGEX = {
    "input_regex": r"(?P<IP>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]"
    r"\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))(/(\d{1,2}))?(?:-(?P<IP2>(?:25[0-5]|2[0-4]"
    r"\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:2"
    r"5[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)))?(:(?<port>\d{1,5}))?",
    "input_text": r"""192.168.1.100
192.168.1.100:8080
127.0.0.1
192.168.1.0/24
192.168.1.1-192.168.1.255
192.168.1.1-192.168.1.255:80
192.168.1.0/24:80""",
}


class PythonRegex(BasicRegexEngine):
    """
    A regex engine implementation using the regex module.
    """

    def __init__(self):
        super().__init__()
        self.regex_cheat_sheet = _REGEX_CHEAT_SHEET_TEMPLATE_PYTHON_REGEX
        self.regex_examples = _REGEX_EXAMPLES_PYTHON_REGEX

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
