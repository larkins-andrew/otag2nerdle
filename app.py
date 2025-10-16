from flask import Flask, render_template, jsonify, current_app, request, abort, json

from tag_check import tagMatch, getTags, genTags, genUri, getUri
import argparse

app = Flask('app')

@app.route('/api/restart')
def restart():
  init_vars()
  return render_template('index.html')

@app.route('/')
def index():
  return render_template('index.html')

def bad_guess(card: str, err_msg: str):
  global strikes
  global guess_status
  
  guess_status = card
  strikes = strikes - 1 if strikes > 0 else 0
  return jsonify({"description": err_msg})

@app.route('/api/play', methods=["GET"])
def api_play():
  global last_card
  global active_player
  global used_cards
  global tag_strikes
  global event_timeline
  global guess_status
  global strikes

  name = request.args.get("name")
  time = request.args.get("time")
  time = int(time) if time else None
  uid = request.args.get("uid")
  uid = int(uid) if uid else None

  if uid == None or uid != active_player:
    abort(406, description=f"Not active player ({uid}, not {active_player})!")
  
  if time == None or time > len(event_timeline):
    if time and len(event_timeline) < time:
      return render_template('index.html')
    else:
      abort(406, description=f"No time passed!")
  
  
  if name == None:
    abort(406, description="No Name Provided!")
  name = name.lower()

  if strikes <= 0:
    return bad_guess(name, "All Guesses Used!")

  if name in used_cards:
    return bad_guess(name, "Card Already Used!")
    # guess_status = name
    # abort(406, description="Card Already Used!")

  tags = tagMatch(name, last_card)
  if tags == set():
    return bad_guess(name, "Card Tags Don't Match!")
    # guess_status = name
    # abort(406, description="Card Tags Don't Match!")
  
  strike_flag = 0 #set to 1 if no tag has <3 hits
  unused_tags = []
  for tag in tags:
    if tag in tag_strikes:
      if tag_strikes[tag] < 3:
        tag_strikes[tag] += 1
        unused_tags.append(tag)
    else:
      tag_strikes[tag] = 1
      unused_tags.append(tag)
  
  if len(unused_tags) == 0:
    return bad_guess(name, f"{tag} at 3 strikes!")
    # guess_status = name
    # abort(406, description=f"{tag} at 3 strikes!")
  
  last_card = name
  used_cards.add(name)
  active_player = 1 if active_player == 0 else 0
  guess_status = ""
  strikes = 3

  event_timeline.append({
    'name': name,
    'uri': getUri(name),
    'tags': [[tag, tag_strikes[tag]] for tag in unused_tags]
  })
  
  return jsonify({'description': "&nbsp;"})

@app.route('/api/update', methods=["GET"])
def api_update():
  global guess_status
  global strikes
  global event_timeline

  time = request.args.get("time")
  time = int(time) if time else None
  if time == None or time > len(event_timeline):
    if time and len(event_timeline) < time:
      # abort(406, description=f"Invalid time: {time}, timeline is size {len(event_timeline)}!")
      return render_template('index.html')
    else:
      abort(406, description=f"No time passed!")
  return jsonify({'data': event_timeline[time:len(event_timeline)],
                  'time': len(event_timeline),
                  'guess_status': f"{guess_status}" if guess_status != "" else "&nbsp;",
                  'strikes': strikes
                })

@app.errorhandler(406)
def custom406(error):
  global guess_status

  response = error.get_response()
  response.data = json.dumps({
    "code": error.code,
    "name": error.name,
    "description": error.description
  })
  return response

def init_vars():
  global active_player
  global starting_card
  global last_card
  global tag_strikes
  global event_timeline
  global used_cards
  global guess_status
  global strikes

  active_player = 0
  starting_card = "forest"
  last_card = starting_card
  used_cards = set()
  used_cards.add(starting_card)
  tag_strikes = {}
  guess_status = ""
  strikes=3

  event_timeline = [
    {
      'name': starting_card,
      'uri': getUri(starting_card),
      'tags': []
    }
  ]
  return

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-l", "--local", help="Run server locally", action='store_true')
  args = parser.parse_args()

  genUri()
  genTags()
  init_vars()
  if args.local:
    app.run()
  else:
    app.run(host='0.0.0.0', port=8080)
