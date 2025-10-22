# Import centralized tracing configuration first
from .disable_tracing import TracingConfig

# Initialize tracing configuration
tracing_config = TracingConfig()
tracing_config.apply_configuration()

# Set up logging configuration
from .logging_config import setup_logging
setup_logging()

from . import agent