#!/usr/bin/python3

"""
File Downloader
https://wingxel.github.io/website/index.html
"""

import getopt
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

save_loc = str(Path.home())


def usage() -> None:
    print("""Usage:
-s or --save           : where to save the downloaded file.
-u or --url            : file download url.
-h or --help           : this help text.""")


def get_args() -> dict:
    info = {
        "save": save_loc,
        "url": ""
    }
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "s:u:h", ["save=", "url=", "help"])
        for opt, arg in opts:
            if opt in ["-h", "--help"]:
                usage()
                sys.exit(0)
            if opt in ["-s", "--save"]:
                if os.path.exists(arg) and not os.path.isfile(arg):
                    info["save"] = arg
            if opt in ["-u", "--url"]:
                info["url"] = arg
    except getopt.GetoptError as err:
        print(f"An error occurred : {str(err)}")
    return info


def download_file(url: str, sv: str) -> str:
    local_filename = os.path.join(sv, url.split('/')[-1])
    data = {
        "User-agent": "Mozilla/105.0"
    }
    if os.path.exists(local_filename):
        return local_filename
    with requests.get(url, stream=True, headers=data) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def download(url_to_download: str, sv: str) -> bool:
    try:
        print(f"{datetime.now()} : {url_to_download} : Started, please wait...")
        downloaded = download_file(url_to_download, sv)
        print(f"{datetime.now()} : Completed download of {downloaded}")
        return True
    except Exception as error:
        print(f"Download failed : {str(error)}")

    return False


def main() -> None:
    data = get_args()
    if len(data["url"]) == 0:
        usage()
    else:
        download(data["url"], data["save"])


if __name__ == '__main__':
    main()
