"""
This module initializes the application by setting up the environment, configuration, and logging.
"""

from project.environments import _App, _Config, _Path
from project.log import _log

Path = _Path()
Config = _Config()
App = _App()
log = _log(name=App.name, level=Config.log_level)
log.info(f"{App.name} {App.version} started logging at {Config.log_level} level")
log.setLevel(Config.log_level)
