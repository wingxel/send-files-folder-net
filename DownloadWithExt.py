#!/usr/bin/python3

"""
Scrap webpage for images with provided extensions and download them.
https://wingxel.github.io/website/index.html
"""

import os
import sys
import getopt
import requests

from pathlib import Path
from bs4 import BeautifulSoup
from Downloader import download


def usage() -> None:
	print("""
-u or --url		URL to download from.
-s or --save	Where to put the downloaded files.
-e or --ext		Extension to look for.
-h or --help	Print this help text.
""")


def get_args() -> dict:
	user_args = {"url": "", "save": os.path.join(Path.home(), "Pictures"), "ext": ""}
	try:
		opts, _ = getopt.getopt(sys.argv[1:], "u:s:e:h", ["url=", "save=", "ext=", "help"])
		for opt, arg in opts:
			if opt in ["-h", "--help"]:
				usage()
				sys.exit(0)
			if opt in ["-s", "--save"]:
				user_args["save"] = arg
			if opt in ["-e", "--ext"]:
				user_args["ext"] = arg
			if opt in ["-u", "--url"]:
				user_args["url"] = arg
	except getopt.GetoptError as err:
		print(f"Error processing arguments : {str(err)}")
	return user_args

def main() -> None:
	provided_args = get_args()
	if len(provided_args["url"]) > 0 and len(provided_args["ext"]) > 0:
		if not os.path.exists(provided_args["save"]):
			try:
				os.makedirs(provided_args["save"])
			except Exception as error:
				print("Error creating directory {provided_args['save']} \n {str(error)}")
				sys.exit(0)
		page = requests.get(provided_args["url"])
		soup = BeautifulSoup(page.text, "html.parser")
		links = soup.findAll("a")
		imgs = soup.findAll("img")

		links_data = []
		for link in links:
			try:
				if link.get("href").endswith(provided_args["ext"]):
					links_data.append(link.get("href"))
			except Exception as err:
				print(f"Error: {str(err)}")

		imgs_data = []
		for img in imgs:
			try:
				if img.get("src").endswith(provided_args["ext"]):
					imgs_data.append(img.get("src"))
			except Exception as err:
				print(f"Error: {str(err)}")

		if len(links_data) > 0:
			for link in links_data:
				res = download(os.path.join(provided_args["url"], link), provided_args["save"])
				if not res:
					download(link, provided_args["save"])

		if len(imgs_data) > 0:
			for img in imgs_data:
				res = download(os.path.join(provided_args["url"], img), provided_args["save"])
				if not res:
					download(img, provided_args["save"])
		print("Done...........")
	else:
		usage()


if __name__ == "__main__":
	main()
