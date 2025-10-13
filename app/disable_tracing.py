#!/usr/bin/env python3
"""
Disable OpenTelemetry tracing before any imports
This file should be imported first to ensure tracing is disabled
"""
import os
import sys

# Disable all OpenTelemetry tracing before any imports
tracing_env_vars = [
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

for var in tracing_env_vars:
    os.environ[var] = "none" if var != "OTEL_SDK_DISABLED" else "true"

# Additional aggressive disabling
os.environ["OTEL_PYTHON_DISABLED_INSTRUMENTATIONS"] = "opentelemetry.instrumentation.auto_instrumentation,opentelemetry.instrumentation.urllib3,opentelemetry.instrumentation.requests,opentelemetry.instrumentation.httpx,opentelemetry.instrumentation.asyncpg,opentelemetry.instrumentation.redis,opentelemetry.instrumentation.elasticsearch"

# Disable context propagation
os.environ["OTEL_PROPAGATORS"] = "none"

print("🚫 OpenTelemetry tracing disabled at process startup")