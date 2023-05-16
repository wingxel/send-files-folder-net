"""
Services
https://wingxel.github.io/website/index.html
"""

import getopt
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from socket import socket, AF_INET, SOCK_STREAM

save_location = os.sep.join([str(Path.home()), "SharePY3"])
log_location = os.sep.join([str(Path.home()), ".FileSharePY3_Log"])
log_file = os.sep.join([log_location, "log_data.log"])
receiving = True
ip_regex = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
port_regex = re.compile(r"\d{4}")
probable_ports = [8000, 8001, 1578, 1233, 2578, 31293, 4319, 42780, 1783, 3301, 1890, 1234,
                  1901, 6490, 61514, 14312]

# Port number regex
PORT_REGEX = re.compile(r"^\d{4,5}$")


def check_if_port_valid(port_number: int) -> bool:
    """
    Check if provided port number is valid - 1025-65535
    :param port_number: number to check
    :return:
    """
    return 1025 <= port_number < 65536


if os.path.exists("/sdcard/"):
    save_location = os.sep.join(["", "sdcard", "SharePy3"])


def log_error(what_to_log: str) -> None:
    if not os.path.exists(log_location):
        try:
            os.mkdir(log_location)
        except Exception as error:
            print(f"Error setting the logs {str(error)}")
            return
    else:
        with open(log_file, "a") as logger:
            print(f"{datetime.now()} : {what_to_log}", file=logger)


def get_dir_size(filename: str) -> int:
    s = 0
    for r, ds, fs in os.walk(filename):
        for f in fs:
            s += os.path.getsize(os.path.join(r, f))
    return s


def port_is_available(port: int) -> bool:
    try:
        checker = socket(AF_INET, SOCK_STREAM)
        checker.connect(("", port))
        checker.close()
        return False
    except Exception as error:
        log_error(str(error))
    return True


def print_user_backup() -> None:
    print(""""Usage: 
backup.py -s source_dir -d destination_dir
-s or --source          : source directory or file.
-d or --destination     : destination directory.
-h or --help            : this help text.""")


def mark(d: int) -> None:
    print(f"At => {d}")


def get_metadata(filename: str) -> dict:
    metadata = {}
    if os.path.isfile(filename):
        metadata["name"] = os.path.basename(filename)
    return metadata


def check_if_ip_valid(ip: str) -> bool:
    tokens = ip.split(".")
    for token in tokens:
        cr = int(token)
        if cr > 255 or cr < 0:
            return False
    return True


def usage_sender() -> None:
    print(f"""Usage:
-f or --file               : file and directory.
-a or --address            : ip address for receiver.
-p or --port               : receiver process address.
-h or --help               : this help text.
Example
./Sender.py -a receiver_ip -p receiver_port -f directory_1 -f directory_2 -f file_1 -f directory_3""")


def usage_receiver() -> None:
    print("""Usage:
-p or --port                : port to listen at.
-s or --save                : where to save the received files.
-h or --help                : this help text.
Example:
./Receiver.py -p 8001""")


def get_sender_args(arguments: list) -> dict:
    try:
        opts, _ = getopt.getopt(arguments, "a:p:f:h", ["address=", "port=", "file=", "help"])
    except getopt.GetoptError as err:
        log_error(str(err))
        usage_sender()
        sys.exit(1)

    files = []
    ip_a_address = ""
    port_a_address = 0

    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            usage_sender()
            sys.exit(0)
        if opt in ["-a", "--address"]:
            if len(ip_regex.findall(arg)) == 1 and check_if_ip_valid(arg):
                ip_a_address = arg
            else:
                print(f"Invalid IP address : {arg}")
        if opt in ["-p", "--port"]:
            try:
                port_a_address = int(arg)
                if port_a_address < 1 or port_a_address > 65535:
                    port_a_address = 0
                    raise ValueError(f"Invalid port number : {arg}")
            except ValueError as error:
                print(f"Error : {str(error)}")
        if opt in ["-f", "--file"]:
            files.append(arg)

    return {
        "data": files,
        "ip": ip_a_address,
        "port": port_a_address
    }


def get_av_port() -> int:
    for p in probable_ports:
        if port_is_available(p):
            return p
    return 0


def get_receiver_arg(arguments: list) -> dict:
    try:
        opts, _ = getopt.getopt(arguments, "p:s:h", ["port=", "save=", "help"])
    except getopt.GetoptError as err:
        log_error(str(err))
        usage_receiver()
        sys.exit(1)
    port = 0
    save = ""
    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            usage_receiver()
            sys.exit(0)
        if opt in ["-p", "--port"]:
            try:
                port = int(arg)
                if not port_is_available(port):
                    port = 0
                    raise ValueError(f"{port} is already in use by another process.\n")
                if port < 1025 or port > 65536:
                    port = 0
                    raise ValueError(f"Port {port} is invalid or reserved for system use.\n")
            except ValueError as err:
                print(f"Invalid port : {arg} : {str(err)}")
                usage_receiver()
                print("\nUsing default port...")
        if opt in ["-s", "--save"]:
            if os.path.exists(arg):
                save = arg
    if port == 0:
        port = get_av_port()
    return {
        "port": port,
        "save": save
    }
