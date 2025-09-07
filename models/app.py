import os
from flask import Flask, render_template
from flask_socketio import SocketIO

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, '..', 'templates')
STATIC_DIR = os.path.join(BASE_DIR, '..', 'static')

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
socketio = SocketIO(app, cors_allowed_origins="*")

# -----------------------------
# Handle new chat messages
# -----------------------------
@socketio.on('new_message')
def handle_new_message(msg):
    print("Received new message:", msg)
    # Broadcast to all connected clients
    socketio.emit('new_message', msg)

# -----------------------------
# Handle daily login messages
# -----------------------------
@socketio.on('daily_login')
def handle_daily_login(msg):
    print("Received daily login:", msg)
    # Broadcast to all connected clients
    socketio.emit('daily_login', msg)

# -----------------------------
# Handle client connections
# -----------------------------
@socketio.on('connect')
def handle_connect():
    print("🟢 Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("❌ Client disconnected")

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)