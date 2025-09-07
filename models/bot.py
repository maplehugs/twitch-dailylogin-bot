import asyncio
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatCommand
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from models.sqlite import sqlite
from dotenv import load_dotenv
from functools import partial
import socketio
import os

# -----------------------------
# Socket.IO
# -----------------------------
sio = socketio.AsyncClient()

@sio.event
async def connect():
    print("✅ Connected to Socket.IO server")

@sio.event
async def disconnect():
    print("❌ Disconnected from Socket.IO server")

# -----------------------------
# Database
# -----------------------------
checkin_system = sqlite()

# Load .env
load_dotenv()
APP_ID = os.getenv("CLIENT_ID")
APP_SECRET = os.getenv("CLIENT_SECRET")
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CHANNEL_MANAGE_BROADCAST]
TARGET_CHANNEL = os.getenv("CHANNEL")

# -----------------------------
# Twitch Events
# -----------------------------
async def on_message(message: ChatMessage):
    print(f'{message.user.display_name} - {message.text}')

async def on_ready(ready_event: EventData):
    await ready_event.chat.join_room(TARGET_CHANNEL)
    print("Bot ready")

# -----------------------------
# Commands
# -----------------------------
async def say_command(cmd: ChatCommand):
    print("Sending:", cmd.parameter)
    if sio.connected:
        await sio.emit("new_message", f"{cmd.user.name}: {cmd.parameter}")
    else:
        print("⚠️ Socket.IO not connected")


async def daily_command(cmd: ChatCommand, bot=None):
    print("Daily command:", cmd.parameter)

    # Check if user is live
    online = await is_user_live(bot, "maplehugs")

    # Get user info from database
    username, image, checkin_count, last_checkin = checkin_system.get_user_info(cmd.user.name)
    can_checkin = checkin_system.can_checkin(cmd.user.name)

    # Reply in Twitch chat depending on status
    if online and can_checkin:
        checkin_system.checkin(cmd.user.name)
        # Get updated user info from database
        username, image, checkin_count, last_checkin = checkin_system.get_user_info(cmd.user.name)
        await cmd.reply(f"Yay! Total check-ins: {checkin_count}")

        # -----------------------------
        # Emit to Socket.IO safely
        # -----------------------------

        if sio.connected:
            print(username, image, checkin_count, last_checkin)
            try:
                # If last_image is None or empty, skip emitting
                if image:
                    await sio.emit("daily_login", image)
                    print(f"✅ Sent daily_login: {image}")
                else:
                    print("⚠️ No image to send")
            except Exception as e:
                print("⚠️ Error emitting daily_login:", e)
        else:
            print("⚠️ Socket.IO not connected")

    elif not can_checkin:
        await cmd.reply(f"Already checked in! Total check-ins: {checkin_count}")
    else:
        await cmd.reply(f"Maple not online, check-ins: {checkin_count}")




async def lurk_command(cmd: ChatCommand):
    await cmd.reply("huh?")

# -----------------------------
# Helper
# -----------------------------
async def is_user_live(bot, username: str):
    async for stream in bot.get_streams(user_login=[username]):
        return True
    return False

# -----------------------------
# Bot setup
# -----------------------------
async def run_bot():
    # Connect Socket.IO once
    await sio.connect("http://localhost:5000")

    # Authenticate Twitch
    bot = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(bot, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await bot.set_user_authentication(token, USER_SCOPE, refresh_token)

    # Setup chat
    chat = await Chat(bot)
    chat.set_prefix("?")
    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)
    chat.register_command("lurk", lurk_command)
    chat.register_command("say", say_command)
    chat.register_command("daily", partial(daily_command, bot=bot))

    # Start chat in background thread
    chat.start()

    # Keep the bot alive without blocking the async loop
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        chat.stop()
        await bot.close()
        await sio.disconnect()
        print("Bot and Socket.IO disconnected")

# -----------------------------
# Run (Stand alone just in case)
# -----------------------------
if __name__ == "__main__":
    asyncio.run(run_bot())
