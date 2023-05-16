#!/usr/bin/python3
"""
Send file(s) and/or folder(s) across the network
https://wingxel.github.io/website/index.html
"""

import json
import os
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

import util
from sender_utils import get_args


class Sender:
    def __init__(self, ip_address: str, port_address: int) -> None:
        """
        Init sender
        :param ip_address: Receiver IP address
        :param port_address: Receiver port number
        """
        self.__ip_address = ip_address
        self.__port_address = port_address
        self.client_socket = socket(AF_INET, SOCK_STREAM)

    def connect_to_receiver(self) -> bool:
        """
        Connect to the receiver
        :return:
        """
        try:
            self.client_socket.connect((self.__ip_address, self.__port_address))
            return True
        except Exception as error_data:
            print(f"An error_data occurred : {str(error_data)}")
            util.log_error(f"An error_data occurred (snd 1) : {str(error_data)}")
        return False

    def get_ip_address(self) -> str:
        """
        Get the current receiver IP address
        :return:
        """
        return self.__ip_address

    def get_port_address(self) -> int:
        """
        Get the current receiver port number
        :return:
        """
        return self.__port_address


def send_files(connection_socket: socket, metadata: dict, filename_to_send: str) -> None:
    """
    Send single file
    :param connection_socket: Connection to the receiver socket
    :param metadata: File information
    :param filename_to_send: File absolute path /home/user/Videos/Example.mp4
    :return:
    """
    # Create json object describing the file being sent
    head = json.dumps(metadata).encode()
    # Send file description
    connection_socket.send(head)
    # If the receiver agrees to receive the file (the file does not exist)
    ok = connection_socket.recv(1024)
    if ok.decode() == "ok":
        # Go ahead and send the file content
        print(f"Sending {os.sep.join(metadata['name'])}")
        with open(filename_to_send, "rb") as the_file:
            # 1024 bytes at a time
            data = the_file.read(1024)
            while data:
                # Send
                connection_socket.send(data)
                # Read next chunk
                data = the_file.read(1024)
            # Log when done sending a given file
            print(f"{datetime.now()} : Done sending {os.sep.join(metadata['name'])}")
            # Receiver requests the next file
            next_data = connection_socket.recv(1024)
            # Write log to file
            Thread(target=util.log_error, args=(f"{datetime.now()} : {next_data}",)).start()
    elif ok.decode() == "not":
        # If the receiver does not agree to receive the file (file exists) skip the file
        print(f"{datetime.now()} : File already exists : {os.sep.join(metadata['name'])}")


def main(ip_address: str, port_number: int, files: list) -> None:
    """
    Main program
    :param ip_address: Receiver IP address
    :param port_number: Receiver process port number
    :param files: List of file(s) and/or folder(s) to send to the receiver
    :return:
    """
    the_sender = Sender(ip_address, port_number)
    if the_sender.connect_to_receiver():
        # Iterate over all the provided files/folders
        for abs_file_path in files:
            # If folder is provided and the path has path seperator at the end (/)
            # remove it
            if abs_file_path.endswith(os.sep):
                abs_file_path = os.sep.join(abs_file_path.split(os.sep)[0:len(abs_file_path.split(os.sep)) - 1:1])
            # Check if the file or folder exists
            if os.path.exists(abs_file_path):
                # For file
                if os.path.isfile(abs_file_path):
                    # Get file info
                    print(f"{datetime.now()} : Getting file metadata. Please wait...")
                    metadata_d = {
                        "name": [os.path.basename(abs_file_path)],
                        "size_d": os.path.getsize(abs_file_path),
                        "size": os.path.getsize(abs_file_path)
                    }
                    # Send file metadata and file content
                    send_files(the_sender.client_socket, metadata_d, abs_file_path)
                # For folder
                elif os.path.isdir(abs_file_path):
                    print(f"{datetime.now()} : Getting file metadata. Please wait...")
                    # Get folder size
                    directory_size = util.get_dir_size(abs_file_path)
                    # Walk the folder to get to files
                    for folder_path, folder_list, filenames_list in os.walk(abs_file_path):
                        for filename_item in filenames_list:
                            # Don't send empty files
                            if os.path.getsize(os.path.join(folder_path, filename_item)) > 0:
                                # Get each file path relative to the folder being sent in a list of folders
                                # example [folder_being_sent, sub-folder1, sub-folder2, file.ext]
                                # to help recreate the folder structure in the receiver end.
                                root = folder_path.split(os.sep)[
                                       folder_path.split(os.sep).index(abs_file_path.split(os.sep)[-1]):len(
                                           folder_path.split(os.sep)
                                       ):1]
                                # Append base filename
                                root.append(filename_item)
                                # Create file description
                                metadata_d = {
                                    "name": root,
                                    "size_d": directory_size,
                                    "size": os.path.getsize(os.path.join(folder_path, filename_item))
                                }
                                # Send file metadata and file content
                                send_files(
                                    the_sender.client_socket,
                                    metadata_d, os.path.join(folder_path, filename_item)
                                )
            else:
                print(f"{abs_file_path} : File or directory not found!")
    try:
        # Cleanup
        the_sender.client_socket.shutdown(2)
        the_sender.client_socket.close()
    except Exception as error:
        util.log_error(str(error))


if __name__ == "__main__":
    # Get commandline arguments
    arguments = get_args()
    main(arguments["address"], arguments["port"], arguments["files"])
