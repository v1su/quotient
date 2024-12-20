import os
import json
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import ChannelInvalidError
from datetime import datetime, timedelta

# Telegram configuration from environment variables
API_ID = os.getenv('API_ID')  # API ID of your Telegram application
API_HASH = os.getenv('API_HASH')  # API Hash of your Telegram application
SESSION_STRING = os.getenv('SESSION_STRING')  # Telethon session string
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')  # Username of your Telegram channel

# Check if environment variables are loaded correctly
if not all([API_ID, API_HASH, SESSION_STRING, CHANNEL_USERNAME]):
    print("Error: Missing environment variables.")
    exit()

# Define the output file for the quotes
QUOTES_FILE = "quotes.json"

client = TelegramClient(StringSession(SESSION_STRING), api_id=API_ID, api_hash=API_HASH)
client.start()

# Improved English placeholder quote
PLACEHOLDER_QUOTE = "`I didn't find anything in my author's diary! I'm still waiting for his thoughts on this day.`"

# Function to fetch the last 7 posts from the channel
async def fetch_last_7_posts(client, channel_username):
    try:
        # Ensure the channel exists by getting its entity using the username
        entity = await client.get_entity(channel_username)
        messages = await client.get_messages(entity, limit=7)
        quotes = []
        for msg in messages:
            if msg.text:
                quotes.append({"quote": msg.text, "date": None})
        return quotes[::-1]  # Reverse to maintain chronological order
    except ChannelInvalidError:
        print(f"Error: Channel with username {channel_username} is invalid or does not exist.")
        return []

# Function to get the dates for the next week, starting from Sunday
def get_next_week_dates():
    # Get the current date
    today = datetime.today()
    # Calculate how many days to subtract to get to the previous Sunday
    days_to_subtract = today.weekday() + 1  # Monday = 0, Sunday = 6
    start_of_week = today - timedelta(days=days_to_subtract)
    
    next_week_dates = []
    for i in range(7):
        next_day = start_of_week + timedelta(days=i)
        next_week_dates.append(next_day.strftime("%Y-%m-%d"))
    
    return next_week_dates

# Function to update the quotes file with messages for the next week
async def update_quotes_file():
    # Fetch the last 7 posts from the Telegram channel
    messages = await fetch_last_7_posts(client, CHANNEL_USERNAME)
    
    # Get the dates for the next week, starting from Sunday
    next_week_dates = get_next_week_dates()

    # Prepare the data to save
    quotes_data = []
    for idx, date in enumerate(next_week_dates):
        quote = (
            messages[idx]["quote"]
            if idx < len(messages)
            else PLACEHOLDER_QUOTE  # Use placeholder if there aren't enough messages
        )
        quotes_data.append({"quote": quote, "date": date})

    # Save the quotes to a JSON file
    with open(QUOTES_FILE, "w") as f:
        json.dump(quotes_data, f, indent=4)

    print(f"Updated quotes for the next week and saved to {QUOTES_FILE}")

# Run the script
if __name__ == "__main__":
    import asyncio
    asyncio.run(update_quotes_file())
