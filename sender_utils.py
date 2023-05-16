"""
Sender utility functions and consts
"""
import argparse
import re
import sys


# IP address regex
IP_REGEX = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
# Port number regex
PORT_REGEX = re.compile(r"^\d{4,5}$")


def check_if_ip_valid(ip: str) -> bool:
    """
    Check if the entered IP address is valid
    :param ip: IP provided in commandline
    :return:
    """
    tokens = ip.split(".")
    for token in tokens:
        cr = int(token)
        if cr > 255 or cr < 0:
            return False
    return True


def check_if_port_valid(port_number: int) -> bool:
    """
    Check if provided port number is valid - 1025-65535
    :param port_number: number to check
    :return:
    """
    return 1025 <= port_number < 65536


def get_args() -> dict:
    """
    Get commandline arguments for sender script
    :return:
    """
    parser = argparse.ArgumentParser(
        prog="Sender",
        description="Send files and/or folders across network",
        epilog="python3 Sender.py -a receiver.ip.address -p receiver_port_number -f list_of_file(s)_or/and_folder(s)"
    )

    parser.add_argument(
        "-a", "--address", required=True,
        help="The IP address of the machine where Receiver is running"
    )
    parser.add_argument(
        "-p", "--port", required=True,
        help="The Receiver process network port number"
    )
    parser.add_argument(
        "-f", "--files", required=True, nargs="+",
        help="The list of file(s) and/or folder(s) to send to the Receiver"
    )

    args = parser.parse_args()
    ip_address = args.address

    if not len(IP_REGEX.findall(ip_address)) == 1 or not check_if_ip_valid(ip_address):
        sys.exit(f"Invalid IP address {ip_address}")

    port_number = args.port
    if not len(PORT_REGEX.findall(port_number)) == 1 or not check_if_port_valid(int(port_number)):
        sys.exit(f"Invalid port number {port_number}")

    return {
        "address": ip_address,
        "port": int(port_number),
        "files": args.files
    }
