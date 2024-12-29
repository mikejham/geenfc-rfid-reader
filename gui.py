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

Classes:
    - ModernTreeview: A styled treeview widget for displaying tag data
    - RFIDGui: The main GUI application class

Dependencies:
    - tkinter: For GUI components
    - database.RFIDDatabase: For data storage and retrieval
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import RFIDDatabase
from typing import Dict, Any, Optional
from queue import Queue


class ModernTreeview(ttk.Treeview):
    """
    A custom Treeview widget with modern styling and improved visual design.

    This class extends the standard ttk.Treeview with custom styling to match
    modern UI design principles, including custom fonts, colors, and row heights.

    Attributes:
        style (ttk.Style): The style configuration for the treeview

    Example:
        tree = ModernTreeview(parent,
                            columns=("ID", "Name"),
                            show="headings")
        tree.grid(row=0, column=0)
    """

    def __init__(self, master: Any, **kwargs):
        """
        Initialize the ModernTreeview with custom styling.

        Args:
            master: The parent widget
            **kwargs: Additional keyword arguments passed to ttk.Treeview
        """
        super().__init__(master, **kwargs)
        style = ttk.Style()
        style.configure(
            "Modern.Treeview",
            background="#ffffff",
            foreground="#2c3e50",
            fieldbackground="#ffffff",
            rowheight=30,
            font=("SF Pro Display", 10),
        )
        style.configure(
            "Modern.Treeview.Heading",
            background="#f8f9fa",
            foreground="#2c3e50",
            font=("SF Pro Display", 11, "bold"),
        )
        self.configure(style="Modern.Treeview")


class RFIDGui:
    """
    Main GUI application class for the RFID Tag Reader.

    This class manages the entire graphical interface, including real-time updates,
    database interaction, and user controls. It provides a modern, clean interface
    with separate views for new and existing tags.

    Attributes:
        root (tk.Tk): The main window of the application
        data_queue (Queue): Queue for receiving data from the RFID reader thread
        main_frame (ttk.Frame): The main container frame
        notebook (ttk.Notebook): Tab container for different views
        new_tags_tree (ModernTreeview): Treeview for displaying new tags
        existing_tags_tree (ModernTreeview): Treeview for displaying existing tags

    Example:
        root = tk.Tk()
        data_queue = Queue()
        app = RFIDGui(root, data_queue)
        root.mainloop()
    """

    def __init__(self, root: tk.Tk, data_queue: Queue):
        """
        Initialize the GUI application.

        Args:
            root: The main window of the application
            data_queue: Queue for receiving data from the RFID reader thread
        """
        self.root = root
        self.data_queue = data_queue

        # Configure root window
        self.root.title("RFID Tag Reader")
        self.root.geometry("1200x800")
        self.root.configure(bg="#ffffff")

        # Configure modern styles
        self.setup_styles()

        # Create main container with padding
        self.main_frame = ttk.Frame(root, padding="20", style="Main.TFrame")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure root grid
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

        # Load existing tags and start update loop
        self.load_existing_tags()
        self.update_gui()

    def setup_styles(self) -> None:
        """
        Configure the visual styles for all GUI components.

        This method sets up a consistent, modern visual theme across the application,
        including colors, fonts, and widget-specific styling. It configures styles for:
        - Frames and containers
        - Labels and text
        - Buttons and interactive elements
        - Treeviews and data displays
        - Tabs and navigation elements
        """
        style = ttk.Style()

        # Configure colors
        bg_color = "#ffffff"
        fg_color = "#2c3e50"
        accent_color = "#007AFF"

        # Remove dotted focus border
        style.configure(".", focuscolor=bg_color)  # Remove focus color
        style.configure(
            "Treeview", highlightthickness=0, bd=0, font=("SF Pro Display", 10)
        )  # Remove treeview border

        # Frame styles
        style.configure("Main.TFrame", background=bg_color)
        style.configure("Card.TFrame", background=bg_color)

        # Label styles
        style.configure(
            "Header.TLabel",
            background=bg_color,
            foreground=fg_color,
            font=("SF Pro Display", 24, "bold"),
        )
        style.configure(
            "Status.TLabel",
            background=bg_color,
            foreground=fg_color,
            font=("SF Pro Display", 12),
        )
        style.configure(
            "Count.TLabel",
            background=bg_color,
            foreground=accent_color,
            font=("SF Pro Display", 12, "bold"),
        )

        # Modern button style
        style.configure(
            "Modern.TButton",
            background=accent_color,
            foreground="#ffffff",
            padding=(20, 10),
            font=("SF Pro Display", 11, "bold"),
            borderwidth=0,
            focuscolor=accent_color,
        )
        # Button hover and pressed states
        style.map(
            "Modern.TButton",
            background=[("active", "#0051D4"), ("pressed", "#0051D4")],
            relief=[("pressed", "flat"), ("!pressed", "flat")],
        )

        # Notebook style
        style.configure(
            "Modern.TNotebook",
            background=bg_color,
            tabmargins=[2, 5, 2, 0],
            borderwidth=0,
        )
        style.configure(
            "Modern.TNotebook.Tab",
            background=bg_color,
            foreground=fg_color,
            padding=[15, 5],
            font=("SF Pro Display", 11, "bold"),
            borderwidth=0,
            focuscolor=bg_color,
        )

        # Configure notebook tab colors and remove dotted border
        style.map(
            "Modern.TNotebook.Tab",
            background=[
                ("selected", "#0051D4"),
                ("active", "#E8F0FE"),
            ],
            foreground=[
                ("selected", "white"),
                ("active", accent_color),
                ("!selected", fg_color),
            ],
            borderwidth=[("selected", 0)],
            focuscolor=[("selected", bg_color)],
        )

        # Configure Treeview colors
        style.configure(
            "Modern.Treeview",
            background="#ffffff",
            foreground="#2c3e50",
            fieldbackground="#ffffff",
            rowheight=30,
            font=("SF Pro Display", 10),
            borderwidth=0,
            focuscolor=bg_color,
        )
        style.configure(
            "Modern.Treeview.Heading",
            background="#f8f9fa",
            foreground="#2c3e50",
            font=("SF Pro Display", 11, "bold"),
            borderwidth=0,
            relief="flat",
        )
        # Treeview selection colors
        style.map(
            "Modern.Treeview",
            background=[("selected", "#E8F0FE")],
            foreground=[("selected", "#2c3e50")],
        )

    def _setup_header(self) -> None:
        """
        Create and configure the application header.

        Creates a header frame with the application title using the configured
        header style. The header appears at the top of the application window.
        """
        header_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        header_label = ttk.Label(
            header_frame, text="RFID Tag Reader", style="Header.TLabel"
        )
        header_label.grid(row=0, column=0, sticky=tk.W)

    def _setup_status_frame(self) -> None:
        """
        Create and configure the status display area.

        Sets up a frame containing:
        - Current status message (e.g., "Waiting for tags...")
        - Total tag count display
        """
        self.status_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        self.status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        self.status_label = ttk.Label(
            self.status_frame, text="Waiting for tags...", style="Status.TLabel"
        )
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        self.tag_count_label = ttk.Label(
            self.status_frame, text="Total Tags: 0", style="Count.TLabel"
        )
        self.tag_count_label.grid(row=0, column=1, padx=20, sticky=tk.E)

    def _setup_control_frame(self) -> None:
        """
        Create and configure the control button area.

        Sets up a frame containing control buttons:
        - Clear Database button with confirmation dialog
        """
        self.control_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        self.control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        self.clear_btn = ttk.Button(
            self.control_frame,
            text="Clear Database",
            command=self.confirm_clear_database,
            style="Modern.TButton",
        )
        self.clear_btn.grid(row=0, column=0, padx=5, pady=5)

    def _setup_latest_frame(self) -> None:
        """
        Create and configure the latest read display area.

        Sets up a frame showing:
        - Label for "Latest Read"
        - Display of the most recently read tag information
        """
        self.latest_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        self.latest_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        latest_label = ttk.Label(
            self.latest_frame, text="Latest Read", style="Status.TLabel"
        )
        latest_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.latest_tag_label = ttk.Label(
            self.latest_frame, text="No tags read yet", style="Status.TLabel"
        )
        self.latest_tag_label.grid(row=1, column=0, sticky=tk.W)

    def _setup_notebook(self) -> None:
        """
        Create and configure the tabbed interface.

        Sets up a notebook widget with two tabs:
        - New Tags: Displays tags read in the current session
        - Existing Tags: Shows all historical tag readings
        """
        self.notebook = ttk.Notebook(self.main_frame, style="Modern.TNotebook")
        self.notebook.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create frames for each tab
        self.new_tags_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=20)
        self.existing_tags_frame = ttk.Frame(
            self.notebook, style="Card.TFrame", padding=20
        )

        # Add frames to notebook
        self.notebook.add(self.new_tags_frame, text="New Tags")
        self.notebook.add(self.existing_tags_frame, text="Existing Tags")

        # Create treeviews
        self.new_tags_tree = self.create_treeview(self.new_tags_frame)
        self.existing_tags_tree = self.create_treeview(self.existing_tags_frame)

    def create_treeview(self, parent: ttk.Frame) -> ModernTreeview:
        """
        Create a styled treeview for displaying tag data.

        Args:
            parent: The parent frame to contain the treeview

        Returns:
            ModernTreeview: A configured treeview widget with scrollbar

        The treeview displays columns for:
        - Tag ID
        - First Seen timestamp
        - Last Seen timestamp
        - Signal strength
        """
        tree = ModernTreeview(
            parent,
            columns=("Tag ID", "First Seen", "Last Seen", "Signal"),
            show="headings",
        )

        # Configure columns
        tree.heading("Tag ID", text="Tag ID")
        tree.heading("First Seen", text="First Seen")
        tree.heading("Last Seen", text="Last Seen")
        tree.heading("Signal", text="Signal")

        # Set column widths
        tree.column("Tag ID", width=300)
        tree.column("First Seen", width=200)
        tree.column("Last Seen", width=200)
        tree.column("Signal", width=100)

        # Add scrollbar with modern style
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Grid the tree and scrollbar
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        return tree

    def load_existing_tags(self) -> None:
        """
        Load and display all existing tags from the database.

        Retrieves all historical tag readings from the database and populates
        the existing tags treeview. Tags are displayed in reverse chronological
        order (most recent first).
        """
        db = RFIDDatabase()
        existing_tags = db.get_all_tags()
        for tag in existing_tags:
            self.existing_tags_tree.insert(
                "",
                0,
                values=(
                    tag["tag_id"],
                    tag["first_seen"],
                    tag["last_seen"],
                    f"{tag['rssi_percent']}%",
                ),
            )

    def update_gui(self) -> None:
        """
        Update the GUI with new data from the reader thread.

        This method:
        1. Checks the data queue for new information
        2. Updates the appropriate GUI elements based on the data type:
           - New tag readings
           - Status messages
           - Tag count updates
        3. Schedules the next update

        The method runs every 100ms to maintain responsive updates.
        """
        try:
            while not self.data_queue.empty():
                data = self.data_queue.get_nowait()
                if data.get("type") == "new_tag":
                    self._handle_new_tag(data["data"])
                elif data.get("type") == "status":
                    self.status_label.config(text=data["message"])
                elif data.get("type") == "count":
                    self.tag_count_label.config(text=f"Total Tags: {data['count']}")

        except Exception as e:
            print(f"GUI update error: {e}")

        # Schedule next update
        self.root.after(100, self.update_gui)

    def _handle_new_tag(self, tag_data: Dict[str, Any]) -> None:
        """
        Process and display new tag data in the GUI.

        Args:
            tag_data: Dictionary containing tag information with keys:
                - tag_id: Unique identifier for the tag
                - timestamp: Time of reading
                - rssi_percent: Signal strength as percentage
                - type: Tag type identifier
                - antenna: Antenna identifier
                - rssi_hex: Raw signal strength value

        This method:
        1. Updates the latest read display
        2. Adds the tag to the new tags view
        3. Updates the existing tags view
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update latest read display
        latest_text = (
            f"Tag: {tag_data['tag_id']}  |  "
            f"Time: {current_time}  |  "
            f"Signal: {tag_data['rssi_percent']}"
        )
        self.latest_tag_label.config(text=latest_text)

        # Add to new tags tree
        self.new_tags_tree.insert(
            "",
            0,
            values=(
                tag_data["tag_id"],
                current_time,
                current_time,
                tag_data["rssi_percent"],
            ),
        )

        # Update existing tags tree
        self._update_existing_tags_tree(tag_data, current_time)

    def _update_existing_tags_tree(
        self, tag_data: Dict[str, Any], current_time: str
    ) -> None:
        """
        Update the existing tags view with new tag data.

        Args:
            tag_data: Dictionary containing tag information
            current_time: Formatted timestamp string for the current reading

        This method either:
        1. Updates the last seen time for an existing tag, or
        2. Adds a new entry if the tag hasn't been seen before
        """
        existing_items = self.existing_tags_tree.get_children("")
        tag_found = False

        for item in existing_items:
            if self.existing_tags_tree.item(item)["values"][0] == tag_data["tag_id"]:
                values = list(self.existing_tags_tree.item(item)["values"])
                values[2] = current_time  # Update last seen
                self.existing_tags_tree.item(item, values=values)
                tag_found = True
                break

        if not tag_found:
            self.existing_tags_tree.insert(
                "",
                0,
                values=(
                    tag_data["tag_id"],
                    current_time,
                    current_time,
                    tag_data["rssi_percent"],
                ),
            )

    def confirm_clear_database(self) -> None:
        """
        Show a confirmation dialog before clearing the database.

        Displays a warning message box asking the user to confirm the database
        clear operation. If confirmed, calls the clear_database method.
        """
        if tk.messagebox.askyesno(
            "Confirm Clear",
            "Are you sure you want to clear all tag data? This cannot be undone.",
            icon="warning",
        ):
            self.clear_database()

    def clear_database(self) -> None:
        """
        Clear all tag data from the database and update the GUI.

        This method:
        1. Clears all records from the database
        2. Clears both treeview displays
        3. Updates the tag count and status displays
        4. Shows a success message

        If an error occurs during the process, displays an error message.
        """
        try:
            db = RFIDDatabase()
            db.clear_database()

            # Clear both treeviews
            for item in self.new_tags_tree.get_children():
                self.new_tags_tree.delete(item)
            for item in self.existing_tags_tree.get_children():
                self.existing_tags_tree.delete(item)

            # Update status
            self.tag_count_label.config(text="Total Tags: 0")
            self.status_label.config(text="Database cleared")

            # Show success message
            tk.messagebox.showinfo("Success", "Database has been cleared successfully!")

        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to clear database: {str(e)}")
