"""
Receiver utility functions and consts
https://wingxel.github.io/website/index.html
"""

import argparse
import os
import sys
from pathlib import Path
from socket import socket, AF_INET, SOCK_STREAM

import util

# The default folder to save received items
DEFAULT_SAVE_FOLDER = os.sep.join([str(Path.home()), "SharePY3"])
# Port list to choose default port from
LIST_OF_PORTS_TO_USE = [8000, 8001, 1578, 1233, 2578, 31293, 4319, 42780, 1783, 3301, 1890, 1234,
                        1901, 6490, 61514, 14312]
# If the script is run on android device
if os.path.exists("/sdcard/"):
    DEFAULT_SAVE_FOLDER = os.sep.join(["", "sdcard", "SharePy3"])


def port_is_available(port: int) -> bool:
    """
    Check if provided port is available for use
    :param port: 
    :return: 
    """
    try:
        checker = socket(AF_INET, SOCK_STREAM)
        checker.connect(("", port))
        checker.close()
        return False
    except Exception as error:
        util.log_error(str(error))
    return True


def get_available_port() -> int:
    """
    Get available port
    :return: 
    """
    for p in LIST_OF_PORTS_TO_USE:
        if port_is_available(p):
            return p
    return 0


def get_receiver_args() -> dict:
    """
    Get receiver commandline arguments
    :return:
    """
    parser = argparse.ArgumentParser(
        prog="Receiver",
        description="Receive file from the network",
        epilog="python3 Receiver.py -p port_number -s folder_to_save_received_file(s)_and/or_folder(s)"
    )

    parser.add_argument(
        "-p", "--port", default=str(get_available_port()),
        help=f"Port address to use for receiving, if not {get_available_port()} will be used"
    )
    parser.add_argument(
        "-s", "--save", default=DEFAULT_SAVE_FOLDER,
        help=f"Folder to save received items, if not provided {DEFAULT_SAVE_FOLDER} will be used"
    )

    args = parser.parse_args()

    port_number = args.port
    if not len(util.PORT_REGEX.findall(port_number)) == 1 or not util.check_if_port_valid(int(port_number)):
        sys.exit(f"Invalid port number {port_number}")

    save_folder = args.save
    if os.path.exists(save_folder) and os.path.isfile(save_folder):
        sys.exit(f"{save_folder} should be a folder")

    if not os.path.exists(save_folder):
        try:
            os.makedirs(save_folder)
        except Exception as error:
            sys.exit(f"Error creating folder {save_folder}\n{str(error)}")

    return {
        "port": int(port_number),
        "folder": save_folder
    }
