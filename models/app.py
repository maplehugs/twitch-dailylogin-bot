import os
from flask import Flask, render_template
from flask_socketio import SocketIO

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, '..', 'templates')

app = Flask(__name__, template_folder=TEMPLATES_DIR)
socketio = SocketIO(app, cors_allowed_origins="*")

# ---- Socket.IO Events ----
@socketio.on('connect')
def test_connect():
    print("🟢 A client connected")

@socketio.on("new_message")
def handle_message(msg):
    print("Received from client:", msg)
    # Rebroadcast to all web clients
    socketio.emit("new_message", msg)

# ---- Routes ----
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
