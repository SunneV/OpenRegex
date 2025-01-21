# pylint: disable=R0801

"""
This module initializes and runs the Flask application for regex matching.
"""

import html

from flask import Flask, jsonify, render_template, request, send_from_directory

from project import App, Config, log
from src.engine_manager import EngineManager
from src.utils.interface import ColorGenerator, MatchHighlighterRegex, MatchHighlighterText, MatchTableGenerator


class RegexMatcherApp:
    """
    A Flask application for regex matching using various regex engines.
    """

    def __init__(self):
        self.app = Flask(__name__)
        self.engine_manager = EngineManager()
        self.color_generator = ColorGenerator(division_factor=4)
        self.match_highlighter_text = MatchHighlighterText()
        self.match_highlighter_regex = MatchHighlighterRegex()
        self.match_table_generator = MatchTableGenerator()

        self.app.add_url_rule("/", methods=["GET", "POST"], view_func=self.index)
        self.app.add_url_rule("/get_engine_info", methods=["POST"], view_func=self.get_engine_info)
        self.app.add_url_rule("/get_example_regex", methods=["POST"], view_func=self.get_example_regex)
        self.app.add_url_rule("/robots.txt", methods=["GET"], view_func=self.robots_txt)

    def robots_txt(self):
        """
        Serves the robots.txt file.
        """
        if Config.debug:
            return send_from_directory(self.app.static_folder, "robots_disallow.txt")
        return send_from_directory(self.app.static_folder, "robots_allow.txt")

    def index(self):
        """
        Handles the main page requests, processes regex matching, and returns the results.
        """
        if request.method == "POST":
            regex_pattern = request.json["regex_input"]
            input_text = request.json["text_input"]
            selected_engine = request.json.get("engine", None)

            if not regex_pattern or not input_text:
                response_data = {
                    "error": "",
                    "highlighted_text": html.escape(input_text) if input_text else "",
                    "highlighted_regex": html.escape(regex_pattern) if regex_pattern else "",
                    "selected_engine": selected_engine,
                    "matches_table": "",
                    "execution_time": "Engine: N/A",
                    "dark_theme_color": {},
                    "light_theme_color": {},
                }
                return jsonify(response_data)

            matches, error, execution_time = self.engine_manager.match(selected_engine, regex_pattern, input_text)
            number_of_colors = self.get_number_of_colors(matches)
            self.color_generator.generate_color(number_of_colors)
            matches_table = self.match_table_generator.generate_match_table(matches)
            highlighted_text = self.match_highlighter_text.highlight_matches(input_text, matches)
            highlighted_regex = self.match_highlighter_regex.highlight_regex(regex_pattern, number_of_colors)
            self.color_generator.generate_gray_color(
                number_of_colors, number_of_colors + self.match_highlighter_regex.gray_color_counter
            )
            if error:
                highlighted_text = html.escape(error)
                highlighted_regex = html.escape(regex_pattern)
            return jsonify(
                {
                    "error": error,
                    "selected_engine": selected_engine,
                    "matches_table": matches_table,
                    "highlighted_text": highlighted_text,
                    "highlighted_regex": highlighted_regex,
                    "execution_time": self.execution_time(execution_time),
                    "dark_theme_color": self.color_generator.dark_theme_colors,
                    "light_theme_color": self.color_generator.light_theme_colors,
                }
            )

        # Get the list of engines
        engines = self.engine_manager.get_engine_list()

        return render_template(
            "index.html",
            app_name=App.name,
            app_link=App.home_link,
            app_description=App.description,
            app_debug_mode=App.debug_info,
            app_author=App.author,
            app_linkedin=App.linkedin,
            app_repository=App.repository,
            app_version=App.version,
            app_release_date=App.release_date,
            app_docker_link=App.docker_link,
            engines=engines,
            execution_time=self.execution_time(0),
            dark_theme_color={},
            light_theme_color={},
        )

    def get_engine_info(self):
        """
        Returns information about the selected regex engine.
        """
        selected_engine = request.json.get("engine", None)
        engine = self.engine_manager.get_engine(selected_engine)
        if not engine:
            return jsonify({"error": "Invalid engine name."})
        return jsonify(
            {
                "selected_engine": selected_engine,
                "engine_version": engine.version,
                "cheat_sheet": engine.regex_cheat_sheet,
            }
        )

    def get_example_regex(self):
        """
        Returns the example regex and text.
        """
        selected_engine = request.json.get("engine", None)
        engine = self.engine_manager.get_engine(selected_engine)
        return jsonify(engine.regex_examples)

    @staticmethod
    def execution_time(execution_time: float) -> str:
        """
        Converts execution time to a string in milliseconds.
        """
        return f"Engine: {int(execution_time * 1000)}ms"  # Convert to milliseconds

    @staticmethod
    def get_number_of_colors(matches):
        """
        Returns the number of colors needed for the matches group.
        """
        return max((len(match.get("groups", [])) for match in matches), default=0)

    def run(self, debug=Config.debug, port=Config.port, use_reloader=True):
        """
        Runs the Flask application.
        """
        self.app.run(debug=debug, port=port, use_reloader=use_reloader)


app = RegexMatcherApp().app

if __name__ == "__main__":
    log.warning("Running the Flask development mode")
    app.run(debug=Config.debug, port=Config.port, use_reloader=False)
