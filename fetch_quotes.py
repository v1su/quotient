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

# Improved English placeholder quote
PLACEHOLDER_QUOTE = "`I didn't find anything in my author's diary! I'm still waiting for his thoughts on this day.`"

async def fetch_quotes_from_telegram():    
    try:
        # Start the client
        await client.start()

        # Get the channel using its username
        channel = await client.get_entity(CHANNEL_USERNAME)

        # Fetch messages (quotes) from the channel, adjust the limit as needed
        messages = await client.get_messages(channel, limit=7)  # Adjust the limit based on how many quotes you need

        # Get today's date and calculate the start of the current week (Sunday)
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday() + 1)  # Sunday of the current week

        # Initialize an empty list for quotes
        quotes = []

        # Calculate the next Sunday starting from the start of the week
        next_sunday = start_of_week + timedelta(days=7)

        # Loop through the upcoming 7 days starting from next Sunday
        for i in range(7):
            target_date = next_sunday + timedelta(days=i)
            # Search for a message that corresponds to the target date
            found_quote = False
            for message in messages:
                if message.date.date() == target_date.date() and message.text:
                    quotes.append({
                        "quote": message.text,
                        "date": target_date.strftime("%Y-%m-%d")
                    })
                    found_quote = True
                    break
            
            # If no post was found for the day, add a placeholder quote with improved English
            if not found_quote:
                quotes.append({
                    "quote": PLACEHOLDER_QUOTE,
                    "date": target_date.strftime("%Y-%m-%d")
                })

        # Save quotes to a JSON file
        with open(QUOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(quotes, f, ensure_ascii=False, indent=4)

        print(f"Fetched and saved {len(quotes)} quotes.")

    except ChannelInvalidError:
        print(f"Error: Channel {CHANNEL_USERNAME} does not exist or is invalid.")
    
    finally:
        # Disconnect the client
        await client.disconnect()

# Run the script
if __name__ == "__main__":
    import asyncio
    asyncio.run(fetch_quotes_from_telegram())