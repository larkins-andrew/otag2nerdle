from tracemalloc import start
from flask import Flask, render_template, jsonify, current_app, request, abort, json

from tag_check import tagMatch, getTags, genTags, genUri, getUri


app = Flask('app')

active_player = 0

genUri()
genTags()

starting_card = "forest"
last_card = starting_card
used_cards = set(starting_card)
tag_strikes = {}

event_timeline = [
  {
    'name': starting_card,
    'uri': getUri(starting_card),
    'tags': []
  }
]


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/api/play', methods=["GET"])
def api_play():
  global last_card
  global active_player
  global used_cards
  global tag_strikes
  global event_timeline

  name = request.args.get("name")
  time = request.args.get("time")
  time = int(time) if time else None
  uid = request.args.get("uid")
  uid = int(uid) if uid else None
  if uid == None or uid != active_player:
    abort(406, description=f"Not active player ({uid}, not {active_player})!")
  if time == None or time > len(event_timeline):
    if time and len(event_timeline) < time:
      abort(406, description=f"Invalid time: {time}, timeline is size {len(event_timeline)}!")
    else:
      abort(406, description=f"No time passed!")
  if name == None:
    abort(406, description="No Name Provided!")
  name = name.lower()

  if name in used_cards:
    abort(406, description="Card Already Used!")

  tags = tagMatch(name, last_card)
  if tags == set():
    print(getTags(name))
    print(getTags(last_card))
    abort(406, description="Card Tags Don't Match!")
  
  strike_flag = 0 #set to 1 if no tag has <3 hits
  for tag in tags:
    if tag in tag_strikes:
      if tag_strikes[tag] > 3:
        abort(406, descrption=f"{tag} at 3 strikes!")
      tag_strikes[tag] += 1
    else:
      tag_strikes[tag] = 1

  last_card = name
  used_cards.add(name)
  active_player = 1 if active_player == 0 else 0

  event_timeline.append({
    'name': name,
    'uri': getUri(name),
    'tags': [[tag, tag_strikes[tag]] for tag in tags]
  })
  print(getUri(name))
  return jsonify({'data': event_timeline[time:len(event_timeline)], 'time': len(event_timeline)})

@app.route('/api/update', methods=["GET"])
def api_update():
  time = request.args.get("time")
  time = int(time) if time else None
  if time == None or time > len(event_timeline):
    if time and len(event_timeline) < time:
      abort(406, description=f"Invalid time: {time}, timeline is size {len(event_timeline)}!")
    else:
      abort(406, description=f"No time passed!")
  return jsonify({'data': event_timeline[time:len(event_timeline)], 'time': len(event_timeline)})

@app.errorhandler(406)
def custom406(error):
  response = error.get_response()
  response.data = json.dumps({
    "code": error.code,
    "name": error.name,
    "description": error.description,
  })
  return response

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)