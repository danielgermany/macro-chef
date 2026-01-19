"""
Base database manager with common operations.
All other scripts inherit from this class.
"""

import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config.config import DATABASE_PATH

def get_db_path() -> Path:
    """Get database path from environment or config."""
    # Check for DATABASE_URL environment variable first (for tests)
    db_url = os.getenv("DATABASE_URL", "")
    if db_url and db_url.startswith("sqlite:///"):
        # Extract path from SQLite URL
        db_path = db_url.replace("sqlite:///", "")
        return Path(db_path)
    
    # Fall back to config
    return DATABASE_PATH

class DatabaseManager:
    """Base class for database operations."""

    def __init__(self, db_path: Optional[Union[Path, str]] = None):
        """Initialize database connection.
        
        Args:
            db_path: Optional database path. If None, reads from DATABASE_URL
                    environment variable or falls back to config.
        """
        if db_path is None:
            self.db_path = get_db_path()
        else:
            self.db_path = Path(db_path) if isinstance(db_path, str) else db_path
        self.conn = None

    def connect(self):
        """Establish database connection."""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            # Enable foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON;")
        return self.conn

    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a SELECT query and return results as list of dicts."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def execute_single(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Execute a SELECT query and return single result as dict."""
        results = self.execute_query(query, params)
        return results[0] if results else None

    def execute_write(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return last row ID."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid

    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Execute multiple INSERT/UPDATE queries."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.execute_single(query, (table_name,))
        return result is not None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
