import os
import json
import html
tags = {}
form_cards = "card_data/formatted-cards.json"
tag_dir = "card_data/tags/"

def genUri():
    global tags
    global form_cards
    with open(form_cards) as f:
        card_json = json.load(f)
    for c in card_json:
        name = c["name"].lower()
        uri = c["uri"]
        tags[name] = {"tags":set(), "uri":uri}

def genTags() -> None:
    global tags
    global tag_dir
    files = os.listdir(tag_dir)
    for file_name in files:
        with open(os.path.join(tag_dir,file_name), 'r') as f:
            card_json = json.load(f)
        tag_name = file_name[:-5]
        for c in card_json:
            if c.lower() in tags:
                tags[c.lower()]['tags'].add(tag_name)

def tagMatch(card1, card2) -> set:
    global tags
    try:
        return tags[card1]['tags'].intersection(tags[card2]['tags'])
    except:
        return set()

def getTags(card) -> set:
    global tags
    return tags[card]['tags']

def getUri(card) -> str:
    global tags
    return tags[card]['uri']

def genDatalist():
    with open("datalist.html", "w") as f:
        f.write(f'<datalist id="cardnames">')
        for n in tags.keys():
            f.write(f'<option value="{html.escape(n)}"></option>')
        f.write(f'</datalist>')

if __name__ == "__main__":
    genUri()
    genTags()
    genDatalist()