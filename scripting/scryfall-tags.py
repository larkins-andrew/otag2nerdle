import requests
import json
import time
import sqlite3
from scripting.tag_regex import get_tags

from scryfall_db import *

api_url = "https://api.scryfall.com"
search_url = "/cards/search"

header = {
    "Accept": "*/*",
    "User-Agent": "otag2nerdle"
}

tags = get_tags()

con = sqlite3.connect("card-tag.db")
cur = con.cursor()


for t in tags:
    page = 1
    more_page = True

    while more_page:
        payload = {
            "q": f"oracletag:{t}",
            "page": page

        }
        r = requests.get(api_url + search_url, headers=header, params=payload)

        with open("scryfall-output.json", "w+") as f:
            f.write(r.text)

        obj = r.json()
        print(f"{t}, {page}")
        for c in obj["data"]:
            print(f"\t{c["name"]}\n\t\t{c["id"]}")

        if obj["has_more"] == False:
            more_page = False
        else:
            page += 1
        time.sleep(1)
