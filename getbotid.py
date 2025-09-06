import requests
from dotenv import load_dotenv
import os

load_dotenv()

BOT_USERNAME = os.getenv('BOT_NICK')
CLIENT_ID = os.getenv('CLIENT_ID')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

# ---- MAKE REQUEST TO TWITCH API ----
url = f'https://api.twitch.tv/helix/users?login={BOT_USERNAME}'
headers = {
    'Client-ID': CLIENT_ID,
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

response = requests.get(url, headers=headers)

# ---- CHECK RESPONSE ----
if response.status_code == 200:
    data = response.json()
    if 'data' in data and len(data['data']) > 0:
        bot_id = data['data'][0]['id']
        print(f"Your bot ID is: {bot_id}")
    else:
        print("Bot username not found.")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
