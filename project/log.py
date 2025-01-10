"""
This module provides logging functionality with custom formatting and colors.
"""

import logging
from dataclasses import dataclass

import colorlog

default_config = {
    "timer": True,
    "app_name": True,
    "thread": True,
    "error_level": True,
    "message": True,
    "filename": False,
}


@dataclass
class MESSAGE:
    """
    Class for defining log_handler message formats.
    """

    timer = "[%(asctime)s]"
    app_name = "[%(name)s]"
    thread = "[%(threadName)s]"
    error_level = "[%(levelname)-8s]"
    message = "%(message)s"
    filename = "[%(filename)s:%(lineno)d]"


@dataclass
class COLOR:
    """
    Class for defining log_handler colors.
    """

    white = "\x1b[1;1m"
    white_bright = "\x1b[1;97m"
    blue = "\x1b[36;20m"
    yellow = "\x1b[1;33m"
    violet = "\x1b[1;35m"
    green = "\x1b[1;32m"
    red = "\x1b[31;20m"
    pink = "\x1b[95m"
    bold_red = "\x1b[31;1m"
    gray = "\x1b[38;5;240m"
    light_gray = "\x1b[38;5;244m"
    light_gray_bold = "\x1b[38;5;244m\x1b[1m"
    reset = "\x1b[0m"


def get_formatter(config):
    """
    Returns a colorlog.ColoredFormatter with the specified configuration.
    """
    message_parts = {
        f"{COLOR.light_gray}{MESSAGE.timer}": config["timer"],
        "%(log_color)s" + f"{MESSAGE.error_level}": config["error_level"],
        f"{COLOR.green}{MESSAGE.app_name}": config["app_name"],
        f"{COLOR.violet}{MESSAGE.thread}": config["thread"],
        f"{COLOR.white_bright}: {MESSAGE.message} ": config["message"],
        f"{MESSAGE.filename}": config["filename"],
    }
    message = "".join([key for key, value in message_parts.items() if value])

    return colorlog.ColoredFormatter(
        message,
        datefmt="%Y-%m-%d %H:%M:%S",  # Use '%X' for the locale’s appropriate time representation
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "white",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "light_white,bg_red",
        },
        secondary_log_colors={},
        style="%",
    )


def _log(name, level, config=None):
    """
    Configures and returns a logger with the specified name and level.

    Args:
        name (str): The name of the logger.
        level (str): The logging level (e.g., 'DEBUG', 'INFO').
        config (dict, optional): Configuration for the log message format.

    Returns:
        logging.Logger: Configured logger instance.
    """
    if config is None:
        config = default_config
    if level == "DEBUG":
        config["filename"] = True
    formatter = get_formatter(config)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logging.getLogger(name)
