"""Stock Analysis Agent Application Package"""

# Set up logging configuration
from .logging_config import setup_logging
setup_logging()

# Load Firestore configurations before importing agents
# This ensures model configurations are ready when agents are created
from .sub_agents.utils.firestore_config import FirestoreConfig
FirestoreConfig.load_configs()

# Import main agent module
from . import agent

__all__ = ["agent"]