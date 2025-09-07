from models import app, socketio, run_bot
import threading
import asyncio
from models.sqlite import sqlite

# -----------------------------
# Test the daily check-in system
# -----------------------------
# def test_checkin():
#     checkin_system = sqlite()  # uses default paths
#     user_id = "user123"
#
#     success, message = checkin_system.checkin(user_id)
#     print(f"[Test] {message}")
#
#     # Fetch last check-in info
#     last_date, last_username, last_image = checkin_system.get_last_checkin(user_id)
#     print(f"[Test] Last check-in: {last_date}, username: {last_username}, image: {last_image}")
#
# # Run the test
# test_checkin()
#
def run_flask():
    print("🌍 Flask server starting at http://127.0.0.1:5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)

# Run Flask + SocketIO in a separate thread
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Run Twitch bot in the main thread
asyncio.run(run_bot())
