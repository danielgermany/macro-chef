"""
Migration script to add authentication fields to user_profile table.
Adds email and password_hash columns for JWT authentication.

Usage: python scripts/migrate_add_auth.py
"""
import sqlite3
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config.config import DATABASE_PATH

def migrate():
    """Add authentication columns to user_profile table."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(user_profile)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'email' not in columns:
            print("Adding email column...")
            cursor.execute("ALTER TABLE user_profile ADD COLUMN email TEXT")
            print("[OK] email column added")
        else:
            print("[OK] email column already exists")
        
        if 'password_hash' not in columns:
            print("Adding password_hash column...")
            cursor.execute("ALTER TABLE user_profile ADD COLUMN password_hash TEXT")
            print("[OK] password_hash column added")
        else:
            print("[OK] password_hash column already exists")
        
        # Create unique index on email for faster lookups and uniqueness
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_user_email ON user_profile(email)")
            print("[OK] email unique index created")
        except sqlite3.OperationalError as e:
            # If index creation fails due to duplicate emails, warn but continue
            print(f"[WARNING] Could not create unique index: {e}")
            print("  (This is OK if you have existing users without emails)")
        
        conn.commit()
        print("\n[SUCCESS] Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
