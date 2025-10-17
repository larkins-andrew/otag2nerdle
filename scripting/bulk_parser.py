import json

cards = []
card_index = {}
with open('all-cards-20251014214010.json') as f:
    bulk_cards = json.load(f)

for card in bulk_cards:
    if card["reprint"] == True:
        continue
    if "paper" not in card["games"]:
        continue
    if card["layout"] in ["token", "emblem", "art_series", "double_faced_token", "vanguard"]:
        continue
    if card['set_type'] in ['token', 'memorabilia', 'minigame', 'treasure_chest', 'planechase', 'archenemy']:
        continue
    if card['lang'] != 'en':
        continue
    if "image_uris" in card.keys():
        url = card["image_uris"]["normal"]
        url_crop = card["image_uris"]["art_crop"]
    
    elif "card_faces" in card.keys():
        # print(card["uri"])
        url      = card["card_faces"][0]["image_uris"]["normal"]
        url_crop = card["card_faces"][0]["image_uris"]["art_crop"]

    if card["name"] in card_index.keys():
        if card['promo'] == False:
            cards[card_index[card["name"]]] = {"name": card["name"], "uri": url, "uri_crop": url_crop}
    else:
        card_index[card["name"]] = len(cards)
        cards.append({"name": card["name"], "uri": url, "uri_crop": url_crop})

with open("../card_data/formatted-cards.json", "w") as f:
    json.dump(cards, f)