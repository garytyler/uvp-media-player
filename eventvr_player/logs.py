import logging
import logging.config
import os

try:
    from colorlog import ColoredFormatter
except ImportError:
    color_available = False
else:
    color_available = True


def initialize_logging(level="INFO", color=color_available):
    level = os.getenv("LOG_LEVEL", level)
    logger = logging.getLogger()
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(get_formatter(color))
    logger.addHandler(handler)
    logger.info(f"CONFIGURED DEFAULT LOGGING level={level}, color={color}")


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

    return ColoredFormatter(
        fmt=" ".join(
            [
                "{log_color}{no_log_color}[{dim_log_color}{asctime:}{no_log_color}]",
                "{emphasis_log_color}{levelname:-<8}{no_log_color}>",
                "{primary_log_color}{message}{dim_log_color}",
                "[{filename}:{lineno}({funcName})]{no_log_color}",
            ]
        ),
        style="{",
        reset=True,
        log_colors=get_color_style("default"),
        secondary_log_colors={
            "primary": get_color_style("default"),
            "emphasis": get_color_style("strong"),
            "dim": get_color_style("dim"),
            "no": get_color_style("no"),
        },
    )


def get_color_style(style):
    return {
        "default": {
            "DEBUG": "reset,fg_cyan",
            "INFO": "reset,fg_green",
            "WARNING": "reset,fg_yellow",
            "ERROR": "reset,fg_red",
            "CRITICAL": "reset,fg_white,bg_red",
        },
        "strong": {
            "DEBUG": "reset,fg_bold_cyan",
            "INFO": "reset,fg_bold_green",
            "WARNING": "reset,fg_bold_yellow",
            "ERROR": "reset,fg_red",
            "CRITICAL": "reset,fg_bold_white,bg_red",
        },
        "dull": {
            "DEBUG": "reset,thin_cyan",
            "INFO": "reset,thin_green",
            "WARNING": "reset,thin_yellow",
            "ERROR": "reset,thin_red",
            "CRITICAL": "reset,fg_bold_white,bg_bold_red",
        },
        "dim": {
            "DEBUG": "reset,fg_bold_black",
            "INFO": "reset,fg_bold_black",
            "WARNING": "reset,fg_bold_black",
            "ERROR": "reset,fg_bold_black",
            "CRITICAL": "reset,fg_bold_black",
        },
        "no": {
            "DEBUG": "reset",
            "INFO": "reset",
            "WARNING": "reset",
            "ERROR": "reset",
            "CRITICAL": "reset",
        },
    }
