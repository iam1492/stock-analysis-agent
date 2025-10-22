"""
Environment Variable Management for Tracing Configuration

This module provides utilities for managing tracing-related environment variables
across different deployment scenarios and ensures consistent configuration.
"""

import os
from typing import Dict, List, Optional, Union


class TracingEnvironmentManager:
    """
    Manages tracing-related environment variables with priority and validation.

    This class provides a centralized way to manage all tracing configuration
    through environment variables, with support for different deployment modes.
    """

    # Environment variable names and their descriptions
    ENV_VARS = {
        # Core tracing control
        "FORCE_DISABLE_OTEL": "Force disable all OpenTelemetry tracing",
        "OTEL_SDK_DISABLED": "Disable OpenTelemetry SDK",
        "ENABLE_OTEL_TRACING": "Enable OpenTelemetry tracing (overrides disable)",

        # Tracing exporters
        "OTEL_TRACES_EXPORTER": "Trace exporter (console, otlp, none)",
        "OTEL_METRICS_EXPORTER": "Metrics exporter",
        "OTEL_LOGS_EXPORTER": "Logs exporter",

        # OTLP endpoints
        "OTEL_EXPORTER_OTLP_ENDPOINT": "OTLP endpoint",
        "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT": "OTLP traces endpoint",
        "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "OTLP metrics endpoint",
        "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT": "OTLP logs endpoint",

        # Resource and service identification
        "OTEL_RESOURCE_ATTRIBUTES": "Resource attributes",
        "OTEL_SERVICE_NAME": "Service name",

        # Sampling and filtering
        "OTEL_TRACES_SAMPLER": "Trace sampler",
        "OTEL_TRACES_SAMPLER_ARG": "Trace sampler argument",

        # Instrumentation control
        "OTEL_PYTHON_DISABLED_INSTRUMENTATIONS": "Disabled instrumentations",
        "OTEL_PYTHON_CONTEXT": "Context provider",
        "OTEL_PROPAGATORS": "Context propagators",

        # Cloud-specific settings
        "OTEL_EXPORTER_JAEGER_ENDPOINT": "Jaeger endpoint",
        "OTEL_EXPORTER_ZIPKIN_ENDPOINT": "Zipkin endpoint",
        "OTEL_EXPORTER_PROMETHEUS_ENDPOINT": "Prometheus endpoint",

        # Custom ADK settings
        "ADK_TRACING_MODE": "ADK-specific tracing mode (aggressive, selective, production)",
        "ADK_DISABLE_FASTAPI_INSTRUMENTATION": "Disable FastAPI instrumentation",
        "ADK_DISABLE_STARLETTE_INSTRUMENTATION": "Disable Starlette instrumentation",
    }

    # Default values for different modes
    DEFAULTS = {
        "development": {
            "FORCE_DISABLE_OTEL": "true",
            "OTEL_SDK_DISABLED": "true",
            "OTEL_TRACES_EXPORTER": "none",
            "OTEL_METRICS_EXPORTER": "none",
            "OTEL_LOGS_EXPORTER": "none",
            "OTEL_PROPAGATORS": "none",
            "ADK_TRACING_MODE": "aggressive",
        },
        "production": {
            "OTEL_SDK_DISABLED": "false",
            "OTEL_TRACES_EXPORTER": "otlp",
            "OTEL_METRICS_EXPORTER": "none",
            "OTEL_LOGS_EXPORTER": "none",
            "OTEL_PROPAGATORS": "tracecontext,baggage",
            "ADK_TRACING_MODE": "production",
        },
        "testing": {
            "FORCE_DISABLE_OTEL": "true",
            "OTEL_SDK_DISABLED": "true",
            "ADK_TRACING_MODE": "aggressive",
        }
    }

    def __init__(self):
        self._env_cache = {}
        self._mode = self._detect_mode()

    def _detect_mode(self) -> str:
        """Detect the current deployment mode."""
        # Check explicit mode setting
        mode = os.environ.get("ADK_DEPLOYMENT_MODE", "").lower()
        if mode in self.DEFAULTS:
            return mode

        # Auto-detect based on environment
        if os.environ.get("CI", "").lower() == "true":
            return "testing"
        if os.environ.get("GOOGLE_CLOUD_PROJECT"):
            return "production"
        if os.environ.get("PYTHON_ENV") == "development" or "dev" in os.getcwd().lower():
            return "development"

        return "development"  # Default fallback

    def get_mode(self) -> str:
        """Get the current deployment mode."""
        return self._mode

    def set_mode(self, mode: str) -> None:
        """Set the deployment mode."""
        if mode not in self.DEFAULTS:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {list(self.DEFAULTS.keys())}")
        self._mode = mode

    def apply_defaults_for_mode(self) -> None:
        """Apply default environment variables for the current mode."""
        defaults = self.DEFAULTS.get(self._mode, self.DEFAULTS["development"])

        for key, value in defaults.items():
            if key not in os.environ:  # Don't override explicit settings
                os.environ[key] = value

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get an environment variable value."""
        return os.environ.get(key, default)

    def set(self, key: str, value: Union[str, bool, int]) -> None:
        """Set an environment variable."""
        if isinstance(value, bool):
            value = "true" if value else "false"
        elif isinstance(value, int):
            value = str(value)

        os.environ[key] = value
        self._env_cache[key] = value

    def is_tracing_enabled(self) -> bool:
        """Check if tracing is enabled."""
        # Check explicit disable flags first
        if self.get("FORCE_DISABLE_OTEL", "").lower() == "true":
            return False
        if self.get("OTEL_SDK_DISABLED", "").lower() == "true":
            return False

        # Check explicit enable flag
        if self.get("ENABLE_OTEL_TRACING", "").lower() == "true":
            return True

        # Check based on mode
        return self._mode == "production"

    def get_tracing_config(self) -> Dict[str, str]:
        """Get all tracing-related environment variables."""
        config = {}
        for key in self.ENV_VARS:
            value = self.get(key)
            if value is not None:
                config[key] = value
        return config

    def validate_config(self) -> List[str]:
        """Validate the current tracing configuration."""
        issues = []

        # Check for conflicting settings
        if self.get("FORCE_DISABLE_OTEL") == "true" and self.get("ENABLE_OTEL_TRACING") == "true":
            issues.append("FORCE_DISABLE_OTEL and ENABLE_OTEL_TRACING are both set")

        if self.get("OTEL_SDK_DISABLED") == "true" and self.get("ENABLE_OTEL_TRACING") == "true":
            issues.append("OTEL_SDK_DISABLED is true but ENABLE_OTEL_TRACING is also true")

        # Check for invalid exporter combinations
        traces_exporter = self.get("OTEL_TRACES_EXPORTER", "").lower()
        if traces_exporter not in ["", "none", "console", "otlp", "jaeger", "zipkin"]:
            issues.append(f"Invalid OTEL_TRACES_EXPORTER: {traces_exporter}")

        # Check OTLP endpoint configuration
        if traces_exporter == "otlp":
            if not self.get("OTEL_EXPORTER_OTLP_ENDPOINT") and not self.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"):
                issues.append("OTLP exporter configured but no endpoint specified")

        return issues

    def print_config_summary(self) -> None:
        """Print a summary of the current tracing configuration."""
        print(f"[TRACING] Configuration Summary (Mode: {self._mode})")
        print(f"  Tracing Enabled: {self.is_tracing_enabled()}")

        config = self.get_tracing_config()
        if config:
            print("  Active Configuration:")
            for key, value in sorted(config.items()):
                print(f"    {key}: {value}")
        else:
            print("  No tracing configuration set")

        issues = self.validate_config()
        if issues:
            print("  [WARNING] Configuration Issues:")
            for issue in issues:
                print(f"    - {issue}")

    def reset_to_defaults(self) -> None:
        """Reset all tracing environment variables to mode defaults."""
        # Clear existing tracing vars
        for key in self.ENV_VARS:
            if key in os.environ:
                del os.environ[key]

        # Apply defaults for current mode
        self.apply_defaults_for_mode()


# Global instance
tracing_env = TracingEnvironmentManager()


def setup_tracing_environment() -> None:
    """
    Set up the tracing environment for the application.

    This function should be called early in the application lifecycle,
    before any OpenTelemetry imports or initialization.
    """
    tracing_env.apply_defaults_for_mode()

    # Print configuration in development mode
    if tracing_env.get_mode() == "development":
        tracing_env.print_config_summary()


if __name__ == "__main__":
    # Allow running as a script for testing
    setup_tracing_environment()