"""
Database Module
=============

Handles all database operations for the RFID Tag Reader application.
Uses SQLite for persistent storage of tag data.

Features:
    - Tag storage and retrieval
    - First seen and last seen tracking
    - Signal strength history
    - Duplicate tag detection
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


class RFIDDatabase:
    """Manages the SQLite database for RFID tag storage."""

    def __init__(self, db_path: str = "tags.db"):
        """Initialize the database connection and create tables if needed."""
        self.db_path = db_path
        self.setup_database()
        logger.info(f"Database initialized at {db_path}")

    def setup_database(self) -> None:
        """Create the necessary database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create tags table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tags (
                        tag_id TEXT PRIMARY KEY,
                        first_seen TIMESTAMP,
                        last_seen TIMESTAMP,
                        rssi_hex TEXT,
                        rssi_percent TEXT,
                        antenna TEXT,
                        reader_id TEXT
                    )
                """)
                conn.commit()
                logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error setting up database: {e}")
            raise

    def record_tag(self, tag_data: Dict[str, str]) -> bool:
        """
        Record a tag reading in the database.

        Args:
            tag_data: Dictionary containing tag information

        Returns:
            bool: True if this is a new tag, False if it's an update
        """
        try:
            logger.debug(f"Recording tag: {tag_data}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if tag exists
                cursor.execute(
                    "SELECT tag_id FROM tags WHERE tag_id = ?", (tag_data["tag_id"],)
                )
                existing_tag = cursor.fetchone()

                if existing_tag:
                    # Update existing tag
                    logger.debug(f"Updating existing tag: {tag_data['tag_id']}")
                    cursor.execute(
                        """
                        UPDATE tags 
                        SET last_seen = ?, rssi_hex = ?, rssi_percent = ?, 
                            antenna = ?
                        WHERE tag_id = ?
                    """,
                        (
                            tag_data["timestamp"],
                            tag_data["rssi_hex"],
                            tag_data["rssi_percent"],
                            tag_data["antenna"],
                            tag_data["tag_id"],
                        ),
                    )
                    return False
                else:
                    # Insert new tag
                    logger.debug(f"Inserting new tag: {tag_data['tag_id']}")
                    cursor.execute(
                        """
                        INSERT INTO tags (
                            tag_id, first_seen, last_seen, rssi_hex,
                            rssi_percent, antenna, reader_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            tag_data["tag_id"],
                            tag_data["timestamp"],
                            tag_data["timestamp"],
                            tag_data["rssi_hex"],
                            tag_data["rssi_percent"],
                            tag_data["antenna"],
                            tag_data.get("reader_id", "default"),
                        ),
                    )
                    return True

        except Exception as e:
            logger.error(f"Error recording tag: {e}")
            return False

    def get_all_tags(self) -> List[Tuple]:
        """Retrieve all tags from the database."""
        try:
            logger.debug("Retrieving all tags from database")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT tag_id, first_seen, last_seen, rssi_hex,
                           rssi_percent, antenna, reader_id
                    FROM tags
                    ORDER BY last_seen DESC
                """)
                tags = cursor.fetchall()
                logger.debug(f"Retrieved {len(tags)} tags")
                return tags
        except Exception as e:
            logger.error(f"Error retrieving tags: {e}")
            return []

    def get_tag_count(self) -> int:
        """Get the total number of unique tags in the database."""
        try:
            logger.debug("Getting tag count")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM tags")
                count = cursor.fetchone()[0]
                logger.debug(f"Current tag count: {count}")
                return count
        except Exception as e:
            logger.error(f"Error getting tag count: {e}")
            return 0

    def clear_database(self) -> bool:
        """Remove all tags from the database."""
        try:
            logger.info("Clearing database")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tags")
                conn.commit()
                logger.info("Database cleared successfully")
                return True
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            return False
