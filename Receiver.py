#!/usr/bin/python3
"""
Receiver End
https://wingxel.github.io/website/index.html

Usage python3 Receiver.py Port file_saving_directory
"""

import json
import os
import sys
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

import util


def prep() -> bool:
    if not os.path.exists(util.save_location):
        try:
            os.mkdir(util.save_location)
            return True
        except Exception as error:
            util.log_error(f"Error making save file directory : {str(error)}")
            return False
    return True


def communicate(connection_socket: socket, client_address: tuple) -> None:
    print(f"Client Sending Files => {client_address} : {datetime.now()}")
    try:
        while util.receiving:
            head = json.loads(connection_socket.recv(1024).decode())
            d_s, directory_size = 0, head["size_d"]
            while d_s != directory_size:
                if not util.receiving:
                    break
                if len(head["name"]) > 1:
                    p = os.sep.join([util.save_location, os.sep.join(head["name"][0:len(head["name"]) - 1:1])])
                    try:
                        os.makedirs(p)
                    except FileExistsError as error:
                        util.log_error(f"An error occurred : {str(error)}")
                    except Exception as error:
                        util.log_error(f"An error occurred : {str(error)}")
                file_size, f_s = head["size"], 0
                save_file = os.sep.join([util.save_location, os.sep.join(head["name"])])
                if not os.path.exists(save_file):
                    connection_socket.send(b"ok")
                    with open(save_file, "wb") as the_file:
                        data = connection_socket.recv(1024)
                        while f_s != file_size:
                            f_s += len(data)
                            d_s += len(data)
                            the_file.write(data)
                            if f_s == file_size or not util.receiving:
                                break
                            data = connection_socket.recv(1024)
                    connection_socket.send(b"next")
                    """if d_s < directory_size:
                        connection_socket.send(b"next")"""
                else:
                    d_s += file_size
                    connection_socket.send(b"not")
                if d_s < directory_size:
                    head = json.loads(connection_socket.recv(1024).decode())
    except Exception as error_value:
        util.log_error(str(error_value))
    finally:
        print(f"Client Done => {client_address} : {datetime.now()}")
        print("Closing Connection...")
        connection_socket.close()


class Receiver:
    def __init__(self, port: int) -> None:
        self.__port_address = port
        self.server_socket = socket(AF_INET, SOCK_STREAM)

    def start(self) -> None:
        try:
            self.server_socket.bind(("", self.__port_address))
            self.__work()
        except Exception as error:
            print(f"An error occurred : {str(error)}")
            util.log_error(f"An error occurred (rc 1) : {str(error)}")

    def __work(self) -> None:
        try:
            self.server_socket.listen(10)
            print(f"Files will be saved at: {util.save_location}")
            print(f"Server started at port : {self.__port_address} : (Press ctrl+c to exit) Waiting...")
            util.log_error(f"Server started at port : {self.__port_address}")
            while True:
                try:
                    connection_socket, client_address = self.server_socket.accept()
                    print(f"Client Connected => {client_address} : {datetime.now()}")
                    t = Thread(target=communicate, args=(connection_socket, client_address))
                    t.start()
                except KeyboardInterrupt:
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
    if os.path.exists(util.log_file):
        try:
            os.remove(util.log_file)
        except Exception as error_d:
            print(f"Error cleaning : {str(error_d)}")
    if prep():
        arg_value = util.get_receiver_arg(sys.argv[1:])
        if len(arg_value["save"]) != 0 and os.path.exists(arg_value["save"]):
            util.save_location = arg_value["save"]
        if arg_value["port"] != 0:
            r = Receiver(arg_value["port"])
            r.start()
        else:
            util.usage_receiver()
    else:
        print("Check the log file for errors")
