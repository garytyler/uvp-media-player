import logging
import os

import vlc

log = logging.getLogger()


def initialize_logging():
    # Set vlc log level
    vlc.logger.setLevel(0)

    # Setup local logger
    logger = logging.getLogger()
    logger.addHandler(logging.FileHandler("player.log"))
    logger.info(f"INIT LOGGING")

    # Set local log levels
    log_levels = (i.split(":") for i in os.getenv("LOG_LEVELS", "").split(",") if i)
    for name, level in log_levels:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.info(f"SET LOGGER LOG LEVEL name={name} level={level}")
