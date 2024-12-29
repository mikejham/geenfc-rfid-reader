# RFID Tag Reader Application

## Overview

This application provides a user-friendly way to read and manage RFID (Radio-Frequency Identification) tags using a USB RFID reader. It features a modern graphical interface that displays tag information in real-time and stores historical data.

## Features

- 🔄 Real-time tag reading and display
- 📊 Historical tag data tracking
- 💾 Automatic data storage in a local database
- 📈 Signal strength monitoring
- 🎨 Modern, easy-to-use interface
- 📱 Separate views for new and existing tags
- 🗑️ Database management tools

## Requirements

### Hardware

- A compatible USB RFID reader (GEENFC E series UHF RFID Reader)
- RFID tags to read
- Windows computer with available USB port

### Software

- Python 3.7 or higher
- Windows operating system
- Required Python packages (install using `pip install -r requirements.txt`):
  - tkinter (usually comes with Python)
  - sqlite3 (usually comes with Python)
- RFID Reader DLL (`SWHidApi.dll`) - included in the project directory

## Installation

1. **Clone or Download the Repository**

   ```bash
   git clone [repository-url]
   cd rfid-reader
   ```

2. **Install Required Packages**

   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Files**

   - Ensure all required files are present in the project directory:
     - `main.py`
     - `reader.py`
     - `database.py`
     - `gui.py`
     - `SWHidApi.dll`

4. **Connect the RFID Reader**
   - Plug the USB RFID reader into your computer
   - Wait for Windows to recognize the device

## Running the Application

1. **Start the Program**

   ```bash
   python main.py
   ```

2. **Using the Interface**

   - The application will automatically:
     - Initialize the RFID reader
     - Create the database (if it doesn't exist)
     - Open the main window

3. **Reading Tags**

   - Hold an RFID tag near the reader
   - The tag information will appear in the "New Tags" tab
   - Historical data will be shown in the "Existing Tags" tab

4. **Managing Data**
   - Use the "Clear Database" button to remove all stored tag data
   - A confirmation dialog will appear before clearing

## Understanding the Display

### Status Section

- Shows the current reader status
- Displays total number of unique tags read

### Latest Read Section

- Shows information about the most recently read tag
- Includes tag ID and signal strength

### Tags Tabs

1. **New Tags Tab**

   - Shows tags read in the current session
   - Displays:
     - Tag ID
     - First seen time
     - Last seen time
     - Signal strength

2. **Existing Tags Tab**
   - Shows all historical tag readings
   - Same information as New Tags tab
   - Ordered by most recent first

## Technical Details

### Application Structure

The application is split into three main components:

1. **Main Module** (`main.py`)

   - Application entry point
   - Sets up the GUI and reader threads
   - Manages communication between components

2. **Reader Module** (`reader.py`)

   - Handles RFID reader communication
   - Processes tag data
   - Calculates signal strength
   - Runs in a separate thread

3. **Database Module** (`database.py`)
   - Manages the SQLite database
   - Stores tag information
   - Tracks first and last seen times
   - Handles data queries

### Data Storage

- Uses SQLite database (`rfid_readings.db`)
- Stores:
  - Unique tag IDs
  - First seen timestamp
  - Last seen timestamp
  - Signal strength information
  - Antenna and reader details

### Signal Strength Calculation

- Raw values range from 0x82 to 0xA0
- Converted to percentage for easier understanding
- Higher percentage = stronger signal

## Troubleshooting

### Common Issues

1. **Reader Not Found**

   - Check USB connection
   - Verify the reader is powered on
   - Ensure `SWHidApi.dll` is in the same directory as the Python files
   - Try unplugging and reconnecting the reader

2. **No Tags Appearing**

   - Make sure tags are within range (usually within a few inches)
   - Check if the reader is beeping when tags are present
   - Verify the status message shows "Waiting for tags..."
   - Try moving the tag closer to the reader's antenna

3. **Database Issues**
   - Check if the application has write permissions in the current directory
   - Try clearing the database using the "Clear Database" button
   - If database becomes corrupted, delete `rfid_readings.db` and restart the application

### Error Messages

- "Failed to load DLL": Verify `SWHidApi.dll` is in the same directory as the Python files
- "No USB Device": Check reader connection and Windows Device Manager
- "Failed to connect reader": Try unplugging and reconnecting the reader, or restart the application

### Performance Tips

- Keep the reader and tags away from metal objects
- Maintain clear line of sight between reader and tags
- For best results, hold tags 2-6 inches from the reader
- If readings are inconsistent, try adjusting the tag's orientation

## Support and Contribution

### Getting Help

- Check the troubleshooting section
- Review error messages in the terminal
- Contact technical support

### Contributing

- Fork the repository
- Make your changes
- Submit a pull request
- Follow the coding style guidelines

## License

[Insert License Information]

## Acknowledgments

- GEENFC for the RFID reader and SDK
- Contributors and testers
- [Add any other acknowledgments]

## Version History

- 1.0.0: Initial release
  - Basic tag reading
  - Database storage
  - GUI interface

---

_Note: This application is designed for Windows systems and requires specific hardware. Please ensure all requirements are met before installation._
