#!/usr/bin/python3
"""
Receive file(s) and/or folder(s) across the network
https://wingxel.github.io/website/index.html
"""

import json
import os
import sys
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import receiver_utils
import util


def communicate(connection_socket: socket, client_address: tuple) -> None:
    """
    Worker function handles incoming content
    :param connection_socket: Connection socket with the sending end
    :param client_address: Sender IP address
    :return:
    """
    print(f"Client Sending Files => {client_address} : {datetime.now()}")
    try:
        while util.receiving:
            # Receive each file description (metadata)
            head = json.loads(connection_socket.recv(1024).decode())
            # Disassemble some metadata to help track overall progress
            receive_progress_tracker, directory_size = 0, head["size_d"]
            # Keep receiving data until the expected directory size is reached
            while receive_progress_tracker != directory_size:
                # Exit if not receiving
                if not util.receiving:
                    break
                # Determine if the file currently being received should be put
                # in sub-folder(s)
                if len(head["name"]) > 1:
                    p = os.sep.join([
                        receiver_utils.DEFAULT_SAVE_FOLDER,
                        os.sep.join(head["name"][0:len(head["name"]) - 1:1])
                    ])
                    # Create the sub-folder(s) if they do not exist
                    try:
                        os.makedirs(p)
                    except FileExistsError as error:
                        util.log_error(f"An error occurred : {str(error)}")
                    except Exception as error:
                        util.log_error(f"An error occurred : {str(error)}")
                # Disassemble some metadata to help track individual file progress
                full_file_size, received_size = head["size"], 0
                # Create absolute destination file path
                save_file = os.sep.join([
                    receiver_utils.DEFAULT_SAVE_FOLDER,
                    os.sep.join(head["name"])
                ])
                # Check if the file with that name already exists
                if not os.path.exists(save_file):
                    # If not tell the sender to go ahead and start sending
                    connection_socket.send(b"ok")
                    # Open the destination file for writing binary
                    with open(save_file, "wb") as the_file:
                        # Receive first chunk
                        data = connection_socket.recv(1024)
                        # Keep receiving until file full size is reached
                        while received_size != full_file_size:
                            # Increment file size tracker
                            received_size += len(data)
                            # Increment overall progress
                            receive_progress_tracker += len(data)
                            # Save the received chunk into the opened file
                            the_file.write(data)
                            # If the expected file size is reached or the receiver has stopped,
                            # stop receiving and writing
                            if received_size == full_file_size or not util.receiving:
                                break
                            # Receive subsequent chunks
                            data = connection_socket.recv(1024)
                    connection_socket.send(b"next")
                    """if receive_progress_tracker < directory_size:
                        connection_socket.send(b"next")"""
                else:
                    # Increment the received folder size progress
                    receive_progress_tracker += full_file_size
                    # Tell the sender to skip that file because a file with that name already exists
                    connection_socket.send(b"not")
                if receive_progress_tracker < directory_size:
                    # Get metadata for the next file
                    head = json.loads(connection_socket.recv(1024).decode())
    except Exception as error_value:
        util.log_error(str(error_value))
    finally:
        # Cleanup
        print(f"Client Done => {client_address} : {datetime.now()}")
        print("Closing Connection...")
        connection_socket.close()


class Receiver:
    def __init__(self, port: int) -> None:
        """
        Init Receive server
        :param port: Receiver process port number
        """
        self.__port_address = port
        self.server_socket = socket(AF_INET, SOCK_STREAM)

    def start(self) -> None:
        """
        Start receive server
        :return:
        """
        try:
            self.server_socket.bind(("", self.__port_address))
            self.__work()
        except Exception as error:
            print(f"An error occurred : {str(error)}")
            util.log_error(f"An error occurred (rc 1) : {str(error)}")

    def __work(self) -> None:
        """
        Receive incoming items
        :return:
        """
        try:
            self.server_socket.listen(10)
            print(f"Files will be saved at: {receiver_utils.DEFAULT_SAVE_FOLDER}")
            print(f"Server started at port : {self.__port_address} : (Press ctrl+c to exit) Waiting...")
            util.log_error(f"Server started at port : {self.__port_address}")
            while True:
                try:
                    connection_socket, client_address = self.server_socket.accept()
                    print(f"Client Connected => {client_address} : {datetime.now()}")
                    # Each sender is handled by a different thread
                    t = Thread(target=communicate, args=(connection_socket, client_address))
                    t.start()
                except KeyboardInterrupt:
                    # Stopped receiving
                    util.receiving = False
                    print(f"{datetime.now()} : Server stopped")
                    try:
                        sys.exit(0)
                    except SystemExit:
                        return
        except KeyboardInterrupt:
            try:
                sys.exit(0)
            except SystemExit:
                return
        except Exception as error:
            print(f"An error occurred : {str(error)}")
            util.log_error(f"An error occurred (rc 2) : {str(error)}")


if __name__ == "__main__":
    # Prepare the log file
    if os.path.exists(util.LOG_FILE):
        try:
            os.remove(util.LOG_FILE)
        except Exception as error_d:
            print(f"Error cleaning : {str(error_d)}")

    # Get commandline arguments
    arguments = receiver_utils.get_receiver_args()
    # Set where to save received files
    receiver_utils.DEFAULT_SAVE_FOLDER = arguments["folder"]
    receiver = Receiver(arguments["port"])
    receiver.start()
