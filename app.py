# pylint: disable=R0801

"""
This module initializes and runs the Flask application for regex matching.
"""

import html

from flask import Flask, jsonify, render_template, request, send_from_directory

from project import App, Config, log
from src.engine_manager import EngineManager
from src.utils.interface import ColorGenerator, MatchHighlighterRegex, MatchHighlighterText, MatchTableGenerator
from src.utils.link import decode_dict, encode_dict


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
        self.app.add_url_rule("/get_decode_link", methods=["POST"], view_func=self.decode_link)
        self.app.add_url_rule("/robots.txt", methods=["GET"], view_func=self.robots_txt)
        self.app.add_url_rule("/favicon.ico", methods=["GET"], view_func=self.favicon)

    def robots_txt(self):
        """
        Serves the robots.txt file.
        """
        return send_from_directory(
            self.app.static_folder, "robots_disallow.txt" if Config.debug else "robots_allow.txt"
        )

    def favicon(self):
        """
        Serves the favicon.ico file.
        """
        return send_from_directory(self.app.static_folder, "favicon.svg", mimetype="image/svg+xml")

    def _process_regex(self, regex_pattern, input_text, selected_engine):
        """
        Processes the regex matching and returns the results.  This is the
        core logic, extracted for reuse.  Returns a dictionary suitable for
        either jsonify or render_template.
        """
        data = {"r": regex_pattern, "t": input_text, "e": selected_engine}
        encode_data = encode_dict(data)

        if not regex_pattern or not input_text:
            return {
                "error": "",
                "highlighted_text": html.escape(input_text) if input_text else "",
                "highlighted_regex": html.escape(regex_pattern) if regex_pattern else "",
                "selected_engine": selected_engine,
                "matches_table": "",
                "execution_time": "Engine: N/A",
                "dark_theme_color": {},
                "light_theme_color": {},
                "encode_data": encode_data,
            }

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

        return {
            "error": error,
            "selected_engine": selected_engine,
            "matches_table": matches_table,
            "highlighted_text": highlighted_text,
            "highlighted_regex": highlighted_regex,
            "execution_time": self.execution_time(execution_time),
            "dark_theme_color": self.color_generator.dark_theme_colors,
            "light_theme_color": self.color_generator.light_theme_colors,
            "encode_data": encode_data,
        }

    def _render_index(self, context_data=None):
        """Renders the index.html template with provided context or defaults."""
        default_context = {
            "app_name": App.name,
            "app_link": App.home_link,
            "app_description": App.description,
            "app_debug_mode": App.debug_info,
            "app_author": App.author,
            "app_linkedin": App.linkedin,
            "app_repository": App.repository,
            "app_version": App.version,
            "app_release_date": App.release_date,
            "app_docker_link": App.docker_link,
            "engines": self.engine_manager.get_engine_list(),
            "execution_time": self.execution_time(0),
            "dark_theme_color": {},
            "light_theme_color": {},
        }

        # Update the default context with any provided data
        if context_data:
            default_context.update(context_data)

        return render_template("index.html", **default_context)

    def index(self):
        """Handles the main page requests."""
        if request.method == "POST":
            regex_pattern = request.json["regex_input"]
            input_text = request.json["text_input"]
            selected_engine = request.json.get("engine", "")
            result = self._process_regex(regex_pattern, input_text, selected_engine)
            return jsonify(result)  # AJAX response

        return self._render_index()  # Default GET request

    def get_engine_info(self):
        """Returns information about the selected regex engine."""
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
        """Returns the example regex and text."""
        selected_engine = request.json.get("engine", None)
        engine = self.engine_manager.get_engine(selected_engine)
        if engine:  # Check if engine is valid
            return jsonify(engine.regex_examples)
        else:
            return jsonify({"error": "Invalid engine selected."})

    @staticmethod
    def decode_link():
        """Decodes the encoded link data and returns it as JSON."""
        encoded_data = request.json.get("encoded_data")
        if not encoded_data:
            return jsonify({"error": "No encoded data provided."}), 400  # Return a 400 Bad Request

        try:
            data = decode_dict(encoded_data)
            return jsonify(data)
        except Exception as e:
            log.error(f"Error decoding link data: {e}")
            return jsonify({"error": "Invalid encoded data."}), 400  # Return a 400 Bad Request

    @staticmethod
    def execution_time(execution_time: float) -> str:
        """Converts execution time to a string in milliseconds."""
        return f"Engine: {int(execution_time * 1000)}ms"

    @staticmethod
    def get_number_of_colors(matches):
        """Returns the number of colors needed for the matches group."""
        return max((len(match.get("groups", [])) for match in matches), default=0)

    def run(self, debug=Config.debug, port=Config.port, use_reloader=True):
        """Runs the Flask application."""
        self.app.run(debug=debug, port=port, use_reloader=use_reloader)


app = RegexMatcherApp().app

if __name__ == "__main__":
    log.warning("Running the Flask development mode")
    app.run(debug=Config.debug, port=Config.port, use_reloader=False)
