import logging
import os

log = logging.getLogger()


def initialize_logging():
    # Set player log file
    player_log_file = os.getenv("VR_PLAYER_LOG_FILE", None)
    if player_log_file:
        dirpath, filename = os.path.split(player_log_file)
        if dirpath:
            os.makedirs(os.path.dirname(dirpath), exist_ok=True)
        logger = logging.getLogger()
        logger.addHandler(logging.FileHandler(player_log_file))
        logger.info(f"INIT LOGGING")

    # Set player log levels
    player_log_levels = os.getenv("VR_PLAYER_LOG_LEVELS", "")
    for name, level in (i.split(":") for i in player_log_levels.split(",") if i):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.info(f"SET LOGGER LOG LEVEL name={name} level={level}")
