"""
RFID Tag Database Module
=======================

This module handles all database operations for the RFID tag reader application.
It provides a clean interface for storing and retrieving tag data using SQLite.

The database schema includes:
    - id: Primary key
    - tag_id: Unique identifier for each tag
    - first_seen: Timestamp of first detection
    - last_seen: Timestamp of most recent detection
    - rssi_hex: Raw signal strength value
    - rssi_percent: Calculated signal strength percentage
    - antenna: Antenna identifier
    - reader_id: Identifier for the RFID reader

Features:
    - Automatic database creation and schema management
    - Thread-safe database operations
    - Efficient tag lookup and updates
    - Support for historical tag data

Dependencies:
    - sqlite3: For database operations
    - datetime: For timestamp handling
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Union


class RFIDDatabase:
    """
    Database manager for RFID tag data.

    This class handles all database operations including initialization,
    tag recording, and data retrieval. It maintains a SQLite database
    for persistent storage of tag readings.

    Attributes:
        db_path (str): Path to the SQLite database file

    Example:
        db = RFIDDatabase()
        db.record_tag({
            'tag_id': 'ABC123',
            'rssi_hex': '0xA0',
            'rssi_percent': '85.5%',
            'antenna': '1'
        })
    """

    def __init__(self, db_path: str = "rfid_readings.db"):
        """
        Initialize the database connection.

        Args:
            db_path: Path where the database file should be created/accessed
        """
        self.db_path = db_path
        self.setup_database()

    def setup_database(self) -> None:
        """
        Create the database and required tables if they don't exist.

        Creates a table with the following schema:
        - id: INTEGER PRIMARY KEY
        - tag_id: TEXT NOT NULL UNIQUE
        - first_seen: TIMESTAMP
        - last_seen: TIMESTAMP
        - rssi_hex: TEXT
        - rssi_percent: REAL
        - antenna: TEXT
        - reader_id: TEXT
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        try:
            # Create or update table schema
            c.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY,
                    tag_id TEXT NOT NULL,
                    first_seen TIMESTAMP,
                    last_seen TIMESTAMP,
                    rssi_hex TEXT,
                    rssi_percent REAL,
                    antenna TEXT,
                    reader_id TEXT,
                    UNIQUE(tag_id)
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def get_tag_count(self) -> int:
        """
        Get the total number of unique tags in the database.

        Returns:
            int: The number of unique tags recorded
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM tags")
        count = c.fetchone()[0]
        conn.close()
        return count

    def is_tag_seen(self, tag_id: str) -> bool:
        """
        Check if a specific tag has been recorded before.

        Args:
            tag_id: The unique identifier of the tag to check

        Returns:
            bool: True if the tag exists in the database, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT tag_id FROM tags WHERE tag_id = ?", (tag_id,))
        result = c.fetchone()
        conn.close()
        return result is not None

    def record_tag(
        self, tag_data: Dict[str, str], reader_id: str = "READER_001"
    ) -> bool:
        """
        Record a tag reading in the database.

        If the tag is new, creates a new record. If the tag exists,
        updates its last_seen timestamp.

        Args:
            tag_data: Dictionary containing tag information with keys:
                - tag_id: Unique identifier for the tag
                - rssi_hex: Raw signal strength value
                - rssi_percent: Signal strength as percentage
                - antenna: Antenna identifier
            reader_id: Identifier for the RFID reader (default: "READER_001")

        Returns:
            bool: True if this is a new tag, False if it's an update

        Raises:
            sqlite3.Error: If there's a database error
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        try:
            # Try to insert new record
            c.execute(
                """
                INSERT INTO tags 
                (tag_id, first_seen, last_seen, rssi_hex, rssi_percent, antenna, reader_id)
                VALUES (?, datetime('now'), datetime('now'), ?, ?, ?, ?)
            """,
                (
                    tag_data["tag_id"],
                    tag_data["rssi_hex"],
                    float(tag_data["rssi_percent"].rstrip("%")),
                    tag_data["antenna"],
                    reader_id,
                ),
            )
            is_new = True
        except sqlite3.IntegrityError:
            # Update existing record's last_seen time
            c.execute(
                """
                UPDATE tags 
                SET last_seen = datetime('now')
                WHERE tag_id = ?
            """,
                (tag_data["tag_id"],),
            )
            is_new = False

        conn.commit()
        conn.close()
        return is_new

    def get_all_tags(self) -> List[Dict[str, Union[str, float]]]:
        """
        Retrieve all recorded tags from the database.

        Returns:
            List[Dict]: List of dictionaries containing tag information:
                - tag_id: Unique identifier for the tag
                - first_seen: Initial detection timestamp
                - last_seen: Most recent detection timestamp
                - rssi_hex: Raw signal strength value
                - rssi_percent: Signal strength as percentage
                - antenna: Antenna identifier
                - reader_id: Reader identifier

        The results are ordered by last_seen timestamp (most recent first).
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("""
            SELECT 
                tag_id,
                first_seen,
                last_seen,
                rssi_hex,
                rssi_percent,
                antenna,
                reader_id
            FROM tags
            ORDER BY last_seen DESC
        """)

        results = [dict(row) for row in c.fetchall()]
        conn.close()
        return results

    def clear_database(self) -> None:
        """
        Remove all records from the database.

        This operation cannot be undone. It removes all tag records
        while maintaining the table structure.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute("DELETE FROM tags")
            conn.commit()
        finally:
            conn.close()
