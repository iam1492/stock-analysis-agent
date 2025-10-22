"""
Logging Configuration for ADK Agent Engine

This module provides centralized logging configuration with appropriate
levels for OpenTelemetry and other components to reduce noise.
"""

import logging
import os
import sys
from typing import Dict, Optional


class LoggingConfig:
    """
    Centralized logging configuration for the ADK application.

    This class manages logging levels for different components,
    especially OpenTelemetry components that can be verbose.
    """

    # Default logging levels for different components
    DEFAULT_LEVELS = {
        # OpenTelemetry components - reduce noise
        "opentelemetry": logging.WARNING,
        "opentelemetry.context": logging.ERROR,
        "opentelemetry.trace": logging.WARNING,
        "opentelemetry.sdk": logging.WARNING,
        "opentelemetry.exporter": logging.WARNING,
        "opentelemetry.instrumentation": logging.WARNING,

        # Google Cloud components
        "google.cloud": logging.WARNING,
        "google.auth": logging.WARNING,
        "vertexai": logging.WARNING,

        # ADK components
        "google.adk": logging.INFO,
        "app": logging.INFO,

        # FastAPI and Starlette
        "fastapi": logging.WARNING,
        "starlette": logging.WARNING,
        "uvicorn": logging.WARNING,

        # Root logger
        "": logging.INFO,
    }

    # Environment variable mappings
    ENV_LEVELS = {
        "LOG_LEVEL": "",  # Root logger
        "OTEL_LOG_LEVEL": "opentelemetry",
        "ADK_LOG_LEVEL": "google.adk",
        "FASTAPI_LOG_LEVEL": "fastapi",
        "UVICORN_LOG_LEVEL": "uvicorn",
    }

    def __init__(self):
        self._configured = False
        self._custom_levels = {}

    def set_level(self, logger_name: str, level: int) -> None:
        """Set logging level for a specific logger."""
        self._custom_levels[logger_name] = level
        if self._configured:
            logging.getLogger(logger_name).setLevel(level)

    def get_level(self, logger_name: str) -> int:
        """Get the current logging level for a logger."""
        logger = logging.getLogger(logger_name)
        return logger.level

    def configure_logging(self, log_level: Optional[int] = None) -> None:
        """
        Configure logging for the application.

        Args:
            log_level: Override root log level (optional)
        """
        # Set up basic configuration if not already done
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(
                level=log_level or self._get_default_root_level(),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                stream=sys.stdout
            )

        # Apply default levels
        for logger_name, level in self.DEFAULT_LEVELS.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)

        # Apply environment variable overrides
        self._apply_env_overrides()

        # Apply custom levels
        for logger_name, level in self._custom_levels.items():
            logging.getLogger(logger_name).setLevel(level)

        self._configured = True

        # Log configuration summary in debug mode
        if self._is_debug_mode():
            self._log_configuration_summary()

    def _get_default_root_level(self) -> int:
        """Get the default root logging level."""
        # Check environment variable
        env_level = os.environ.get("LOG_LEVEL", "").upper()
        if env_level:
            return getattr(logging, env_level, logging.INFO)

        # Auto-detect based on environment
        if self._is_development_mode():
            return logging.DEBUG
        elif self._is_testing_mode():
            return logging.DEBUG
        else:
            return logging.INFO

    def _apply_env_overrides(self) -> None:
        """Apply logging level overrides from environment variables."""
        for env_var, logger_name in self.ENV_LEVELS.items():
            level_str = os.environ.get(env_var, "").upper()
            if level_str:
                try:
                    level = getattr(logging, level_str)
                    logging.getLogger(logger_name).setLevel(level)
                except AttributeError:
                    print(f"Warning: Invalid log level '{level_str}' for {env_var}")

    def _is_development_mode(self) -> bool:
        """Check if running in development mode."""
        indicators = [
            os.environ.get("PYTHON_ENV") == "development",
            os.environ.get("ENV") == "dev",
            "dev" in os.getcwd().lower(),
            not os.environ.get("GOOGLE_CLOUD_PROJECT"),
        ]
        return any(indicators)

    def _is_testing_mode(self) -> bool:
        """Check if running in testing mode."""
        return os.environ.get("CI", "").lower() == "true" or "test" in sys.argv[0].lower()

    def _is_debug_mode(self) -> bool:
        """Check if debug logging should be enabled."""
        return self._is_development_mode() or self._is_testing_mode()

    def _log_configuration_summary(self) -> None:
        """Log a summary of the current logging configuration."""
        print("[LOGGING] Configuration Summary:")
        print(f"  Root Level: {logging.getLogger().level}")
        print("  Component Levels:")

        for logger_name in sorted(self.DEFAULT_LEVELS.keys()):
            if logger_name:  # Skip root logger
                level = logging.getLogger(logger_name).level
                level_name = logging.getLevelName(level)
                print(f"    {logger_name}: {level_name}")

    def silence_ot_warnings(self) -> None:
        """Specifically silence OpenTelemetry warnings and errors."""
        ot_loggers = [
            "opentelemetry",
            "opentelemetry.context",
            "opentelemetry.trace",
            "opentelemetry.sdk.trace",
            "opentelemetry.sdk.trace.export",
        ]

        for logger_name in ot_loggers:
            logging.getLogger(logger_name).setLevel(logging.ERROR)

    def enable_ot_debug(self) -> None:
        """Enable debug logging for OpenTelemetry (for troubleshooting)."""
        ot_loggers = [
            "opentelemetry",
            "opentelemetry.context",
            "opentelemetry.trace",
            "opentelemetry.sdk",
        ]

        for logger_name in ot_loggers:
            logging.getLogger(logger_name).setLevel(logging.DEBUG)


# Global instance
logging_config = LoggingConfig()


def setup_logging(log_level: Optional[int] = None) -> None:
    """
    Set up logging for the ADK application.

    This function should be called early in the application lifecycle.
    """
    logging_config.configure_logging(log_level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


if __name__ == "__main__":
    # Allow running as a script for testing
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Logging configuration test")
    logger.debug("Debug message")
    logger.warning("Warning message")