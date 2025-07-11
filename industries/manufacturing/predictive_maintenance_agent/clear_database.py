#!/usr/bin/env python3
"""
Utility script to clear the vector database for troubleshooting.
Use this when you encounter robustness issues with the predictive maintenance agent.
"""

import os
import shutil
import sys

def clear_vector_database():
    """Clear the vector database directory."""
    database_path = "database"
    
    if not os.path.exists(database_path):
        print(f"❌ Database directory '{database_path}' does not exist.")
        return False
    
    try:
        # Remove all contents of the database directory
        for item in os.listdir(database_path):
            item_path = os.path.join(database_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"🗑️  Removed directory: {item_path}")
            else:
                os.remove(item_path)
                print(f"🗑️  Removed file: {item_path}")
        
        print("✅ Vector database cleared successfully!")
        print("🔄 Restart your backend to reinitialize the database.")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False

def clear_output_data():
    """Clear the output data directory."""
    output_path = "output_data"
    
    if not os.path.exists(output_path):
        print(f"❌ Output directory '{output_path}' does not exist.")
        return False
    
    try:
        # Remove all JSON files in output directory
        for item in os.listdir(output_path):
            if item.endswith('.json'):
                item_path = os.path.join(output_path, item)
                os.remove(item_path)
                print(f"🗑️  Removed output file: {item_path}")
        
        print("✅ Output data cleared successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing output data: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Predictive Maintenance Agent - Database Cleanup Utility")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        print("Clearing both vector database and output data...")
        clear_vector_database()
        clear_output_data()
    elif len(sys.argv) > 1 and sys.argv[1] == "--output":
        print("Clearing output data only...")
        clear_output_data()
    else:
        print("Clearing vector database only...")
        clear_vector_database()
        
    print("\n💡 Usage:")
    print("  python clear_database.py           # Clear vector database only")
    print("  python clear_database.py --all     # Clear both database and output")
    print("  python clear_database.py --output  # Clear output data only") 