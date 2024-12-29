"""
RFID Tag Reader GUI Module
=========================

This module provides a modern, Apple-inspired graphical user interface for the RFID tag reader application.
It handles the display and interaction of RFID tag data in real-time, with features for viewing both
new and historical tag readings.

Key Features:
    - Real-time tag reading display
    - Historical tag data viewing
    - Modern, clean interface design
    - Database management controls
    - Separate views for new and existing tags
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import RFIDDatabase
from typing import Dict, Any, Optional
from queue import Queue
from logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


class ModernTreeview(ttk.Treeview):
    """A custom Treeview widget with modern styling."""

    def __init__(self, master: Any, **kwargs):
        super().__init__(master, **kwargs)
        style = ttk.Style()

        # Configure colors
        style.configure(
            "Modern.Treeview",
            background="#ffffff",
            foreground="#2c3e50",
            fieldbackground="#ffffff",
            rowheight=30,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Modern.Treeview.Heading",
            background="#f8f9fa",
            foreground="#2c3e50",
            font=("Segoe UI", 11, "bold"),
        )
        self.configure(style="Modern.Treeview")


class RFIDGui:
    """Main GUI application class for the RFID Tag Reader."""

    def __init__(self, root: tk.Tk, data_queue: Queue):
        self.root = root
        self.data_queue = data_queue
        self.db = RFIDDatabase()

        # Configure root window
        self.root.title("RFID Tag Reader")
        self.root.geometry("1200x800")
        self.root.configure(bg="#ffffff")

        # Configure styles
        self.setup_styles()

        # Create main container
        self.main_frame = ttk.Frame(root, padding="20", style="Main.TFrame")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Setup GUI components
        self._setup_header()
        self._setup_status_frame()
        self._setup_control_frame()
        self._setup_latest_frame()
        self._setup_notebook()

        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(4, weight=1)  # Notebook row

        # Initialize
        self.load_existing_tags()
        self.update_gui()

    def setup_styles(self):
        """Configure the visual styles for all GUI components."""
        style = ttk.Style()

        # Colors
        bg_color = "#ffffff"
        fg_color = "#2c3e50"
        accent_color = "#007AFF"

        # Frame styles
        style.configure("Main.TFrame", background=bg_color)
        style.configure("Card.TFrame", background=bg_color)

        # Label styles
        style.configure(
            "Header.TLabel",
            background=bg_color,
            foreground=fg_color,
            font=("Segoe UI", 24, "bold"),
        )
        style.configure(
            "Status.TLabel",
            background=bg_color,
            foreground=fg_color,
            font=("Segoe UI", 12),
        )
        style.configure(
            "Count.TLabel",
            background=bg_color,
            foreground=accent_color,
            font=("Segoe UI", 12, "bold"),
        )

        # Button style
        style.configure(
            "Modern.TButton",
            background=accent_color,
            foreground="#ffffff",
            padding=(20, 10),
            font=("Segoe UI", 11, "bold"),
        )

        # Notebook style
        style.configure(
            "Modern.TNotebook",
            background=bg_color,
            tabmargins=[2, 5, 2, 0],
        )
        style.configure(
            "Modern.TNotebook.Tab",
            background=bg_color,
            foreground=fg_color,
            padding=[15, 5],
            font=("Segoe UI", 11),
        )

    def _setup_header(self):
        """Setup the header section with title."""
        header = ttk.Label(
            self.main_frame, text="RFID Tag Reader", style="Header.TLabel"
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 20))

    def _setup_status_frame(self):
        """Setup the status section showing reader state and tag count."""
        self.status_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        self.status_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        self.status_label = ttk.Label(
            self.status_frame, text="Initializing...", style="Status.TLabel"
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        self.count_label = ttk.Label(
            self.status_frame, text="Tags: 0", style="Count.TLabel"
        )
        self.count_label.grid(row=0, column=1, sticky="e", padx=(20, 0))

        self.status_frame.columnconfigure(1, weight=1)

    def _setup_control_frame(self):
        """Setup the control section with buttons."""
        control_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        control_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))

        # Create a frame for buttons
        button_frame = ttk.Frame(control_frame, style="Card.TFrame")
        button_frame.grid(row=0, column=0, sticky="w")

        clear_btn = ttk.Button(
            button_frame,
            text="Clear Database",
            style="Modern.TButton",
            command=self.confirm_clear_database,
        )
        clear_btn.grid(row=0, column=0, padx=(0, 10))

        view_db_btn = ttk.Button(
            button_frame,
            text="View Database",
            style="Modern.TButton",
            command=self.show_database_contents,
        )
        view_db_btn.grid(row=0, column=1)

    def _setup_latest_frame(self):
        """Setup the section showing the most recent tag read."""
        self.latest_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        self.latest_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))

        latest_label = ttk.Label(
            self.latest_frame, text="Latest Read:", style="Status.TLabel"
        )
        latest_label.grid(row=0, column=0, sticky="w")

        self.latest_tag_label = ttk.Label(
            self.latest_frame, text="No tags read", style="Status.TLabel"
        )
        self.latest_tag_label.grid(row=1, column=0, sticky="w", pady=(5, 0))

    def _setup_notebook(self):
        """Setup the tabbed interface for new and existing tags."""
        self.notebook = ttk.Notebook(self.main_frame, style="Modern.TNotebook")
        self.notebook.grid(row=4, column=0, sticky="nsew")

        # New Tags Tab
        new_tags_frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(new_tags_frame, text="New Tags")

        self.new_tags_tree = ModernTreeview(
            new_tags_frame,
            columns=("tag_id", "time", "rssi", "antenna"),
            show="headings",
        )
        self.new_tags_tree.heading("tag_id", text="Tag ID")
        self.new_tags_tree.heading("time", text="Time")
        self.new_tags_tree.heading("rssi", text="Signal Strength")
        self.new_tags_tree.heading("antenna", text="Antenna")

        self.new_tags_tree.column("tag_id", width=300)
        self.new_tags_tree.column("time", width=200)
        self.new_tags_tree.column("rssi", width=150)
        self.new_tags_tree.column("antenna", width=100)

        self.new_tags_tree.grid(row=0, column=0, sticky="nsew")
        new_tags_frame.columnconfigure(0, weight=1)
        new_tags_frame.rowconfigure(0, weight=1)

        # Existing Tags Tab
        existing_tags_frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(existing_tags_frame, text="Existing Tags")

        self.existing_tags_tree = ModernTreeview(
            existing_tags_frame,
            columns=("tag_id", "first_seen", "last_seen", "rssi", "antenna"),
            show="headings",
        )
        self.existing_tags_tree.heading("tag_id", text="Tag ID")
        self.existing_tags_tree.heading("first_seen", text="First Seen")
        self.existing_tags_tree.heading("last_seen", text="Last Seen")
        self.existing_tags_tree.heading("rssi", text="Signal Strength")
        self.existing_tags_tree.heading("antenna", text="Antenna")

        self.existing_tags_tree.column("tag_id", width=300)
        self.existing_tags_tree.column("first_seen", width=200)
        self.existing_tags_tree.column("last_seen", width=200)
        self.existing_tags_tree.column("rssi", width=150)
        self.existing_tags_tree.column("antenna", width=100)

        self.existing_tags_tree.grid(row=0, column=0, sticky="nsew")
        existing_tags_frame.columnconfigure(0, weight=1)
        existing_tags_frame.rowconfigure(0, weight=1)

    def load_existing_tags(self):
        """Load existing tags from the database into the existing tags treeview."""
        try:
            # Clear existing items
            for item in self.existing_tags_tree.get_children():
                self.existing_tags_tree.delete(item)

            # Get all tags from database
            # Tags are returned as tuples: (tag_id, first_seen, last_seen, rssi_hex, rssi_percent, antenna, reader_id)
            tags = self.db.get_all_tags()
            logger.debug(f"Loading {len(tags)} tags from database")

            # Add each tag to the treeview
            for tag in tags:
                self.existing_tags_tree.insert(
                    "",
                    "end",
                    values=(
                        tag[0],  # tag_id
                        tag[1],  # first_seen
                        tag[2],  # last_seen
                        tag[4],  # rssi_percent
                        tag[5],  # antenna
                    ),
                )
        except Exception as e:
            logger.error(f"Error loading existing tags: {e}")
            messagebox.showerror("Error", "Failed to load existing tags")

    def update_gui(self):
        """Update the GUI with new data from the queue."""
        try:
            while self.data_queue.qsize():
                try:
                    msg = self.data_queue.get_nowait()
                    msg_type = msg.get("type", "")

                    if msg_type == "status":
                        self.status_label.config(text=msg["message"])
                    elif msg_type == "count":
                        self.count_label.config(text=f"Tags: {msg['count']}")
                    elif msg_type == "new_tag":
                        tag_data = msg["data"]
                        # Update latest tag label
                        latest_text = (
                            f"Tag ID: {tag_data['tag_id']}\n"
                            f"Time: {tag_data['timestamp']}\n"
                            f"Signal: {tag_data['rssi_percent']}\n"
                            f"Antenna: {tag_data['antenna']}"
                        )
                        self.latest_tag_label.config(text=latest_text)

                        # Check if tag already exists in new tags tree
                        tag_exists = False
                        for item in self.new_tags_tree.get_children():
                            values = self.new_tags_tree.item(item)["values"]
                            if values[0] == tag_data["tag_id"]:  # Compare tag IDs
                                # Update existing entry with new values
                                self.new_tags_tree.item(
                                    item,
                                    values=(
                                        tag_data["tag_id"],
                                        tag_data["timestamp"],
                                        tag_data["rssi_percent"],
                                        tag_data["antenna"],
                                    ),
                                )
                                tag_exists = True
                                break

                        # Only add if it's a new tag
                        if not tag_exists:
                            self.new_tags_tree.insert(
                                "",
                                0,  # Insert at the top
                                values=(
                                    tag_data["tag_id"],
                                    tag_data["timestamp"],
                                    tag_data["rssi_percent"],
                                    tag_data["antenna"],
                                ),
                            )

                        # Reload existing tags
                        self.load_existing_tags()

                except Exception as e:
                    logger.error(f"Error processing queue message: {e}")

        except Exception as e:
            logger.error(f"Error in update_gui: {e}")
        finally:
            # Schedule the next update
            self.root.after(100, self.update_gui)

    def confirm_clear_database(self):
        """Show confirmation dialog before clearing the database."""
        if messagebox.askyesno(
            "Confirm Clear", "Are you sure you want to clear all tag data?"
        ):
            try:
                if self.db.clear_database():
                    # Clear existing tags view
                    self.load_existing_tags()

                    # Clear new tags tree
                    for item in self.new_tags_tree.get_children():
                        self.new_tags_tree.delete(item)

                    # Reset latest tag label
                    self.latest_tag_label.config(text="No tags read")

                    # Reset tag count
                    self.count_label.config(text="Tags: 0")

                    messagebox.showinfo("Success", "Database cleared successfully")
                else:
                    messagebox.showerror("Error", "Failed to clear database")
            except Exception as e:
                logger.error(f"Error clearing database: {e}")
                messagebox.showerror("Error", f"Failed to clear database: {e}")

    def show_database_contents(self):
        """Show a new window with raw database contents."""
        # Create new window
        db_window = tk.Toplevel(self.root)
        db_window.title("Database Contents")
        db_window.geometry("800x600")
        db_window.configure(bg="#ffffff")

        # Create text widget with scrollbar
        text_frame = ttk.Frame(db_window, style="Card.TFrame")
        text_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        text_widget = tk.Text(
            text_frame,
            wrap=tk.NONE,
            font=("Consolas", 10),
            bg="#ffffff",
            fg="#2c3e50",
        )
        scrollbar_y = ttk.Scrollbar(
            text_frame, orient="vertical", command=text_widget.yview
        )
        scrollbar_x = ttk.Scrollbar(
            text_frame, orient="horizontal", command=text_widget.xview
        )
        text_widget.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
        )

        # Grid layout
        text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Configure grid weights
        db_window.columnconfigure(0, weight=1)
        db_window.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        try:
            # Get all tags from database
            tags = self.db.get_all_tags()

            # Format header
            header = "Database Contents:\n"
            header += "=" * 80 + "\n\n"
            header += f"Total Tags: {len(tags)}\n"
            header += "-" * 80 + "\n\n"
            header += "Format: (tag_id, first_seen, last_seen, rssi_hex, rssi_percent, antenna, reader_id)\n\n"
            text_widget.insert("1.0", header)

            # Add each tag with formatting
            for tag in tags:
                text_widget.insert("end", f"{tag}\n")

            # Make text widget read-only
            text_widget.configure(state="disabled")

        except Exception as e:
            logger.error(f"Error showing database contents: {e}")
            text_widget.insert("1.0", f"Error reading database: {str(e)}")
            text_widget.configure(state="disabled")
