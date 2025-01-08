# pylint: disable=R0801

"""
This module initializes and runs the Flask application for regex matching.
"""

import html as html_lib

from flask import Flask, jsonify, render_template, request

from project import App, Config
from src.engine_manager import EngineManager
from src.utils.html import ColorGenerator, MatchHighlighter, MatchTableGenerator


class RegexMatcherApp:
    """
    A Flask application for regex matching using various regex engines.
    """

    def __init__(self):
        self.app = Flask(__name__)
        self.engine_manager = EngineManager()
        self.color_generator = ColorGenerator(division_factor=4)
        self.match_highlighter = MatchHighlighter()
        self.match_table_generator = MatchTableGenerator()

        self.app.add_url_rule("/", methods=["GET", "POST"], view_func=self.index)
        self.app.add_url_rule("/get_engine_info", methods=["POST"], view_func=self.get_engine_info)

    def index(self):
        """
        Handles the main page requests, processes regex matching, and returns the results.
        """
        if request.method == "POST":
            regex_pattern = request.json["regex_input"]
            input_text = request.json["text_input"]
            selected_engine = request.json.get("engine", None)

            if not regex_pattern or not input_text:
                return jsonify({"error": "", "highlighted_text": html_lib.escape(input_text)})

            matches, error, execution_time = self.engine_manager.match(selected_engine, regex_pattern, input_text)
            number_of_colors = self.get_number_of_colors(matches)
            self.color_generator.generate_color(number_of_colors)
            matches_table = self.match_table_generator.generate_match_table(matches)
            highlighted_text = self.match_highlighter.highlight_matches(input_text, matches)
            if error:
                highlighted_text = html_lib.escape(error)
            return jsonify(
                {
                    "matches": matches_table,
                    "error": error,
                    "selected_engine": selected_engine,
                    "highlighted_text": highlighted_text,
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
            app_description=App.description,
            app_author=App.author,
            app_linkedin=App.linkedin,
            app_repository=App.repository,
            app_version=App.version,
            app_release_date=App.release_date,
            engines=engines,
            python_version=App.python_version,
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
        return jsonify({"selected_engine": selected_engine, "engine_version": engine.version})

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
    app.run(debug=Config.debug, port=Config.port, use_reloader=False)
