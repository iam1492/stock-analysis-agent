"""
LLM Model Configuration with Dynamic Firestore Integration

This module provides the lite_llm_model() function that dynamically retrieves
AI model configurations for agents from Firestore, with graceful fallback to
default models.
"""

import logging
from typing import Optional

from .firestore_config import FirestoreConfig

# Configure logging
logger = logging.getLogger(__name__)


def lite_llm_model(agent_name: Optional[str] = None) -> str:
    """
    Get the LLM model name for the specified agent.
    
    Retrieves model configuration from Firestore via FirestoreConfig service.
    Falls back to default model ('gemini-2.5-flash') if:
    - agent_name is not provided
    - Firestore is unavailable
    - Agent configuration not found
    
    Args:
        agent_name: Name of the agent requesting model configuration.
                   Should match document ID in Firestore 'stock_agents' collection.
                   Examples: 'balance_sheet_agent', 'hedge_fund_manager_agent'
    
    Returns:
        Model name string (e.g., 'gemini-2.5-flash', 'gemini-2.5-pro')
    
    Examples:
        >>> lite_llm_model('balance_sheet_agent')
        'gemini-2.5-flash'
        
        >>> lite_llm_model('hedge_fund_manager_agent')
        'gemini-2.5-pro'
        
        >>> lite_llm_model()  # No agent name provided
        'gemini-2.5-flash'  # Falls back to default
        
        >>> lite_llm_model('unknown_agent')
        'gemini-2.5-flash'  # Falls back to default with warning
    """
    # Backward compatibility: If no agent_name provided, use default
    if agent_name is None:
        logger.warning(
            "lite_llm_model() called without agent_name parameter. "
            f"Using default model '{FirestoreConfig.DEFAULT_MODEL}'. "
            "Please update agent creation to pass agent_name."
        )
        return FirestoreConfig.DEFAULT_MODEL
    
    # Get model from Firestore config service
    model = FirestoreConfig.get_model(agent_name)
    
    return model
