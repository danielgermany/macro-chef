"""
Database migration: Add online recipe support columns to meal_templates table.
Adds api_source, api_recipe_id, nutrition_validated, price_confidence, price_source.
"""

import sqlite3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config.config import DATABASE_PATH


def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def migrate_database():
    """Add new columns to meal_templates table if they don't exist."""

    print("\n" + "=" * 60)
    print("DATABASE MIGRATION: Add Online Recipe Support")
    print("=" * 60)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    columns_to_add = [
        ("api_source", "TEXT DEFAULT NULL"),
        ("api_recipe_id", "TEXT DEFAULT NULL"),
        ("nutrition_validated", "BOOLEAN DEFAULT 0"),
        ("price_confidence", "REAL DEFAULT NULL"),
        ("price_source", "TEXT DEFAULT NULL")
    ]

    added_count = 0
    skipped_count = 0

    for column_name, column_def in columns_to_add:
        if column_exists(cursor, 'meal_templates', column_name):
            print(f"[SKIP] Column '{column_name}' already exists")
            skipped_count += 1
        else:
            try:
                cursor.execute(f"ALTER TABLE meal_templates ADD COLUMN {column_name} {column_def}")
                print(f"[SUCCESS] Added column '{column_name}'")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"[ERROR] Failed to add column '{column_name}': {e}")

    # Add indexes
    indexes_to_add = [
        ("idx_meal_api_source", "meal_templates", "api_source"),
        ("idx_meal_api_recipe_id", "meal_templates", "api_recipe_id")
    ]

    for index_name, table_name, column_name in indexes_to_add:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})")
            print(f"[SUCCESS] Created index '{index_name}'")
        except sqlite3.OperationalError as e:
            print(f"[WARNING] Index '{index_name}' may already exist: {e}")

    conn.commit()
    conn.close()

    print("=" * 60)
    print(f"[COMPLETE] Migration finished")
    print(f"  - Columns added: {added_count}")
    print(f"  - Columns skipped (already exist): {skipped_count}")
    print("=" * 60)


if __name__ == "__main__":
    migrate_database()
