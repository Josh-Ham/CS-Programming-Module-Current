"""Logger module

Functions:
log_infomation -- logs infomation
log_warning -- logs a warning
log_error -- logs an error
"""
import logging

# Set up logging configeration
logging.basicConfig(
    filename='app.log',
    filemode='w',
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
    )

def log_infomation(infomation: str) -> None:
    """Log infomation to log file."""
    logging.info(infomation)

def log_warning(warning: str) -> None:
    """Log warning to the log file."""
    logging.warning(warning)

def log_error(error: str) -> None:
    """Log error to the log file."""
    logging.error(error)
