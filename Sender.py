#!/usr/bin/python3
"""
Sender data
https://wingxel.github.io/website/index.html
"""

import json
import os
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from sender_utils import get_args
import util


class Sender:
    def __init__(self, ip_address: str, port_address: int) -> None:
        self.__ip_address = ip_address
        self.__port_address = port_address
        self.client_socket = socket(AF_INET, SOCK_STREAM)

    def connect_to_receiver(self) -> bool:
        try:
            self.client_socket.connect((self.__ip_address, self.__port_address))
            return True
        except Exception as error_data:
            print(f"An error_data occurred : {str(error_data)}")
            util.log_error(f"An error_data occurred (snd 1) : {str(error_data)}")
        return False

    def get_ip_address(self) -> str:
        return self.__ip_address

    def get_port_address(self) -> int:
        return self.__port_address


def send_files(cl_socket: socket, metadata: dict, f_n: str) -> None:
    head = json.dumps(metadata).encode()
    cl_socket.send(head)
    ok = cl_socket.recv(1024)
    if ok.decode() == "ok":
        print(f"Sending {os.sep.join(metadata['name'])}")
        with open(f_n, "rb") as the_file:
            data = the_file.read(1024)
            while data:
                cl_socket.send(data)
                data = the_file.read(1024)
            print(f"{datetime.now()} : Done sending {os.sep.join(metadata['name'])}")
            next_data = cl_socket.recv(1024)
            Thread(target=util.log_error, args=(f"{datetime.now()} : {next_data}",)).start()
    elif ok.decode() == "not":
        print(f"{datetime.now()} : File already exists : {os.sep.join(metadata['name'])}")


def main(ip_ad: str, port_num: int, data_s: list) -> None:
    s = Sender(ip_ad, port_num)
    if s.connect_to_receiver():
        filenames = []
        if len(data_s) > 0:
            filenames.extend(data_s)
        else:
            n = input("Enter filename: ").strip()
            filenames.append(n)
        for f_name in filenames:
            if f_name.endswith(os.sep):
                f_name = os.sep.join(f_name.split(os.sep)[0:len(f_name.split(os.sep)) - 1:1])
            if os.path.exists(f_name):
                if os.path.isfile(f_name):
                    print(f"{datetime.now()} : Getting file metadata. Please wait...")
                    metadata_d = {
                        "name": [os.path.basename(f_name)],
                        "size_d": os.path.getsize(f_name),
                        "size": os.path.getsize(f_name)
                    }
                    send_files(s.client_socket, metadata_d, f_name)
                elif os.path.isdir(f_name):
                    print(f"{datetime.now()} : Getting file metadata. Please wait...")
                    directory_size = util.get_dir_size(f_name)
                    for r, ds, fs in os.walk(f_name):
                        for f in fs:
                            if os.path.getsize(os.path.join(r, f)) > 0:
                                root = r.split(os.sep)[
                                       r.split(os.sep).index(f_name.split(os.sep)[-1]):len(r.split(os.sep)):1]
                                root.append(f)
                                metadata_d = {
                                    "name": root,
                                    "size_d": directory_size,
                                    "size": os.path.getsize(os.path.join(r, f))
                                }
                                send_files(s.client_socket, metadata_d, os.path.join(r, f))
            else:
                print(f"{f_name} : File or directory not found!")
    try:
        s.client_socket.shutdown(2)
        s.client_socket.close()
    except Exception as error:
        util.log_error(str(error))


if __name__ == "__main__":
    arguments = get_args()
    main(arguments["address"], arguments["port"], arguments["files"])
