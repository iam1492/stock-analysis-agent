"""
Firestore Configuration Service for Dynamic Model and Instruction Management

This module provides centralized Firestore client initialization and
agent model configuration management with caching and fallback support.
Extended to support shared instructions for all agents.
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
    Centralized model and instruction configuration service.
    
    Loads agent-to-model mappings and shared instructions from Firestore at startup
    and caches them in memory for fast O(1) lookups. Provides graceful fallback
    to default model/instruction if Firestore is unavailable or config is missing.
    """
    
    # Configuration cache: {agent_name: model_name}
    _cache: Dict[str, str] = {}
    
    # Loaded state flag
    _loaded: bool = False
    
    # Default model for fallback
    DEFAULT_MODEL: str = "gemini-2.5-flash"
    
    # Default shared instruction for fallback
    DEFAULT_SHARED_INSTRUCTION: str = "우리는 세계 최고의 금융회사다."
    
    # Firestore collection names
    AGENTS_COLLECTION_NAME: str = "stock_agents"
    COMPANY_COLLECTION_NAME: str = "stock_agent_company"
    
    # Document IDs
    SHARED_INSTRUCTION_DOC_ID: str = "shared_instruction"
    
    # Loading timeout (seconds)
    TIMEOUT: int = 5

    @classmethod
    def load_configs(cls) -> None:
        """
        Load all agent model configurations and shared instructions from Firestore.
        
        This should be called once at application startup, before any agents
        are created. Configurations are cached in memory for O(1) access.
        
        If Firestore is unavailable or loading fails, logs a warning and
        continues with empty cache (fallback to defaults).
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
                    f"Using default model '{cls.DEFAULT_MODEL}' and shared instruction for all agents."
                )
                cls._loaded = True
                return
            
            # Load agent model configurations
            logger.info(
                f"📥 Loading agent configurations from Firestore "
                f"collection '{cls.AGENTS_COLLECTION_NAME}'..."
            )
            
            # Query all documents in stock_agents collection
            docs = client.collection(cls.AGENTS_COLLECTION_NAME).stream(timeout=cls.TIMEOUT)
            
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
            
            # Load shared instruction
            logger.info(
                f"📥 Loading shared instruction from Firestore "
                f"collection '{cls.COMPANY_COLLECTION_NAME}' → '{cls.SHARED_INSTRUCTION_DOC_ID}'..."
            )
            
            try:
                shared_doc = client.collection(cls.COMPANY_COLLECTION_NAME).document(cls.SHARED_INSTRUCTION_DOC_ID).get(timeout=cls.TIMEOUT)
                if shared_doc.exists:
                    shared_data = shared_doc.to_dict()
                    if shared_data and 'description' in shared_data:
                        cls._cache[cls.SHARED_INSTRUCTION_DOC_ID] = shared_data['description']
                        logger.info("✅ Successfully loaded shared instruction from Firestore")
                    else:
                        cls._cache[cls.SHARED_INSTRUCTION_DOC_ID] = cls.DEFAULT_SHARED_INSTRUCTION
                        logger.warning(
                            f"⚠️  Shared instruction document missing 'shared_instruction' field. "
                            f"Using default instruction."
                        )
                else:
                    logger.warning(
                        f"⚠️  Shared instruction document not found. "
                        f"Using default instruction."
                    )
            except Exception as e:
                logger.error(f"❌ Failed to load shared instruction: {e}")
                logger.warning("⚠️  Using default shared instruction.")
            
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
                "and shared instruction for all agents."
            )
            cls._loaded = True  # Prevent retry loop
            
    @classmethod
    def get_shared_instruction(cls) -> str:
        """get the shared instructions from firestore or cache.

        Returns:
            str: shared instruction
        """
        if not cls._loaded:
            # Load 
            cls.load_configs()
        
        if cls.SHARED_INSTRUCTION_DOC_ID in cls._cache:
            shared_instruction = cls._cache[cls.SHARED_INSTRUCTION_DOC_ID]
            logger.debug(
                    f"🎯 Shared Instruction: {shared_instruction}"
                )
            return shared_instruction
        
        logger.debug(f"🎯 Shared Instruction not loaded")
        return cls.DEFAULT_SHARED_INSTRUCTION
            
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
            # Load 
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