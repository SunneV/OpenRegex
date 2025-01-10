"""
This module provides utilities for generating colors, highlighting matches, and generating HTML tables.
"""

import html as html_lib


class ColorGenerator:
    """
    Generates distinct colors for light and dark themes based on the golden angle.
    """

    def __init__(self, division_factor=1):
        self.color_cache = {}
        golden_angle = 137.508  # Golden angle in degrees
        self.hue_step = golden_angle / division_factor
        self.light_theme_colors = {}
        self.dark_theme_colors = {}

    def generate_color(self, color_numbers):
        """Generates a list of distinct colors."""
        self.light_theme_colors = {}
        self.dark_theme_colors = {}
        for i in range(color_numbers):
            hue = (i * self.hue_step) % 360
            self.light_theme_colors[f"color-{i}"] = f"hsl({hue}, 70%, 70%)"
            self.dark_theme_colors[f"color-{i}"] = f"hsl({hue}, 50%, 30%)"


class MatchHighlighter:
    """
    Highlights matches in text, handling nested groups correctly and without overlaps.
    """

    def highlight_matches(self, text, matches):
        """Highlights matches, handling nested groups correctly and without overlaps."""
        if not matches:
            return html_lib.escape(text)

        parts = []
        last_match_end = 0

        for match_data in matches:
            main_start, main_end = match_data["index"]
            begin_text = html_lib.escape(text[last_match_end:main_start])
            parts.append(begin_text)
            match_text = text[main_start:main_end]

            highlighted_match = self._highlight_groups(match_text, match_data.get("groups", []), main_start)
            parts.append(f'<span class="match-highlight match-main-highlight">{highlighted_match}</span>')

            last_match_end = main_end
        last_text = html_lib.escape(text[last_match_end:])
        parts.append(last_text)
        final_str = "".join(parts)
        return final_str

    def _highlight_groups(self, match_text, groups, main_start):
        """Highlights groups, handling nesting correctly, sorted by length, keeping original order for colors."""
        if not groups:
            return match_text

        highlighted_text = list(match_text)  # Use a list for mutability
        highlighted_text = [html_lib.escape(char) for char in highlighted_text]
        # Sort groups by length while preserving original order and color assignment
        sorted_groups = self._sort_groups_by_length(groups)

        for group_info in sorted_groups:
            i = group_info["original_index"]
            group_str = group_info.get("value")
            if group_str and group_info.get("index"):
                group_start = group_info["index"][0] - main_start
                group_end = group_info["index"][1] - main_start

                # Replace chars with highlighted span
                cut_highlighted_text = highlighted_text[group_start:group_end]
                start_str = f'<span class="group-highlight color-{i}">'
                end_str = "</span>"
                highlighted_text[group_start] = f"{start_str}{cut_highlighted_text[0]}"
                highlighted_text[group_end - 1] = f"{highlighted_text[group_end - 1]}{end_str}"

        return "".join(highlighted_text)

    @staticmethod
    def _sort_groups_by_length(groups):
        """Sorts groups by length (shortest to longest), keeping original index."""
        indexed_groups = []
        for i, group in enumerate(groups):
            if group.get("value") and group.get("index"):
                indexed_groups.append({**group, "original_index": i})
        return sorted(indexed_groups, key=lambda x: (x["index"][1] - x["index"][0]))


class MatchTableGenerator:
    """
    Generates HTML tables to display match results with optional groups, escaping HTML.
    """

    HEADER_NAMES = ("Group", "Index", "Name", "Match")
    CELL_STYLES = [
        "width: 9%; text-align: center;",
        "width: 18%;",
        "width: 20%;",
        "width: 53%;",
    ]
    MATCH_CONTAINER_START = '<div class="match-container">'
    MATCH_TABLE_START = '<table class="match-table" style="width: 100%;"><thead><tr>'
    MATCH_TABLE_HEADER_END = "</tr></thead><tbody><tr>"
    MATCH_TABLE_END = "</tr></tbody></table>"
    GROUP_TABLE_START = '<table class="group-table" style="width: 100%;"><thead><tr>'
    GROUP_TABLE_HEADER_END = "</tr></thead><tbody>"
    GROUP_TABLE_END = "</tbody></table></div>"

    def _create_match_header(self, index):
        """Generates the header row for the main match table."""
        return (
            f"{self.MATCH_CONTAINER_START}{self.MATCH_TABLE_START}"
            f"<th>Nr</th>"
            f"<th>Index</th>"
            f"<th>Match</th>"
            f"{self.MATCH_TABLE_HEADER_END}"
            f'<td style="{self.CELL_STYLES[0]}">{index}</td>'
            f'<td style="{self.CELL_STYLES[1]}">'
        )

    def _create_match_body(self, match_data, has_groups=False):
        index_start, index_end = match_data["index"]
        match_str = match_data.get("match")
        escaped_match_str = html_lib.escape(match_str)
        table_content = (
            f"[{index_start}:{index_end}]</td>"
            f'<td class="match-main-highlight{" match-table-highlight" if has_groups else ""}">'
            f"{escaped_match_str}</td>"
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

    def _create_group_rows(self, groups):
        """Generates the table rows for the match groups."""
        group_rows = ""
        for j, group_info in enumerate(groups):
            group_str = group_info.get("value")
            if group_str:
                group_name = group_info.get("name")
                group_index_start, group_index_end = group_info["index"]
                escaped_group_str = html_lib.escape(group_str)
                escaped_group_name = html_lib.escape(group_name) if group_name else "-"
                group_rows += (
                    f'<tr><td style="{self.CELL_STYLES[0]}">{j + 1}</td><td style="{self.CELL_STYLES[1]}" >'
                    f"[{group_index_start}:{group_index_end}]</td>"
                    f'<td style="{self.CELL_STYLES[2]}">{escaped_group_name}</td>'
                    f'<td class="match-table-highlight group-table-highlight color-{j}"'
                    f' style="{self.CELL_STYLES[3]}">{escaped_group_str}</td></tr>'
                )
        return group_rows

    def generate_match_table(self, matches):
        """Generates the complete HTML table(s) for the given matches data."""
        tables = []
        for i, match_data in enumerate(matches, start=1):
            match_str = match_data.get("match")
            if match_str:
                table = self._create_match_header(i)
                if "groups" in match_data and match_data["groups"] and len(match_data["groups"]) > 0:
                    table += self._create_match_body(match_data, True)
                    table += self._create_group_header()
                    table += self._create_group_rows(match_data["groups"])
                    table += f"{self.GROUP_TABLE_END}"

                else:
                    table += self._create_match_body(match_data)
                    table += f'{self.MATCH_CONTAINER_START.replace("<div", "</div")}'
                tables.append(table)

        return "".join(tables)
