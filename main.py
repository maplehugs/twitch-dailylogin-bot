from models import app, socketio, run_bot
import threading
import asyncio

def run_flask():
    print("🌍 Flask server starting at http://127.0.0.1:5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)

# Run Flask + SocketIO in a separate thread
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Run Twitch bot in the main thread
asyncio.run(run_bot())
