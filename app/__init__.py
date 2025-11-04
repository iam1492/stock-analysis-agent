"""Stock Analysis Agent Application Package"""

# Set up logging configuration
from .logging_config import setup_logging
setup_logging()

# Import main agent module
from . import agent

__all__ = ["agent"]