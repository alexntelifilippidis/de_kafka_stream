import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with color codes and emojis for terminal output.
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
        'GRAY': '\033[90m',       # Gray for date/time
        'BLUE': '\033[34m',       # Blue for time
        'CYAN': '\033[96m',       # Light cyan for module name
    }

    # Emoji mappings
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥'
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with colors and emojis.

        Args:
            record: Log record to format

        Returns:
            Formatted log string with colors
        """
        # Get colors
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        gray = self.COLORS['GRAY']
        blue = self.COLORS['BLUE']
        cyan = self.COLORS['CYAN']

        # Get emoji
        emoji = self.EMOJIS.get(record.levelname, '')

        # Format timestamp components
        timestamp = self.formatTime(record, self.datefmt)
        date_part, time_part = timestamp.split(' ')

        # Build colored output
        formatted_msg = (
            f"{gray}{date_part}{reset} "
            f"{blue}{time_part}{reset} - "
            f"{level_color}{emoji} {record.levelname}{reset} - "
            f"{cyan}{record.name}{reset} - "
            f"{level_color}{record.getMessage()}{reset}"
        )

        return formatted_msg


def _get_log_level(level: str) -> int:
    """
    Convert string log level to logging constant.

    Args:
        level: Log level as string (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Logging level constant

    Raises:
        ValueError: If invalid log level provided
    """
    level_mapping = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    level_upper = level.upper()
    if level_upper not in level_mapping:
        raise ValueError(
            f"Invalid log level: {level}. "
            f"Must be one of: {', '.join(level_mapping.keys())}"
        )

    return level_mapping[level_upper]


def setup_logger(
    name: str,
    level: str = 'INFO',
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with colored console output and optional file output.

    Args:
        name: Logger name (typically __name__)
        level: Logging level as string (default: 'INFO')
        log_file: Optional file path for file logging

    Returns:
        Configured logger instance

    Raises:
        ValueError: If invalid log level provided
    """
    log_level = _get_log_level(level)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Optional file handler without colors
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str, level: str = 'INFO') -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name (typically __name__)
        level: Logging level as string (default: 'INFO')

    Returns:
        Logger instance

    Raises:
        ValueError: If invalid log level provided
    """
    return setup_logger(name, level)
