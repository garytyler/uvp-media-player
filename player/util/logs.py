import logging
import os

import vlc

try:
    import colorlog
except ImportError:
    color_available = False
else:
    color_available = True


def initialize_logging(level="INFO", color=color_available):
    vlc.logger.setLevel(0)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(get_formatter(color=color))
    file_handler = logging.FileHandler("player.log")
    file_handler.setFormatter(get_formatter(color=False))

    logger = logging.getLogger()
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.setLevel("INFO")
    logger.info(f"INIT LOGGING level={level} color={color}")

    # Set log levels
    log_levels = (i.split(":") for i in os.getenv("LOG_LEVELS", "").split(",") if i)
    for name, level in log_levels:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.info(f"SET LOGGER LOG LEVEL name={name} level={level}")


def get_formatter(color):
    if not color:
        return logging.Formatter(
            fmt=" ".join(
                [
                    "[{asctime:}]",
                    "{levelname:-<8}>",
                    "{message}",
                    "[{filename}:{lineno}({funcName})]",
                ]
            ),
            style="{",
        )
    return colorlog.ColoredFormatter(
        fmt=" ".join(
            [
                "{log_color}{reset}[{dim_log_color}{asctime:}{reset}]",
                "{emphasis_log_color}{levelname:-<8}{reset}>",
                "{primary_log_color}{message}{dim_log_color}",
                "[{filename}:{lineno}({funcName})]{reset}",
            ]
        ),
        style="{",
        reset=True,
        log_colors=ColorStyle.default,
        secondary_log_colors={
            "primary": ColorStyle.default,
            "emphasis": ColorStyle.strong,
            "dim": ColorStyle.dim,
        },
    )


class ColorStyle:
    default = {
        "DEBUG": "fg_cyan",
        "INFO": "fg_green",
        "WARNING": "fg_yellow",
        "ERROR": "fg_red",
        "CRITICAL": "fg_white,bg_red",
    }
    dim = {f: "fg_bold_black" for f in default.keys()}
    strong = {
        "DEBUG": "fg_bold_cyan",
        "INFO": "fg_bold_green",
        "WARNING": "fg_bold_yellow",
        "ERROR": "fg_red",
        "CRITICAL": "fg_bold_white,bg_red",
    }
    dull = {
        "DEBUG": "thin_cyan",
        "INFO": "thin_green",
        "WARNING": "thin_yellow",
        "ERROR": "thin_red",
        "CRITICAL": "fg_bold_white,bg_bold_red",
    }
