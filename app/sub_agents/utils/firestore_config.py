"""
Firestore Configuration Service for Dynamic Model Management

This module provides centralized Firestore client initialization and
agent model configuration management with caching and fallback support.
"""

import logging
import os
from typing import Dict, Optional

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_client import BaseClient

# Configure logging
logger = logging.getLogger(__name__)


class FirestoreClient:
    """
    Singleton Firestore client manager.
    
    Ensures only one Firebase app and Firestore client instance is created
    throughout the application lifecycle.
    """
    
    _instance: Optional[BaseClient] = None
    _initialized: bool = False
    
    @classmethod
    def get_client(cls) -> Optional[BaseClient]:
        """
        Get or create the Firestore client instance.
        
        Returns:
            Firestore client instance, or None if initialization fails.
        """
        if cls._initialized:
            return cls._instance
            
        try:
            # Load credentials path from environment
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            project_id = os.getenv('FIREBASE_PROJECT_ID')
            
            if not cred_path:
                logger.warning(
                    "FIREBASE_CREDENTIALS_PATH not set. "
                    "Firestore will not be available."
                )
                cls._initialized = True
                return None
            
            if not os.path.exists(cred_path):
                logger.error(
                    f"Firebase credentials file not found: {cred_path}"
                )
                cls._initialized = True
                return None
            
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(cred_path)
            
            # Initialize app with project ID if provided
            if project_id:
                firebase_admin.initialize_app(cred, {
                    'projectId': project_id
                })
            else:
                firebase_admin.initialize_app(cred)
            
            # Get Firestore client
            cls._instance = firestore.client()
            cls._initialized = True
            
            logger.info(
                "✅ Successfully initialized Firestore client "
                f"(Project: {project_id or 'default'})"
            )
            
            return cls._instance
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firestore client: {e}")
            cls._initialized = True  # Prevent retry loop
            return None


class FirestoreConfig:
    """
    Centralized model configuration service.
    
    Loads agent-to-model mappings from Firestore at startup and caches them
    in memory for fast O(1) lookups. Provides graceful fallback to default
    model if Firestore is unavailable or agent config is missing.
    """
    
    # Configuration cache: {agent_name: model_name}
    _cache: Dict[str, str] = {}
    
    # Loaded state flag
    _loaded: bool = False
    
    # Default model for fallback
    DEFAULT_MODEL: str = "gemini-2.5-flash"
    
    # Firestore collection name
    COLLECTION_NAME: str = "stock_agents"
    
    # Loading timeout (seconds)
    TIMEOUT: int = 5
    
    @classmethod
    def load_configs(cls) -> None:
        """
        Load all agent model configurations from Firestore.
        
        This should be called once at application startup, before any agents
        are created. Configurations are cached in memory for O(1) access.
        
        If Firestore is unavailable or loading fails, logs a warning and
        continues with empty cache (fallback to default models).
        """
        if cls._loaded:
            logger.debug("Firestore configs already loaded, skipping")
            return
        
        try:
            # Get Firestore client
            client = FirestoreClient.get_client()
            
            if client is None:
                logger.warning(
                    "⚠️  Firestore client not available. "
                    f"Using default model '{cls.DEFAULT_MODEL}' for all agents."
                )
                cls._loaded = True
                return
            
            # Load configurations from Firestore
            logger.info(
                f"📥 Loading agent configurations from Firestore "
                f"collection '{cls.COLLECTION_NAME}'..."
            )
            
            # Query all documents in stock_agents collection
            docs = client.collection(cls.COLLECTION_NAME).stream(timeout=cls.TIMEOUT)
            
            loaded_count = 0
            for doc in docs:
                agent_name = doc.id
                data = doc.to_dict()
                
                if data and 'llm_model' in data:
                    model_name = data['llm_model']
                    cls._cache[agent_name] = model_name
                    loaded_count += 1
                    logger.debug(
                        f"  ✓ {agent_name} → {model_name}"
                    )
                else:
                    logger.warning(
                        f"  ⚠️  {agent_name}: missing 'llm_model' field"
                    )
            
            cls._loaded = True
            
            if loaded_count > 0:
                logger.info(
                    f"✅ Successfully loaded {loaded_count} agent "
                    f"configuration(s) from Firestore"
                )
            else:
                logger.warning(
                    "⚠️  No agent configurations found in Firestore. "
                    f"Using default model '{cls.DEFAULT_MODEL}' for all agents."
                )
                
        except Exception as e:
            logger.error(
                f"❌ Failed to load Firestore configurations: {e}"
            )
            logger.warning(
                f"⚠️  Falling back to default model '{cls.DEFAULT_MODEL}' "
                "for all agents."
            )
            cls._loaded = True  # Prevent retry loop
    
    @classmethod
    def get_model(cls, agent_name: str) -> str:
        """
        Get the model name for a specific agent.
        
        Performs O(1) dictionary lookup in cached configurations. If agent
        is not found or configs not loaded, returns default model.
        
        Args:
            agent_name: Name of the agent (e.g., 'balance_sheet_agent')
        
        Returns:
            Model name string (e.g., 'gemini-2.5-flash')
        """
        # Ensure configs are loaded (idempotent)
        if not cls._loaded:
            cls.load_configs()
        
        # Lookup in cache
        if agent_name in cls._cache:
            model = cls._cache[agent_name]
            logger.debug(
                f"🎯 Agent '{agent_name}' using model '{model}'"
            )
            return model
        
        # Fallback to default
        logger.debug(
            f"⚠️  Agent '{agent_name}' not found in config, "
            f"using default model '{cls.DEFAULT_MODEL}'"
        )
        return cls.DEFAULT_MODEL
    
    @classmethod
    def get_all_configs(cls) -> Dict[str, str]:
        """
        Get all cached agent model configurations.
        
        Returns:
            Dictionary mapping agent names to model names
        """
        if not cls._loaded:
            cls.load_configs()
        return cls._cache.copy()
    
    @classmethod
    def reload_configs(cls) -> None:
        """
        Force reload of configurations from Firestore.
        
        Clears cache and reloads all configurations. Useful for
        hot-reloading configurations without restarting the service
        (future enhancement).
        """
        logger.info("🔄 Reloading Firestore configurations...")
        cls._cache.clear()
        cls._loaded = False
        cls.load_configs()