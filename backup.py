#!/usr/bin/python3
"""
Backup script
https://wingxel.github.io/website/index.html
"""
import getopt
import os
import shutil
import sys
from datetime import datetime

import util

opts = ()

try:
    opts, _ = getopt.getopt(sys.argv[1:], "s:d:h", ["source=", "destination=", "help"])
except getopt.GetoptError as err:
    print(f"An error occurred : {str(err)}")

source_dir = "__"
destination_dir = os.path.join(os.environ.get("HOME"), os.sep.join(["Documents", "projects", "backups",
                                                                    f"SenderData{datetime.now()}"]))

for opt, arg in opts:
    if opt in ["-h", "--help"]:
        util.print_user_backup()
        sys.exit(0)
    if opt in ["-s", "--source"]:
        source_dir = arg
    if opt in ["-d", "--destination"]:
        destination_dir = arg

if not os.path.exists(source_dir):
    util.print_user_backup()
    sys.exit(1)

try:
    shutil.copytree(source_dir, destination_dir)
    print("Done doing backup......")
except Exception as error:
    print(f"An error occurred : {str(error)}")
    util.log_error(f"An error occurred (bcp 1) : {str(error)}")
