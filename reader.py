"""
RFID Reader Module
=================

This module handles communication with the RFID reader hardware through the provided DLL.
It manages the initialization, configuration, and continuous reading of RFID tags.

Features:
    - USB device detection and connection
    - Tag data reading and parsing
    - Signal strength calculation
    - Threaded operation for non-blocking reads
    - Error handling and recovery

Dependencies:
    - ctypes: For DLL interaction
    - database: For data storage
    - queue: For thread communication
"""

import ctypes
from ctypes import *
import time
from datetime import datetime
import os
import sys
from typing import Dict, List, Optional, Any
from queue import Queue
from database import RFIDDatabase
from logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


def get_dll_path() -> str:
    """
    Get the appropriate path for the DLL file, handling both development
    and PyInstaller bundled environments.

    Returns:
        str: Path to the SWHidApi.dll file
    """
    if getattr(sys, "frozen", False):
        # Running in PyInstaller bundle
        dll_path = os.path.join(sys._MEIPASS, "SWHidApi.dll")
    else:
        # Running in normal Python environment
        dll_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "SWHidApi.dll"
        )

    logger.debug(f"DLL path resolved to: {dll_path}")
    return dll_path


# Get the DLL path based on the execution environment
DLL_PATH = get_dll_path()


def format_tag_data(
    tag_type: str, antenna: str, tag_id: str, rssi: str
) -> Dict[str, str]:
    """
    Format raw tag data into a standardized dictionary format.

    Args:
        tag_type: Hexadecimal string representing the tag type
        antenna: Hexadecimal string representing the antenna number
        tag_id: Space-separated hexadecimal string of the tag ID
        rssi: Hexadecimal string representing signal strength

    Returns:
        Dict containing formatted tag data
    """
    try:
        # Convert RSSI to percentage (assuming 0x82 to 0xa0 range)
        rssi_int = int(rssi, 16)
        rssi_min = 0x82
        rssi_max = 0xA0
        rssi_percent = (
            ((rssi_int - rssi_min) / (rssi_max - rssi_min)) * 100
            if rssi_int >= rssi_min
            else 0
        )

        # Format tag ID without leading 0x and spaces
        tag_id_clean = "".join([x.replace("0x", "").zfill(2) for x in tag_id.split()])

        formatted_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "type": tag_type,
            "antenna": antenna,
            "tag_id": tag_id_clean,
            "rssi_hex": rssi,
            "rssi_percent": f"{rssi_percent:.1f}%",
        }

        logger.debug(f"Formatted tag data: {formatted_data}")
        return formatted_data
    except Exception as e:
        logger.error(f"Error formatting tag data: {e}")
        raise


class RFIDReader:
    """Interface for the RFID reader hardware."""

    def __init__(self, dll_path: str):
        """Initialize the RFID reader interface."""
        self.dll_path = dll_path
        self.dll = None
        self.db = RFIDDatabase()
        logger.info(f"RFIDReader initialized with DLL path: {dll_path}")

    def initialize(self) -> bool:
        """Load and initialize the reader's DLL."""
        try:
            self.dll = ctypes.windll.LoadLibrary(self.dll_path)
            logger.info("Successfully loaded RFID reader DLL")
            return True
        except Exception as e:
            logger.error(f"Failed to load DLL: {e}")
            return False

    def get_device_count(self) -> int:
        """Get the number of connected USB devices."""
        count = self.dll.SWHid_GetUsbCount()
        logger.info(f"Found {count} USB device(s)")
        return count

    def open_device(self, device_index: int = 0) -> bool:
        """Open and initialize a specific RFID reader device."""
        result = self.dll.SWHid_OpenDevice(device_index) == 1
        if result:
            logger.info(f"Successfully opened RFID reader at index {device_index}")
        else:
            logger.error(f"Failed to open RFID reader at index {device_index}")
        return result

    def start_reading(self) -> bool:
        """Start the tag reading operation."""
        try:
            logger.debug("Clearing tag buffer before starting read")
            self.dll.SWHid_ClearTagBuf()

            logger.debug("Attempting to start continuous read")
            result = self.dll.SWHid_StartRead() == 1

            if result:
                logger.info("Successfully started tag reading")
            else:
                logger.error("Failed to start tag reading")
            return result
        except Exception as e:
            logger.error(f"Error starting tag reading: {e}")
            return False

    def stop_reading(self) -> bool:
        """Stop the tag reading operation and close the device."""
        try:
            self.dll.SWHid_StopRead()
            self.dll.SWHid_CloseDevice()
            logger.info("Successfully stopped tag reading and closed device")
            return True
        except Exception as e:
            logger.error(f"Error stopping reader: {e}")
            return False

    def read_tags(self) -> List[Dict[str, str]]:
        """Read and parse available tags from the reader's buffer."""
        try:
            arrBuffer = bytes(9182)
            iTagLength = c_int(0)
            iTagNumber = c_int(0)

            ret = self.dll.SWHid_GetTagBuf(
                arrBuffer, byref(iTagLength), byref(iTagNumber)
            )

            logger.debug(
                f"GetTagBuf return value: {ret}, TagNumber: {iTagNumber.value}, TagLength: {iTagLength.value}"
            )

            # Return value 2 indicates successful read with tags
            # Return value 1 indicates successful read but no tags
            # Return value 0 or other indicates error
            if ret != 2:
                logger.debug(f"No tags found in buffer (return code: {ret})")
                return []

            tags = []
            if iTagNumber.value > 0:
                logger.debug(f"Found {iTagNumber.value} tags in buffer")
                iLength = 0
                for tag_index in range(iTagNumber.value):
                    try:
                        bPackLength = arrBuffer[iLength]
                        logger.debug(
                            f"Tag {tag_index + 1} packet length: {bPackLength}"
                        )

                        # Get Tag Type
                        tag_type = hex(arrBuffer[1 + iLength + 0])
                        logger.debug(f"Tag {tag_index + 1} type: {tag_type}")

                        # Get Antenna
                        antenna = hex(arrBuffer[1 + iLength + 1])
                        logger.debug(f"Tag {tag_index + 1} antenna: {antenna}")

                        # Get Tag ID
                        tag_id = ""
                        for i in range(2, bPackLength - 1):
                            tag_id += hex(arrBuffer[1 + iLength + i]) + " "
                        logger.debug(f"Tag {tag_index + 1} raw ID: {tag_id}")

                        # Get RSSI
                        rssi = hex(arrBuffer[1 + iLength + bPackLength - 1])
                        logger.debug(f"Tag {tag_index + 1} RSSI: {rssi}")

                        # Dump raw buffer for debugging
                        raw_data = " ".join(
                            [
                                hex(x)
                                for x in arrBuffer[iLength : iLength + bPackLength + 1]
                            ]
                        )
                        logger.debug(f"Tag {tag_index + 1} raw buffer: {raw_data}")

                        # Format the data
                        tag_data = format_tag_data(
                            tag_type, antenna, tag_id.strip(), rssi
                        )
                        tags.append(tag_data)

                        logger.debug(
                            f"Successfully read tag {tag_index + 1}: {tag_data}"
                        )

                        # Update length for next tag
                        iLength = iLength + bPackLength + 1
                    except Exception as e:
                        logger.error(f"Error processing tag {tag_index + 1}: {e}")
                        continue

            return tags
        except Exception as e:
            logger.error(f"Error reading tags: {e}")
            return []


def rfid_reader_thread(data_queue: Queue) -> None:
    """Background thread function for continuous tag reading."""
    logger.info("Starting RFID reader thread")

    try:
        reader = RFIDReader(DLL_PATH)
        db = RFIDDatabase()

        # Initialize reader
        data_queue.put({"type": "status", "message": "Initializing reader..."})
        if not reader.initialize():
            msg = "Failed to initialize reader"
            logger.error(msg)
            data_queue.put({"type": "status", "message": msg})
            return

        # Check for devices
        device_count = reader.get_device_count()
        msg = f"Found {device_count} USB device(s)"
        logger.info(msg)
        data_queue.put({"type": "status", "message": msg})

        if device_count == 0:
            msg = "No USB Device"
            logger.error(msg)
            data_queue.put({"type": "status", "message": msg})
            return

        # Open device
        if not reader.open_device():
            msg = "Failed to connect reader"
            logger.error(msg)
            data_queue.put({"type": "status", "message": msg})
            return

        msg = "Reader connected"
        logger.info(msg)
        data_queue.put({"type": "status", "message": msg})

        # Start reading
        if not reader.start_reading():
            msg = "Failed to start reading"
            logger.error(msg)
            data_queue.put({"type": "status", "message": msg})
            return

        msg = "Waiting for tags..."
        logger.info(msg)
        data_queue.put({"type": "status", "message": msg})

        read_count = 0
        while True:
            try:
                read_count += 1
                if read_count % 100 == 0:  # Log every 100th read attempt
                    logger.debug(f"Read attempt {read_count}")

                tags = reader.read_tags()
                if tags:
                    logger.info(f"Found {len(tags)} tags in this read cycle")

                for tag_data in tags:
                    if db.record_tag(tag_data):
                        logger.info(f"New tag detected: {tag_data['tag_id']}")
                        data_queue.put({"type": "new_tag", "data": tag_data})
                        data_queue.put({"type": "count", "count": db.get_tag_count()})
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in tag reading loop: {e}")
                continue

    except Exception as e:
        msg = f"Error: {e}"
        logger.error(msg)
        data_queue.put({"type": "status", "message": msg})
    finally:
        try:
            reader.stop_reading()
            msg = "Reader disconnected"
            logger.info(msg)
            data_queue.put({"type": "status", "message": msg})
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
