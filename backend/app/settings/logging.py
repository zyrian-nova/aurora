"""
Logging configuration for backend
"""
import sys
import logging
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class ColoredFormatter(logging.Formatter):
    """Custom formatter with readable colors."""
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m',     # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Add colors to log level names."""
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname:8}"
                f"{self.COLORS['RESET']}"
            )
        return super().format(record)

# Aurora specific logger customization
class AuroraLogger:
    """Centralized logging manager for Aurora."""

    def __init__(
        self,
        name: str = "aurora",
        log_dir: Optional[Path] = None,
        level: str = "INFO",
        enable_file_logging: bool = True,
    ) -> None:
        self.name = name
        self.log_dir = log_dir or Path("logs")
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.enable_file_logging = enable_file_logging
        # Ensure log directory exists
        if self.enable_file_logging:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Configure and return the main logger."""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        logger.propagate = False

        # Clear existing handlers (prevents duplicates)
        logger.handlers.clear()

        # Console handler (always enabled)
        logger.addHandler(self._get_console_handler())
        if self.enable_file_logging:
            # General application logs
            logger.addHandler(self._get_file_handler())
            # Error only logs
            logger.addHandler(self._get_error_handler())
        return logger

    def _get_console_handler(self) -> logging.Handler:
        """Create colored console handler for development."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self.level)

        # Use colored formatter in dev, plain in production
        if settings.ENVIRONMENT == "development":
            formatter = ColoredFormatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:&M:%S"
            )
        else:
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:&M:%S"
            )

        handler.setFormatter(formatter)
        return handler

    def _get_file_handler(self) -> logging.Handler:
        """Create rotating file handler for general logs."""
        log_file = self.log_dir / "aurora.log"

        # Rotate when file reaches 10MB, keeps 5 backups
        handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=10 * 1024 * 1024, # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        handler.setLevel(self.level)

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s - %(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        return handler

    def _get_error_handler(self) -> logging.Handler:
        """Create a daily rotating handler for error logs only."""
        log_file = self.log_dir / "errors.log"

        # Rotate daily, keep 30 days of error logs
        handler = TimedRotatingFileHandler(
            filename=log_file,
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        handler.setLevel(logging.ERROR)

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s - %(pathname)s:%(lineno)d\n"
                "%(message)s\n"
                "Exception: %(exc_info)s\n",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        return handler

    def get_logger(self) -> logging.Logger:
        """Return the configured logger instance."""
        return self.logger

# Global logger setup
def setup_logging(
    level: Optional[str] = None,
    enable_file_logging: bool = True # Maybe making it an ENV variable later
) -> logging.Logger:
    """Initialize and return the global Aurora logger."""
    log_level = level or settings.LOG_LEVEL

    aurora_logger = AuroraLogger(
        name="aurora",
        log_dir=Path("logs"),
        level=log_level,
        enable_file_logging=enable_file_logging
    )

    # Set up uvicorn's logger to match
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(getattr(logging, log_level.upper()))
