"""
Common utility functions
https://wingxel.github.io/website/index.html
"""

import os
import re
from datetime import datetime
from pathlib import Path


# Folder where the log file is at
LOG_FILE_LOCATION = os.sep.join([str(Path.home()), ".FileSharePY3_Log"])
# The log file
LOG_FILE = os.sep.join([LOG_FILE_LOCATION, "log_data.log"])

# If the receiver is busy
receiving = True

# Port number regex
PORT_REGEX = re.compile(r"^\d{4,5}$")


def check_if_port_valid(port_number: int) -> bool:
    """
    Check if provided port number is valid - 1025-65535
    :param port_number: number to check
    :return:
    """
    return 1025 <= port_number < 65536


def log_error(what_to_log: str) -> None:
    """
    Write log
    :param what_to_log: Log message
    :return:
    """
    if not os.path.exists(LOG_FILE_LOCATION):
        try:
            os.mkdir(LOG_FILE_LOCATION)
        except Exception as error:
            print(f"Error setting the logs {str(error)}")
            return
    else:
        with open(LOG_FILE, "a") as logger:
            print(f"{datetime.now()} : {what_to_log}", file=logger)


def get_dir_size(the_folder: str) -> int:
    """
    Get folder size
    :param the_folder: absolute path
    :return:
    """
    s = 0
    for r, ds, fs in os.walk(the_folder):
        for f in fs:
            s += os.path.getsize(os.path.join(r, f))
    return s


def mark(d: int) -> None:
    """
    Print logs to screen
    :param d:
    :return:
    """
    print(f"At => {d}")


def get_metadata(filename: str) -> dict:
    """
    Get file base name
    :param filename: file absolute path
    :return:
    """
    metadata = {}
    if os.path.isfile(filename):
        metadata["name"] = os.path.basename(filename)
    return metadata
