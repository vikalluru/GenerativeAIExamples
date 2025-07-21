"""
Direct SQLite database connector for golden plot generation.
No dependencies on the agentic framework.
"""
import sqlite3
import pandas as pd
import os
from typing import Optional

class DatabaseConnector:
    def __init__(self, db_path: str = "../PredM_db/nasa_turbo.db"):
        self.db_path = db_path
        
    def execute_query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """
        Execute SQL query and return results as pandas DataFrame.
        
        Args:
            sql_query (str): SQL query to execute
            
        Returns:
            pd.DataFrame or None: Query results
        """
        try:
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(f"Database not found at: {self.db_path}")
                
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(sql_query, conn)
                return df
                
        except Exception as e:
            print(f"Error executing query: {e}")
            print(f"SQL Query: {sql_query}")
            return None
    
    def get_table_info(self, table_name: str) -> Optional[pd.DataFrame]:
        """Get table schema information."""
        sql = f"PRAGMA table_info({table_name})"
        return self.execute_query(sql)
    
    def list_tables(self) -> Optional[pd.DataFrame]:
        """List all tables in the database."""
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        return self.execute_query(sql) 