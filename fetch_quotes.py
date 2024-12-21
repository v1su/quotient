import os
import json
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import ChannelInvalidError
from datetime import datetime, timedelta
import asyncio

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

# Improved English placeholder quote
PLACEHOLDER_QUOTE = "`I didn't find anything in my author's diary! I'm still waiting for his thoughts on this day.`"

# Function to fetch the last 7 posts from the channel
async def fetch_last_7_posts(client, channel_username):
    try:
        # Ensure the client is connected before fetching messages
        if not client.is_connected():
            await client.connect()
        
        # Ensure the channel exists by getting its entity using the username
        entity = await client.get_entity(channel_username)
        messages = await client.get_messages(entity, limit=7)
        
        # Collect the messages
        quotes = []
        for msg in messages:
            if msg.text:
                quotes.append({"quote": msg.text, "date": None})
        
        return quotes[::-1]  # Reverse to maintain chronological order
    except ChannelInvalidError:
        print(f"Error: Channel with username {channel_username} is invalid or does not exist.")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

# Function to get the dates for the next week, starting from the previous Sunday
def get_next_week_dates():
    # Get the current date
    today = datetime.today()

    # Calculate how many days to subtract to get to the previous Sunday
    days_to_subtract = today.weekday() + 1  # Monday = 0, Sunday = 6
    start_of_previous_week = today - timedelta(days=days_to_subtract)

    # Generate the next week's dates starting from the next Sunday after the previous Sunday
    next_week_dates = []
    for i in range(7):
        next_day = start_of_previous_week + timedelta(days=(i + 7))  # Shift by 7 days for the next week
        next_week_dates.append(next_day.strftime("%Y-%m-%d"))

    return next_week_dates

# Function to update the quotes file with messages for the next week
async def update_quotes_file():
    # Fetch the last 7 posts from the Telegram channel
    messages = await fetch_last_7_posts(client, CHANNEL_USERNAME)
    
    # Get the dates for the next week, starting from the previous Sunday
    next_week_dates = get_next_week_dates()

    # Load existing data from the JSON file
    if os.path.exists(QUOTES_FILE):
        with open(QUOTES_FILE, "r") as f:
            quotes_data = json.load(f)
    else:
        quotes_data = []

    # Prepare the new data entries
    new_quotes = []
    for idx, date in enumerate(next_week_dates):
        quote = (
            messages[idx]["quote"]
            if idx < len(messages)
            else PLACEHOLDER_QUOTE  # Use placeholder if there aren't enough messages
        )
        
        # Check if this date is already in the existing quotes
        existing_quote = next((item for item in quotes_data if item["date"] == date), None)
        if existing_quote:
            # If it exists, overwrite the quote for this date
            existing_quote["quote"] = quote
        else:
            # If it doesn't exist, add a new entry
            new_quotes.append({"quote": quote, "date": date})

    # Append new quotes to the existing data
    quotes_data.extend(new_quotes)

    # Sort quotes_data by date to maintain chronological order
    quotes_data = sorted(quotes_data, key=lambda x: x['date'])

    # Save the updated data back to the JSON file
    with open(QUOTES_FILE, "w") as f:
        json.dump(quotes_data, f, indent=4)

    print(f"Updated quotes for the next week and saved to {QUOTES_FILE}")

# Run the script with proper event loop management
if __name__ == "__main__":
    loop = asyncio.get_event_loop()  # Get the existing event loop
    loop.run_until_complete(update_quotes_file())  # Run the asynchronous function
