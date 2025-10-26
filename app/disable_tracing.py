#!/usr/bin/env python3
"""
Centralized OpenTelemetry Tracing Configuration

This module provides comprehensive control over OpenTelemetry tracing settings.
Import this module FIRST in any entry point to ensure consistent tracing behavior.

Features:
- Centralized environment variable management
- Development vs production mode handling
- Aggressive tracing disable for problematic scenarios
- Context propagation control
"""

import os
import sys
import logging
from typing import Dict, List, Optional


class TracingConfig:
    """Centralized configuration for OpenTelemetry tracing."""

    # Core tracing disable variables
    TRACING_DISABLE_VARS = [
        "OTEL_SDK_DISABLED",
        "OTEL_TRACES_EXPORTER",
        "OTEL_METRICS_EXPORTER",
        "OTEL_LOGS_EXPORTER",
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
        "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
        "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT",
        "OTEL_RESOURCE_ATTRIBUTES",
        "OTEL_SERVICE_NAME",
        "OTEL_EXPORTER_JAEGER_ENDPOINT",
        "OTEL_EXPORTER_ZIPKIN_ENDPOINT",
        "OTEL_EXPORTER_PROMETHEUS_ENDPOINT",
        "OTEL_PYTHON_DISABLED_INSTRUMENTATIONS"
    ]

    # Additional context and propagation control
    CONTEXT_VARS = [
        "OTEL_PROPAGATORS",
        "OTEL_PYTHON_CONTEXT",
        "OTEL_PYTHON_CONTEXT_PROVIDERS"
    ]

    # Instrumentation libraries to disable
    DISABLED_INSTRUMENTATIONS = [
        "opentelemetry.instrumentation.auto_instrumentation",
        "opentelemetry.instrumentation.urllib3",
        "opentelemetry.instrumentation.requests",
        "opentelemetry.instrumentation.httpx",
        "opentelemetry.instrumentation.asyncpg",
        "opentelemetry.instrumentation.redis",
        "opentelemetry.instrumentation.elasticsearch",
        "opentelemetry.instrumentation.google_genai",
        "opentelemetry.instrumentation.fastapi",
        "opentelemetry.instrumentation.starlette"
    ]

    def __init__(self, disable_tracing: bool = True, development_mode: bool = True):
        """
        Initialize tracing configuration.

        Args:
            disable_tracing: Whether to completely disable OpenTelemetry tracing
            development_mode: Whether running in development (more aggressive disabling)
        """
        self.disable_tracing = disable_tracing
        self.development_mode = development_mode
        self.logger = logging.getLogger(__name__)

    def apply_configuration(self) -> None:
        """Apply the tracing configuration to environment variables."""
        if self.disable_tracing:
            self._disable_all_tracing()
            if self.development_mode:
                self._apply_aggressive_disable()
        else:
            self._enable_selective_tracing()

        self._configure_context_propagation()
        self._configure_logging()

    def _disable_all_tracing(self) -> None:
        """Disable all OpenTelemetry tracing components."""
        for var in self.TRACING_DISABLE_VARS:
            if var == "OTEL_SDK_DISABLED":
                os.environ[var] = "true"
            elif var == "OTEL_PYTHON_DISABLED_INSTRUMENTATIONS":
                os.environ[var] = ",".join(self.DISABLED_INSTRUMENTATIONS)
            else:
                os.environ[var] = "none"

        # Additional aggressive disable for context issues
        os.environ["OTEL_PYTHON_CONTEXT"] = "none"
        os.environ["OTEL_PROPAGATORS"] = "none"
        os.environ["OTEL_BSP_SCHEDULE_DELAY"] = "0"
        os.environ["OTEL_BSP_MAX_EXPORT_BATCH_SIZE"] = "0"
        os.environ["OTEL_BSP_MAX_QUEUE_SIZE"] = "0"

    def _apply_aggressive_disable(self) -> None:
        """Apply additional aggressive disabling for development environments."""
        # Force disable any remaining OTEL components
        aggressive_vars = [
            "OTEL_TRACES_SAMPLER",
            "OTEL_TRACES_SAMPLER_ARG",
            "OTEL_METRICS_EXPORTER",
            "OTEL_LOGS_EXPORTER",
            "OTEL_EXPORTER_CONSOLE_ENDPOINT",
            "OTEL_EXPORTER_CONSOLE_PROTOCOL",
            "OTEL_EXPORTER_CONSOLE_TRACES_ENDPOINT",
            "OTEL_EXPORTER_CONSOLE_METRICS_ENDPOINT",
            "OTEL_EXPORTER_CONSOLE_LOGS_ENDPOINT",
            "OTEL_EXPORTER_OTLP_COMPRESSION",
            "OTEL_EXPORTER_OTLP_HEADERS",
            "OTEL_EXPORTER_OTLP_TIMEOUT",
            "OTEL_EXPORTER_OTLP_PROTOCOL",
            "OTEL_EXPORTER_OTLP_INSECURE",
            "OTEL_EXPORTER_OTLP_CERTIFICATE",
            "OTEL_EXPORTER_OTLP_CLIENT_KEY",
            "OTEL_EXPORTER_OTLP_CLIENT_CERTIFICATE",
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
            "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT",
            "OTEL_EXPORTER_JAEGER_ENDPOINT",
            "OTEL_EXPORTER_JAEGER_USER",
            "OTEL_EXPORTER_JAEGER_PASSWORD",
            "OTEL_EXPORTER_ZIPKIN_ENDPOINT",
            "OTEL_EXPORTER_PROMETHEUS_ENDPOINT",
            "OTEL_EXPORTER_PROMETHEUS_HOST",
            "OTEL_EXPORTER_PROMETHEUS_PORT",
            "OTEL_RESOURCE_ATTRIBUTES",
            "OTEL_SERVICE_NAME",
            "OTEL_SERVICE_NAMESPACE",
            "OTEL_SERVICE_INSTANCE_ID",
            "OTEL_SERVICE_VERSION",
            "OTEL_LIBRARY_INFO_ENABLED",
            "OTEL_DISABLE_TELEMETRY",
            "OTEL_TELEMETRY_SDK_DISABLED",
            "OTEL_PYTHON_ID_GENERATOR",
            "OTEL_PYTHON_FAILED_REQUEST_ATTRIBUTE_COUNT",
            "OTEL_PYTHON_SUCCESSFUL_REQUEST_ATTRIBUTE_COUNT",
            "OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED",
            "OTEL_PYTHON_LOGGING_CORRELATION",
            "OTEL_PYTHON_LOGGING_INCLUDE_TRACING_CONTEXT",
            "OTEL_PYTHON_LOGGING_EXCLUDE_URLS",
            "OTEL_PYTHON_LOGGING_LOG_LEVEL",
            "OTEL_PYTHON_LOGGING_CAPTURE_HEADERS_SERVER_REQUEST",
            "OTEL_PYTHON_LOGGING_CAPTURE_HEADERS_SERVER_RESPONSE",
            "OTEL_PYTHON_LOGGING_CAPTURE_HEADERS_CLIENT_REQUEST",
            "OTEL_PYTHON_LOGGING_CAPTURE_HEADERS_CLIENT_RESPONSE",
        ]

        for var in aggressive_vars:
            os.environ[var] = "none"

        # Ensure SDK is completely disabled
        os.environ["OTEL_SDK_DISABLED"] = "true"
        os.environ["OTEL_DISABLE_TELEMETRY"] = "true"
        os.environ["OTEL_TELEMETRY_SDK_DISABLED"] = "true"

    def _enable_selective_tracing(self) -> None:
        """Enable selective tracing for production use."""
        # Only disable problematic instrumentations
        os.environ["OTEL_PYTHON_DISABLED_INSTRUMENTATIONS"] = ",".join([
            "opentelemetry.instrumentation.fastapi",
            "opentelemetry.instrumentation.starlette"
        ])

        # Keep other tracing enabled but with console exporter for debugging
        os.environ["OTEL_TRACES_EXPORTER"] = "console"
        os.environ["OTEL_METRICS_EXPORTER"] = "none"
        os.environ["OTEL_LOGS_EXPORTER"] = "none"

        # Add safe context management for production
        os.environ["OTEL_PYTHON_CONTEXT"] = "contextvars_context"
        os.environ["OTEL_PROPAGATORS"] = "tracecontext,baggage"

    def _configure_context_propagation(self) -> None:
        """Configure OpenTelemetry context propagation."""
        if self.disable_tracing:
            os.environ["OTEL_PROPAGATORS"] = "none"
            os.environ["OTEL_PYTHON_CONTEXT"] = "none"
        else:
            os.environ["OTEL_PROPAGATORS"] = "tracecontext,baggage"

    def _configure_logging(self) -> None:
        """Configure logging levels for OpenTelemetry components."""
        # Reduce OTEL logging noise
        logging.getLogger("opentelemetry").setLevel(logging.WARNING)
        logging.getLogger("opentelemetry.context").setLevel(logging.ERROR)
        logging.getLogger("opentelemetry.trace").setLevel(logging.WARNING)

    def get_status(self) -> Dict[str, str]:
        """Get current tracing configuration status."""
        return {
            "tracing_disabled": str(self.disable_tracing),
            "development_mode": str(self.development_mode),
            "otel_sdk_disabled": os.environ.get("OTEL_SDK_DISABLED", "not_set"),
            "otel_traces_exporter": os.environ.get("OTEL_TRACES_EXPORTER", "not_set"),
            "otel_propagators": os.environ.get("OTEL_PROPAGATORS", "not_set")
        }


def disable_tracing_aggressively() -> None:
    """
    Convenience function to disable tracing aggressively.
    Use this in development or when experiencing OTEL context issues.
    """
    # Force disable before any OTEL imports
    os.environ["OTEL_SDK_DISABLED"] = "true"
    os.environ["OTEL_DISABLE_TELEMETRY"] = "true"
    os.environ["OTEL_TELEMETRY_SDK_DISABLED"] = "true"
    os.environ["OTEL_PYTHON_DISABLED_INSTRUMENTATIONS"] = "opentelemetry.instrumentation.auto_instrumentation,opentelemetry.instrumentation.urllib3,opentelemetry.instrumentation.requests,opentelemetry.instrumentation.httpx,opentelemetry.instrumentation.asyncpg,opentelemetry.instrumentation.redis,opentelemetry.instrumentation.elasticsearch,opentelemetry.instrumentation.google_genai,opentelemetry.instrumentation.fastapi,opentelemetry.instrumentation.starlette"
    os.environ["OTEL_PYTHON_CONTEXT"] = "none"
    os.environ["OTEL_PROPAGATORS"] = "none"

    config = TracingConfig(disable_tracing=True, development_mode=True)
    config.apply_configuration()
    print("[DISABLED] OpenTelemetry tracing aggressively disabled")


def disable_tracing_selective() -> None:
    """
    Convenience function to disable tracing selectively.
    Keeps some tracing for debugging but disables problematic components.
    """
    config = TracingConfig(disable_tracing=True, development_mode=False)
    config.apply_configuration()
    print("[SELECTIVE] OpenTelemetry tracing selectively disabled")


def enable_tracing_for_production() -> None:
    """
    Enable tracing for production use with minimal overhead.
    """
    config = TracingConfig(disable_tracing=False, development_mode=False)
    config.apply_configuration()
    print("[ENABLED] OpenTelemetry tracing enabled for production with safe context management")


# Auto-apply configuration based on environment
def auto_configure_tracing() -> None:
    """
    Automatically configure tracing based on environment variables and context.
    Priority order:
    1. FORCE_DISABLE_OTEL=true -> aggressive disable
    2. OTEL_SDK_DISABLED=true -> selective disable
    3. Development mode (default) -> aggressive disable
    4. Production mode -> selective tracing
    """
    # Always disable tracing aggressively due to persistent context issues
    # This is a temporary measure until the root cause is fully resolved
    disable_tracing_aggressively()
    return

    # Check for explicit disable flags
    if os.environ.get("FORCE_DISABLE_OTEL", "").lower() == "true":
        disable_tracing_aggressively()
        return

    if os.environ.get("OTEL_SDK_DISABLED", "").lower() == "true":
        disable_tracing_selective()
        return

    # Auto-detect environment
    development_indicators = [
        os.environ.get("PYTHON_ENV") == "development",
        os.environ.get("ENV") == "dev",
        "dev" in sys.argv[0].lower(),
        not os.environ.get("GOOGLE_CLOUD_PROJECT"),  # No GCP project = likely dev
    ]

    if any(development_indicators):
        disable_tracing_aggressively()
    else:
        # For production-like environments, use selective tracing with safe context management
        disable_tracing_selective()


# Apply configuration on import
auto_configure_tracing()

# Also set up environment manager
from .tracing_env import setup_tracing_environment
setup_tracing_environment()