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

from queue import Queue
import tkinter as tk
from threading import Thread
from gui import RFIDGui
from reader import rfid_reader_thread
from logger import setup_logger

# Initialize logging
logger = setup_logger(__name__)


def main():
    """Main entry point for the RFID Reader application."""
    try:
        logger.info("Starting RFID Reader application")

        # Create the main window
        root = tk.Tk()
        root.title("RFID Tag Reader")

        # Create data queue for thread communication
        data_queue = Queue()

        # Create and start the RFID reader thread
        reader_thread = Thread(
            target=rfid_reader_thread, args=(data_queue,), daemon=True
        )
        reader_thread.start()
        logger.info("Started RFID reader thread")

        # Create and start the GUI
        gui = RFIDGui(root, data_queue)
        logger.info("Created GUI")

        # Start the main loop
        root.mainloop()
        logger.info("Application closed")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
