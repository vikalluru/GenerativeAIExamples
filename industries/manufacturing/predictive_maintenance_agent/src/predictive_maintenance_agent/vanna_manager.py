"""
VannaManager - A comprehensive manager for Vanna instances to prevent vector store contamination
"""
import os
import logging
import threading
import time
from typing import Dict, Optional
from .vanna_util import NIMVanna, initVanna, CustomEmbeddingFunction

logger = logging.getLogger(__name__)

class VannaManager:
    """
    A singleton manager for Vanna instances that prevents vector store contamination.
    
    Key features:
    - Singleton pattern to ensure only one instance per configuration
    - Thread-safe operations
    - Automatic cleanup and reset capabilities
    - Strict isolation between production and initialization modes
    - Contamination detection and prevention
    """
    
    _instances: Dict[str, 'VannaManager'] = {}
    _lock = threading.Lock()
    
    def __new__(cls, config_key: str):
        """Ensure singleton pattern per configuration"""
        with cls._lock:
            if config_key not in cls._instances:
                cls._instances[config_key] = super().__new__(cls)
                cls._instances[config_key]._initialized = False
            return cls._instances[config_key]
    
    def __init__(self, config_key: str):
        """Initialize the VannaManager"""
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.config_key = config_key
        self.vanna_instance = None
        self.last_reset_time = time.time()
        self.query_count = 0
        self.contamination_threshold = 50  # Reset after 50 queries to prevent contamination
        self.lock = threading.Lock()
        self._initialized = True
        
        logger.info(f"VannaManager initialized for config: {config_key}")
    
    def get_instance(self, vanna_llm_config, vanna_embedder_config, vector_store_path: str, db_path: str) -> NIMVanna:
        """
        Get a clean Vanna instance, creating or resetting as needed.
        """
        with self.lock:
            # Check if we need to reset due to contamination threshold
            if (self.vanna_instance is not None and 
                self.query_count >= self.contamination_threshold):
                logger.warning(f"VannaManager: Contamination threshold reached ({self.query_count} queries). Resetting instance.")
                self._reset_instance()
            
            # Create new instance if needed
            if self.vanna_instance is None:
                self.vanna_instance = self._create_clean_instance(
                    vanna_llm_config, vanna_embedder_config, vector_store_path, db_path
                )
                self.query_count = 0
                self.last_reset_time = time.time()
            
            return self.vanna_instance
    
    def _create_clean_instance(self, vanna_llm_config, vanna_embedder_config, vector_store_path: str, db_path: str) -> NIMVanna:
        """
        Create a clean Vanna instance with proper isolation.
        """
        logger.info(f"VannaManager: Creating clean instance for {self.config_key}")
        
        # Create instance with contamination prevention
        vn_instance = ContaminationPreventionVanna(
            VectorConfig={
                "client": "persistent",
                "path": vector_store_path,
                "embedding_function": CustomEmbeddingFunction(
                    api_key=os.getenv("NVIDIA_API_KEY"), 
                    model=vanna_embedder_config.model_name)
            },
            LLMConfig={
                "api_key": os.getenv("NVIDIA_API_KEY"),
                "model": vanna_llm_config.model_name
            }
        )
        
        # Connect to database
        vn_instance.connect_to_sqlite(db_path)
        
        # Set critical configuration
        vn_instance.allow_llm_to_see_data = True
        vn_instance.disable_auto_training()
        
        # Initialize if needed
        list_of_folders = [d for d in os.listdir(vector_store_path) 
                          if os.path.isdir(os.path.join(vector_store_path, d))]
        if len(list_of_folders) == 0:
            logger.info("VannaManager: Initializing vector store...")
            vn_instance.enable_auto_training()
            try:
                initVanna(vn_instance)
                logger.info("VannaManager: Vector store initialization complete")
            except Exception as e:
                logger.error(f"VannaManager: Error during initialization: {e}")
                raise
            finally:
                vn_instance.disable_auto_training()
        
        logger.info(f"VannaManager: Clean instance created with ID: {id(vn_instance)}")
        return vn_instance
    
    def generate_sql_safe(self, question: str) -> str:
        """
        Generate SQL with contamination prevention and error handling.
        """
        with self.lock:
            if self.vanna_instance is None:
                raise RuntimeError("VannaManager: No instance available")
            
            # Increment query count for contamination tracking
            self.query_count += 1
            
            # Ensure clean state before generation
            self.vanna_instance.allow_llm_to_see_data = True
            self.vanna_instance.disable_auto_training()
            
            try:
                logger.info(f"VannaManager: Generating SQL for query #{self.query_count}")
                sql = self.vanna_instance.generate_sql(question=question)
                
                # Validate SQL response
                if not sql or sql.strip() == "":
                    raise ValueError("Empty SQL response")
                
                # Check for contamination indicators
                if self._is_contaminated_response(sql):
                    logger.warning(f"VannaManager: Contaminated response detected: {sql}")
                    self._reset_instance()
                    raise ValueError("Contaminated response detected - instance reset")
                
                return sql
                
            except Exception as e:
                logger.error(f"VannaManager: Error in SQL generation: {e}")
                # Reset on repeated errors to prevent cascade failures
                if self.query_count % 10 == 0:
                    logger.warning("VannaManager: Resetting instance due to repeated errors")
                    self._reset_instance()
                raise
    
    def _is_contaminated_response(self, sql: str) -> bool:
        """
        Detect contamination indicators in SQL response.
        """
        contamination_indicators = [
            "not allowed to see the data",
            "database introspection",
            "Error:",
            "Cannot generate",
            "Unable to process",
            "Invalid request",
            "{'",  # JSON-like responses
            "[object Object]",
            "undefined",
            "null"
        ]
        
        for indicator in contamination_indicators:
            if indicator in sql:
                return True
        
        return False
    
    def _reset_instance(self):
        """
        Reset the Vanna instance to prevent contamination.
        """
        logger.info(f"VannaManager: Resetting instance for {self.config_key}")
        if self.vanna_instance:
            try:
                # Clean up current instance
                self.vanna_instance = None
            except Exception as e:
                logger.warning(f"VannaManager: Error during instance cleanup: {e}")
        
        self.query_count = 0
        self.last_reset_time = time.time()
    
    def force_reset(self):
        """
        Force reset the instance (useful for external cleanup).
        """
        with self.lock:
            self._reset_instance()
    
    def get_stats(self) -> Dict:
        """
        Get manager statistics.
        """
        return {
            "config_key": self.config_key,
            "query_count": self.query_count,
            "last_reset_time": self.last_reset_time,
            "instance_id": id(self.vanna_instance) if self.vanna_instance else None,
            "contamination_threshold": self.contamination_threshold
        }

class ContaminationPreventionVanna(NIMVanna):
    """
    Enhanced NIMVanna with strict contamination prevention.
    """
    
    def __init__(self, VectorConfig=None, LLMConfig=None):
        super().__init__(VectorConfig, LLMConfig)
        self._strict_mode = True
        self._blocked_train_attempts = 0
        
    def train(self, question: str = None, sql: str = None, ddl: str = None, documentation: str = None, **kwargs):
        """
        Override train method with strict contamination prevention.
        """
        if self._strict_mode and not getattr(self, '_auto_train_enabled', False):
            self._blocked_train_attempts += 1
            logger.warning(f"ContaminationPreventionVanna: Blocked training attempt #{self._blocked_train_attempts}")
            logger.warning(f"ContaminationPreventionVanna: Attempted training - Q: '{question}', SQL: '{sql}'")
            return
        
        # Only allow training during initialization
        if hasattr(self, '_auto_train_enabled') and self._auto_train_enabled:
            logger.info(f"ContaminationPreventionVanna: Training allowed during initialization")
            return super().train(question=question, sql=sql, ddl=ddl, documentation=documentation, **kwargs)
        
        logger.warning(f"ContaminationPreventionVanna: Training blocked in strict mode")
    
    def enable_auto_training(self):
        """Enable auto-training (only during initialization)"""
        super().enable_auto_training()
        self._strict_mode = False
        logger.info("ContaminationPreventionVanna: Auto-training enabled, strict mode disabled")
    
    def disable_auto_training(self):
        """Disable auto-training and enable strict mode"""
        super().disable_auto_training()
        self._strict_mode = True
        logger.info("ContaminationPreventionVanna: Auto-training disabled, strict mode enabled")
    
    def generate_sql(self, question: str, **kwargs) -> str:
        """
        Generate SQL with additional contamination checks.
        """
        # Ensure clean state
        self.allow_llm_to_see_data = True
        self._strict_mode = True
        
        # Log the state
        logger.info(f"ContaminationPreventionVanna: Generating SQL with strict_mode={self._strict_mode}")
        logger.info(f"ContaminationPreventionVanna: allow_llm_to_see_data={self.allow_llm_to_see_data}")
        
        try:
            result = super().generate_sql(question=question, **kwargs)
            
            # Additional validation
            if not result or result.strip() == "":
                raise ValueError("Empty SQL result")
            
            # Check for error responses that might indicate contamination
            if any(indicator in result for indicator in ["Error:", "Cannot", "Unable", "Invalid"]):
                logger.warning(f"ContaminationPreventionVanna: Suspicious result: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"ContaminationPreventionVanna: Error in SQL generation: {e}")
            raise 