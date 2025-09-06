# Import modules
import time

from twitchAPI.chat import Chat, EventData, ChatMessage, ChatCommand
from twitchAPI.type import AuthScope, ChatEvent  # 'type' → 'types', added ChatEvent
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from dotenv import load_dotenv
import os
import socketio

sio = socketio.Client()

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

@sio.event
def connect():
    print("Connected to server")
    # Send a test message

@sio.event
def disconnect():
    print("Disconnected from server")

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



async def lurk_command(cmd: ChatCommand):

    await cmd.reply('huh?')

# End of commands.

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

    #Register Events
    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)

    #Register Commands

    chat.register_command('lurk', lurk_command)
    chat.register_command('say', say_command)

    # Start the chat bot
    chat.start()

    try:
        input('press ENTER to stop\n')
    finally:
        chat.stop()
        await bot.close()
