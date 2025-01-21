"""
This module provides utilities for generating colors, highlighting matches, and generating HTML tables.
"""

import html


class ColorGenerator:
    """
    Generates distinct colors for light and dark themes based on the golden angle.
    """

    def __init__(self, division_factor=1):
        golden_angle = 137.508  # Golden angle in degrees
        self.hue_step = golden_angle / division_factor
        self.light_theme_colors = {}
        self.dark_theme_colors = {}

    def generate_color(self, color_numbers):
        """Generates a list of distinct colors."""
        self.light_theme_colors = {}
        self.dark_theme_colors = {}

        for i in range(0, color_numbers * 4, 4):
            hue = (i * self.hue_step) % 360
            self.light_theme_colors[f"color-{i // 4}"] = f"hsl({hue}, 70%, 70%)"
            self.dark_theme_colors[f"color-{i // 4}"] = f"hsl({hue}, 50%, 30%)"

    def generate_gray_color(self, from_color, to_color):
        """Generates a list of gray colors."""

        for i in range(from_color, to_color):
            self.light_theme_colors[f"color-{i}"] = "hsl(0, 0%, 70%)"
            self.dark_theme_colors[f"color-{i}"] = "hsl(0, 0%, 30%)"


class MatchHighlighterText:
    """
    Highlights matches in text, handling nested groups correctly and without overlaps.
    """

    def highlight_matches(self, text, matches):
        """Highlights matches, handling nested groups correctly and without overlaps."""
        if not matches:
            return html.escape(text)

        parts = []
        last_match_end = 0

        for i, match_data in enumerate(matches):
            text_id = f"text-match-{i}"
            text_class = f"match-{i}"
            main_start, main_end = match_data["index"]
            begin_text = html.escape(text[last_match_end:main_start])
            parts.append(begin_text)
            match_text = text[main_start:main_end]

            highlighted_match = self._highlight_groups(match_text, match_data.get("groups", []), main_start, i)
            parts.append(
                f'<span id="{text_id}" class="match-main-highlight-output '
                f'match-main-highlight {text_class}">{highlighted_match}</span>'
            )

            last_match_end = main_end
        last_text = html.escape(text[last_match_end:])
        parts.append(last_text)
        final_str = "".join(parts)
        return final_str

    def _highlight_groups(self, match_text, groups, main_start, match_id):
        """Highlights groups, handling nesting correctly, sorted by length, keeping original order for colors."""
        if not groups:
            return match_text

        highlighted_text = list(match_text)  # Use a list for mutability
        highlighted_text = [html.escape(char) for char in highlighted_text]
        for i, group in enumerate(groups):
            group["enumeration"] = i
        filtered_groups = sorted([group for group in groups if group.get("index")], key=lambda x: x["index"][0])

        for group_info in filtered_groups:
            i = group_info["enumeration"]
            group_start = group_info["index"][0] - main_start
            group_end = group_info["index"][1] - main_start

            # Replace chars with highlighted span
            cut_highlighted_text = highlighted_text[group_start:group_end]
            group_id = f"text-{match_id}-group-{i}"
            group_class = f"match-{match_id}-group-{i}"
            start_str = f'<span id="{group_id}" class="group-highlight {group_class} color-{i}">'
            end_str = "</span>"
            if cut_highlighted_text:
                highlighted_text[group_start] = f"{start_str}{cut_highlighted_text[0]}"
                highlighted_text[group_end - 1] = f"{highlighted_text[group_end - 1]}{end_str}"

        return "".join(highlighted_text)


class MatchTableGenerator:
    """
    Generates HTML tables to display match results with optional groups, escaping HTML.
    """

    HEADER_NAMES = ("Group", "Index", "Name", "Match")
    MATCH_CONTAINER_START = '<div class="match-container">'
    MATCH_CONTAINER_END = "</div>"
    MATCH_TABLE_START = '<table class="match-table"><thead><tr>'
    MATCH_TABLE_HEADER_END = "</tr></thead><tbody><tr>"
    MATCH_TABLE_END = "</tr></tbody>"
    GROUP_TABLE_START = '<table class="group-table"><thead><tr>'
    GROUP_TABLE_HEADER_END = "</tr></thead><tbody>"
    GROUP_TABLE_END = "</tbody></table></div>"

    def generate_match_table(self, matches):
        """Generates the complete HTML table(s) for the given matches data."""
        tables = []
        for i, match_data in enumerate(matches, start=1):
            match_str = match_data.get("match")
            if match_str:
                match_id = i - 1
                table = [self._create_match_header(i)]
                if "groups" in match_data and match_data["groups"] and len(match_data["groups"]) > 0:
                    table.append(self._create_match_body(match_data, match_id))
                    table.append(self._create_group_header())
                    table.append(self._create_group_rows(match_data["groups"], match_id))
                    table.append(self.GROUP_TABLE_END)
                else:
                    table.append(self._create_match_body(match_data, match_id))
                    table.append(self.MATCH_CONTAINER_END)
                tables.append("".join(table))

        return "".join(tables)

    def _create_match_header(self, index):
        """Generates the header row for the main match table."""
        return (
            f"{self.MATCH_CONTAINER_START}{self.MATCH_TABLE_START}"
            f"<th>Nr</th>"
            f"<th>Index</th>"
            f"<th>Match</th>"
            f"{self.MATCH_TABLE_HEADER_END}"
            f"<td>{index}</td>"
            f"<td>"
        )

    def _create_match_body(self, match_data, match_id):
        """Generates the table row for the main match table."""

        tabel_id = f"tabel-{match_id}"
        tabel_class = f"match-{match_id}"
        index_start, index_end = match_data["index"]
        match_str = match_data.get("match")
        escaped_match_str = html.escape(match_str)
        table_content = (
            f"[{index_start}:{index_end}]</td>"
            f'<td><span id="{tabel_id}" class="match-main-highlight-tablet match-main-highlight {tabel_class}">'
            f"{escaped_match_str}</span></td>"
            f"{self.MATCH_TABLE_END}"
        )
        return table_content

    def _create_group_header(self):
        """Generates the header row for the group table."""
        group_header = f"{self.GROUP_TABLE_START}"
        for header in self.HEADER_NAMES:
            group_header += f"<th>{header}</th>"
        group_header += f"{self.GROUP_TABLE_HEADER_END}"
        return group_header

    @staticmethod
    def _create_group_rows(groups, match_id):
        """Generates the table rows for the match groups."""
        rows = []
        for j, group_info in enumerate(groups):
            group_str = group_info.get("value")
            if group_str:
                group_id = f"tabel-{match_id}-group-{j}"
                group_class = f"match-{match_id}-group-{j}"
                group_name = group_info.get("name")
                group_index_start, group_index_end = group_info["index"]
                escaped_group_str = html.escape(group_str)
                escaped_group_name = html.escape(group_name) if group_name else "-"
                rows.append(
                    f"<tr>"
                    f"<td>{j + 1}</td>"
                    f"<td>[{group_index_start}:{group_index_end}]</td>"
                    f"<td>{escaped_group_name}</td>"
                    f'<td><span id="{group_id}" class="match-table-highlight group-table-highlight {group_class} '
                    f'color-{j}">'
                    f"{escaped_group_str}</span></td>"
                    f"</tr>"
                )
        return "".join(rows)


class MatchHighlighterRegex:
    """
    Highlights the regex pattern.
    """

    def __init__(self):
        self.gray_color_counter = 0

    def highlight_regex(self, regex_pattern, number_of_colors):
        """Highlights the regex pattern."""
        self.gray_color_counter = number_of_colors
        pairs = self._generate_pair(regex_pattern)
        highlight_regex = self._generate_highlight_regex(pairs, regex_pattern)

        return highlight_regex

    def _generate_pair(self, regex_pattern):
        stack = []
        pairs = []
        current = ""
        for i, char in enumerate(regex_pattern):
            if f"{current}{char}" == r"\(" or f"{current}{char}" == r"\)":  # Skip escaped brackets
                current = ""
                continue
            if char == "(":
                stack.append(i)
            elif char == ")":
                if stack:
                    left_index = stack.pop()
                    pairs.append(
                        {
                            "string": regex_pattern[left_index : i + 1],  # noqa: E203
                            "index": (left_index, i),
                        }
                    )
            current = char
        pairs.sort(key=lambda x: x["index"][0])
        return pairs

    def _generate_highlight_regex(self, pairs, regex_pattern):
        highlight_regex = list(regex_pattern)
        highlight_regex = [html.escape(char) for char in highlight_regex]
        counter = 0
        for i, pair in enumerate(pairs):
            string = pair["string"]
            if string.startswith(r"(?:") and string.endswith(")"):
                highlight_regex[pair["index"][0]] = (
                    f'<span id="regex-match-left-{self.gray_color_counter + 1}" class="regex-highlight '
                    f'color-{self.gray_color_counter + 1}">{highlight_regex[pair["index"][0]]}</span>'
                )
                highlight_regex[pair["index"][1]] = (
                    f'<span id="regex-match-right-{self.gray_color_counter + 1}" class="regex-highlight '
                    f'color-{self.gray_color_counter + 1}">{highlight_regex[pair["index"][1]]}</span>'
                )
                self.gray_color_counter += 1
                continue
            highlight_regex[pair["index"][0]] = (
                f'<span id="regex-match-left-{counter}" class="regex-highlight '
                f'color-{counter}">{highlight_regex[pair["index"][0]]}</span>'
            )
            highlight_regex[pair["index"][1]] = (
                f'<span id="regex-match-right-{counter}" class="regex-highlight '
                f'color-{counter}">{highlight_regex[pair["index"][1]]}</span>'
            )
            counter += 1
        return "".join(highlight_regex)
