#!/usr/bin/env python3
"""
Reset Vanna State Utility

This script provides a way to reset the VannaManager state to prevent
vector store contamination. Use this when you notice degraded performance
or after running evaluation scripts.

Usage:
    python reset_vanna_state.py [--force-clean-db]
    
Options:
    --force-clean-db    Also clean the vector database files (more aggressive reset)
"""

import argparse
import os
import sys
import shutil
import logging
from pathlib import Path

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from predictive_maintenance_agent.vanna_manager import VannaManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reset_vanna_managers():
    """Reset all VannaManager instances"""
    logger.info("Resetting all VannaManager instances...")
    
    # Reset all existing instances
    for config_key, manager in VannaManager._instances.items():
        logger.info(f"Resetting VannaManager: {config_key}")
        manager.force_reset()
        stats = manager.get_stats()
        logger.info(f"Manager stats after reset: {stats}")
    
    # Clear the instances dictionary
    VannaManager._instances.clear()
    logger.info("All VannaManager instances have been reset")

def clean_vector_database(vector_store_path: str):
    """Clean the vector database files"""
    if not os.path.exists(vector_store_path):
        logger.info(f"Vector store path does not exist: {vector_store_path}")
        return
    
    logger.info(f"Cleaning vector database at: {vector_store_path}")
    
    try:
        # Remove all subdirectories (ChromaDB collections)
        for item in os.listdir(vector_store_path):
            item_path = os.path.join(vector_store_path, item)
            if os.path.isdir(item_path):
                logger.info(f"Removing directory: {item_path}")
                shutil.rmtree(item_path)
            elif item.endswith('.sqlite3'):
                logger.info(f"Removing database file: {item_path}")
                os.remove(item_path)
        
        logger.info("Vector database cleaned successfully")
        
    except Exception as e:
        logger.error(f"Error cleaning vector database: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Reset Vanna State Utility')
    parser.add_argument('--force-clean-db', action='store_true', 
                       help='Also clean the vector database files (more aggressive reset)')
    parser.add_argument('--vector-store-path', default='./database',
                       help='Path to the vector store database (default: ./database)')
    
    args = parser.parse_args()
    
    logger.info("Starting Vanna state reset...")
    
    # Reset VannaManager instances
    reset_vanna_managers()
    
    # Clean vector database if requested
    if args.force_clean_db:
        logger.info("Performing aggressive database cleanup...")
        clean_vector_database(args.vector_store_path)
        logger.info("Database cleanup completed. Vector store will be re-initialized on next use.")
    
    logger.info("Vanna state reset completed successfully!")
    logger.info("The system is now ready for fresh queries without contamination.")

if __name__ == '__main__':
    main() 