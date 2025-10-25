# utils/logger.py
import logging
import os

def get_logger(name="SudokuSolver", log_file=None, level=logging.INFO):
    """
    Create or get a logger instance.
    Outputs to console and (optionally) to a file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:  # avoid duplicate handlers
        formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s", "%H:%M:%S")
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger
