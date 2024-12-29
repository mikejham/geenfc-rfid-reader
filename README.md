# RFID Tag Reader

A modern GUI application for reading and managing RFID tags using a USB RFID reader. Built with Python, Tkinter, and SQLite.

## Features

- Real-time tag reading and display
- Modern, clean user interface
- Historical tag data tracking
- Database management with SQLite
- Separate views for new and existing tags
- Raw database content viewer

## Requirements

- Python 3.8 or higher
- USB RFID Reader (compatible with SWHidApi.dll)
- Required Python packages (see requirements.txt)
- Windows OS (due to DLL dependency)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/mikejham/geenfc-rfid-reader.git
cd geenfc-rfid-reader
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Verify all required files are present:

- main.py
- reader.py
- database.py
- gui.py
- SWHidApi.dll (in the same directory as the Python files)

## Usage

Run the application:

```bash
python main.py
```

The application window will open with:

- Status section showing reader state and tag count
- Latest read section showing most recent tag
- Tabs for viewing new and existing tags
- Database management controls

## Architecture

### Threading Design

The application uses a multi-threaded architecture for optimal performance and responsiveness:

1. **Main Thread (GUI)**:

```python
def main():
    root = tk.Tk()
    data_queue = Queue()  # Thread-safe queue for communication

    # Start RFID reader thread
    reader_thread = threading.Thread(
        target=rfid_reader_thread,
        args=(data_queue,),
        daemon=True  # Thread will stop when main program exits
    )
    reader_thread.start()

    # Create GUI
    gui = RFIDGui(root, data_queue)
    root.mainloop()
```

2. **Reader Thread**:

```python
def rfid_reader_thread(data_queue):
    reader = RFIDReader()
    db = RFIDDatabase()

    while True:
        # Read tags (non-blocking)
        tags = reader.read_tags()

        if tags:
            for tag in tags:
                # Process tag data
                db.record_tag(tag)

                # Send to GUI via queue
                data_queue.put({
                    "type": "new_tag",
                    "data": tag
                })

        time.sleep(0.1)  # Prevent CPU overuse
```

3. **Thread Communication**:

```python
def update_gui(self):
    """Update GUI with data from the queue"""
    try:
        while self.data_queue.qsize():
            msg = self.data_queue.get_nowait()
            if msg["type"] == "new_tag":
                # Update GUI with new tag data
                self.update_tag_display(msg["data"])
    finally:
        # Schedule next update
        self.root.after(100, self.update_gui)
```

The threading architecture provides:

- **Non-blocking UI**: The GUI remains responsive while reading tags
- **Continuous Reading**: Tags are read continuously without interruption
- **Thread Safety**: Data is passed safely between threads using a queue
- **Clean Termination**: Daemon thread ensures clean program exit

Key components:

- **Queue**: Thread-safe communication between reader and GUI
- **Daemon Thread**: Automatically terminates with main program
- **Non-blocking Updates**: Periodic GUI updates without blocking
- **Thread Safety**: Separated database and GUI operations

This design ensures:

- Responsive user interface
- Continuous tag reading capability
- Safe data handling between threads
- Proper resource management

## Database Structure

The SQLite database maintains two main tables:

- `tags`: Stores unique tag information and history
- `readings`: Records individual tag readings

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the RFID reader manufacturer for providing the DLL
- Built with Python and Tkinter
- Uses SQLite for data storage
