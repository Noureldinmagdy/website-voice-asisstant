# server.py
import os
from livekit import api
from flask import Flask
from flask import request, jsonify, send_from_directory, abort
from flask_cors import CORS
from dotenv import load_dotenv
from livekit.api import (
  AccessToken,
  RoomAgentDispatch,
  RoomConfiguration,
  VideoGrants,
)
import json

from flask_socketio import SocketIO
from flask_socketio import join_room, leave_room



load_dotenv(".env.local")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)


socketio = SocketIO(cors_allowed_origins="*")
socketio.init_app(app)


@app.route('/getToken', methods=['POST'])
def getToken():
    data = request.get_json() 
    print("Received data:", data)
    data = data["data"]
    token = api.AccessToken(os.getenv('LIVEKIT_API_KEY'), os.getenv('LIVEKIT_API_SECRET')) \
        .with_identity(data['userId']) \
        .with_name(data['userId']) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=data['room'],
        )).with_room_config(
            RoomConfiguration(
                agents=[RoomAgentDispatch(agent_name="electropi-agent", 
                                          metadata=json.dumps(data))]
            )
        )
    print("Generated Token:", token.to_jwt())
    return {
        "serverUrl": os.getenv('LIVEKIT_URL'),
        "participantToken": token.to_jwt()
    }



@app.route('/scripts/<path:filename>', methods=['GET'])
def serve_script(filename):
    # Serve JS files from the local `scripts` directory only
    scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
    # Protect against path traversal
    safe_path = os.path.abspath(os.path.join(scripts_dir, filename))
    if not safe_path.startswith(os.path.abspath(scripts_dir) + os.sep):
        abort(404)
    if not os.path.exists(safe_path):
        abort(404)
    # Always return as JavaScript
    return send_from_directory(scripts_dir, filename, mimetype='application/javascript', as_attachment=False)


active_rooms = set()
user_connection_counts = {}
sid_to_user = {}


@socketio.on('connect')
def connect():
    print("+++++++++ new connected user ")
    args = request.args

    sid = request.sid

    user_id = args.get('user_id')
    website = args.get('website_name')

    join_room(user_id)

    # track connection
    sid_to_user[sid] = user_id
    user_connection_counts[user_id] = user_connection_counts.get(user_id, 0) + 1
    active_rooms.add(user_id)
    print("============", user_id, website)

@socketio.on('disconnect')
def disconnect():
    sid = request.sid
    user_id = sid_to_user.pop(sid, None)
    if not user_id:
        return
    # decrement count and remove room when no connections left
    user_connection_counts[user_id] -= 1
    if user_connection_counts[user_id] <= 0:
        user_connection_counts.pop(user_id, None)
        active_rooms.discard(user_id)


@app.route('/events/click', methods=['POST'])
def events_click():
    data = request.get_json() 

    user_id = data["user_id"]
    xpath = data["xpath"]

    # verify room exists / user connected
    if user_id not in active_rooms:
        return jsonify({"error": "room/user not connected"}), 404

    socketio.emit("click", {"xpath": xpath}, room=user_id)

    return {"response": "succfully sent!"}


@app.route('/events/send-input', methods=['POST'])
def events_send_input():
    data = request.get_json() 

    user_id = data["user_id"]
    xpath = data["xpath"]
    value = data["value"]

    # verify room exists / user connected
    if user_id not in active_rooms:
        return jsonify({"error": "room/user not connected"}), 404

    socketio.emit("send-input", {"xpath": xpath, "value": value}, room=user_id)

    return {"response": "succfully sent!"}




if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
