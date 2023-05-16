# Python Sender and Receiver Scripts

Send and receive file(s) and/or folder(s) across a network.
***

Run Sender.py
```shell
python3 Sender.py -a receiver_ip_address \ 
  -p receiver_port_number \ 
  -f list_of_files_and_or_folders
```
***

Run Receiver.py
```shell
python3 Receiver.py -p port_number_to_use \ 
  -s /folder/where/to/save/received/items/
```
Receiver can be run without commandline arguments
