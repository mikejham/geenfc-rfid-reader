"""
RFID Tag Reader Application
==========================

Main entry point for the RFID Tag Reader application. This module initializes
the GUI and RFID reader components and manages their interaction.

The application provides real-time monitoring of RFID tags with features for:
    - Live tag detection and display
    - Historical tag data viewing
    - Database management
    - Modern, user-friendly interface

Architecture:
    The application uses a multi-threaded architecture:
    - Main thread: Runs the GUI and handles user interaction
    - Reader thread: Manages RFID hardware communication
    - Inter-thread communication via Queue

Dependencies:
    - tkinter: For the graphical interface
    - threading: For parallel operation
    - queue: For thread communication
    - gui: Custom GUI implementation
    - reader: RFID reader interface
"""

#!/usr/bin/python
# -*- coding: UTF-8 -*-
import tkinter as tk
import threading
from queue import Queue
from gui import RFIDGui
from reader import rfid_reader_thread


def main() -> None:
    """
    Initialize and start the RFID Tag Reader application.

    This function:
    1. Creates the main application window
    2. Sets up thread communication
    3. Starts the RFID reader thread
    4. Initializes the GUI
    5. Begins the main event loop

    The application runs until the user closes the window,
    at which point all threads are automatically terminated.
    """
    # Create the root window
    root = tk.Tk()

    # Create a queue for thread communication
    data_queue = Queue()

    # Create and start the RFID reader thread
    reader_thread = threading.Thread(
        target=rfid_reader_thread,
        args=(data_queue,),
        daemon=True,  # Thread will be terminated when main program exits
    )
    reader_thread.start()

    # Create the GUI
    app = RFIDGui(root, data_queue)

    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()
