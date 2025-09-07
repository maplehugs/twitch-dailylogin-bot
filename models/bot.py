# Import modules
import cmd

from twitchAPI.chat import Chat, EventData, ChatMessage, ChatCommand
from twitchAPI.type import AuthScope, ChatEvent  # 'type' → 'types', added ChatEvent
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from models.sqlite import sqlite
from dotenv import load_dotenv
from functools import partial
import socketio
import time
import os

# Sockets

sio = socketio.Client()


@sio.event
def connect():
    print("Connected to server")
    # Send a test message


@sio.event
def disconnect():
    print("Disconnected from server")


# Load and Start Database

checkin_system = sqlite()

# Load environment variables from .env file
load_dotenv()

# Constants from .env
APP_ID = os.getenv("CLIENT_ID")
APP_SECRET = os.getenv("CLIENT_SECRET")
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CHANNEL_MANAGE_BROADCAST]
TARGET_CHANNEL = os.getenv("CHANNEL")


async def on_message(message: ChatMessage):
    # Print username and chat message
    print(f'{message.user.display_name} - {message.text}')  # changed msg → message


async def on_ready(ready_event: EventData):
    # Connect to target channel
    await ready_event.chat.join_room(TARGET_CHANNEL)
    # Print
    print('Bot ready')


# Commands:

async def say_command(cmd: ChatCommand):
    # Send message to webpage
    print('Prameter: ' + cmd.parameter)
    sio.connect("http://localhost:5000")
    time.sleep(1)
    sio.emit("new_message", f"{cmd.user.name}: {cmd.parameter}")
    # send_message_to_web(f"{cmd.user.name}: {cmd.parameter}")
    sio.disconnect()
    # (Optional) Reply in Twitch chat
    # await cmd.reply('Message updated')


async def daily_command(cmd: ChatCommand, bot=None):
    # Send message to webpage
    print('Prameter: ' + cmd.parameter)

    online = await is_user_live(bot, "maplehugs")
    print(f"maplehugs | Online: {online} |")
    print(f"User: {cmd.user.name} Can check in? {checkin_system.can_checkin(cmd.user.name)}")

    if online and checkin_system.can_checkin(cmd.user.name):

        checkin_system.checkin(cmd.user.name)
        last_username, last_image, last_checkin, _ = checkin_system.get_user_info(cmd.user.name)

        await cmd.reply(
            f"Yay! You have a total of {last_checkin} check-ins! Keep it up!"
        )

        sio.connect("http://localhost:5000")
        time.sleep(1)
        sio.emit("daily_login", f"{cmd.user.name}: {cmd.parameter}")
        # send_message_to_web(f"{cmd.user.name}: {cmd.parameter}")
        sio.disconnect()
        # (Optional) Reply in Twitch chat
        # await cmd.reply('Message updated')

    if not checkin_system.can_checkin(cmd.user.name):

        last_username, last_image, last_checkin, _ = checkin_system.get_user_info(cmd.user.name)

        await cmd.reply(
            f"hmm?, seems like you have already checked in in this stream, but still, you have: {last_checkin} check-ins."
        )

    else:

        last_username, last_image, last_checkin, _ = checkin_system.get_user_info(cmd.user.name)

        await cmd.reply(
            f"huh?, maple doesn't seem to be online right now, but you have: {last_checkin} check-ins."
        )


async def lurk_command(cmd: ChatCommand):
    await cmd.reply('huh?')


# End of commands.

# Fetch streams info (pretty much just if its online or now)

async def is_user_live(bot, username: str):
    async for stream in bot.get_streams(user_login=[username]):
        return True
    return False


# Usage:
# online = await is_user_live(bot, "maplehugs")
# print(f"maplehugs | Online: {online}")

# Bot setup function
async def run_bot():
    # Authenticate application
    bot = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(bot, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await bot.set_user_authentication(token, USER_SCOPE, refresh_token)

    # Initialize chat class
    chat = await Chat(bot)
    chat.set_prefix('?')

    # Register Events
    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)

    # Register Commands

    online = await is_user_live(bot, "maplehugs")
    print(f"maplehugs | Online: {online} |")

    chat.register_command('lurk', lurk_command)
    chat.register_command('say', say_command)
    chat.register_command('daily', partial(daily_command, bot=bot))
    # Start the chat bot
    chat.start()

    try:

        input('press ENTER to stop\n')

    finally:
        chat.stop()
        await bot.close()
