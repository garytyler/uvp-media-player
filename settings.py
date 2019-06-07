import logging
import logging.config
import os
from pathlib import Path  # python3 only

from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path, verbose=True)


logging_color_styles = {
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
    "uncolored": {
        "DEBUG": "reset",
        "INFO": "reset",
        "WARNING": "reset",
        "ERROR": "reset",
        "CRITICAL": "reset",
    },
}


logging_format_string = "{log_color}{reset_log_color}[{dim_log_color}{asctime:}{reset_log_color}]{emphasis_log_color}{levelname:·<8}{reset_log_color}❯{primary_log_color}{message}{dim_log_color}[{filename}:{lineno}({funcName})]{reset_log_color}"


logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored_applogs_formatter": {
                "()": "colorlog.ColoredFormatter",
                "style": "{",
                "format": logging_format_string,
                "log_colors": logging_color_styles["default"],
                "secondary_log_colors": {
                    "primary": logging_color_styles["default"],
                    "emphasis": logging_color_styles["strong"],
                    "dim": logging_color_styles["dim"],
                    "reset": logging_color_styles["uncolored"],
                },
            }
        },
        "handlers": {
            "colored_applogs_console": {
                "formatter": "colored_applogs_formatter",
                "class": "logging.StreamHandler",
            }
        },
        "loggers": {
            "eventvr_player": {
                "handlers": ["colored_applogs_console"],
                "level": os.getenv("LOG_LEVEL", "INFO"),
            }
        },
    }
)
