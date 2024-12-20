import os
import json
from telethon.sync import TelegramClient
from telethon.tl.types import PeerChannel

# Telegram configuration from environment variables
API_ID = os.getenv('API_ID')  # API ID of your Telegram application
API_HASH = os.getenv('API_HASH')  # API Hash of your Telegram application
SESSION_STRING = os.getenv('TELETHON_SESSION_STRING')  # Telethon session string
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')  # Username of your Telegram channel

# Define the output file for the quotes
QUOTES_FILE = "quotes.json"

# Function to fetch quotes from Telegram channel
def fetch_quotes_from_telegram():
    # Initialize the Telethon client
    client = TelegramClient(session=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
    
    async def main():
        await client.start()

        # Get the channel
        channel = await client.get_entity(PeerChannel(CHANNEL_USERNAME))
        
        # Fetch messages (quotes) from the channel, adjust the limit as needed
        messages = await client.get_messages(channel, limit=100)  # Adjust the limit based on how many quotes you need

        quotes = []
        for message in messages:
            quotes.append(message.text)

        # Save quotes to a JSON file
        with open(QUOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(quotes, f, ensure_ascii=False, indent=4)

        print(f"Fetched {len(quotes)} quotes from the channel.")

    # Run the client to fetch quotes
    client.loop.run_until_complete(main())

# Run the script
if __name__ == "__main__":
    fetch_quotes_from_telegram()
