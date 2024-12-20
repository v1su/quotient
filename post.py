import os
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from telegram import Bot
import asyncio

# Load environment variables for bot token and chat ID
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("Please set the environment variables BOT_TOKEN and CHAT_ID.")
    exit()

# Load today's date
today = datetime.now().strftime("%Y-%m-%d")

# Load quotes from JSON file
try:
    with open("quotes.json", "r") as file:
        quotes = json.load(file)
except FileNotFoundError:
    print("quotes.json file not found!")
    exit()

# Find the quote for today
quote_of_the_day = next((q for q in quotes if q["date"] == today), None)

if not quote_of_the_day:
    print(f"No quote scheduled for today ({today}).")
    exit()

# Create an image for the quote
def create_quote_image(quote_text):
    # Image settings
    width, height = 1080, 1080
    background_color = "#1E1E2C"
    text_color = "#FFFFFF"

    # Set the font path to the .otf file uploaded to the repo
    font_path = "./assets/fonts/font.otf"  # Ensure this is the correct path
    font_size = 60  # Set a larger font size

    try:
        font = ImageFont.truetype(font_path, font_size)  # Use the custom .otf font
    except IOError:
        print(f"Font file not found at {font_path}. Using default font.")
        font = ImageFont.load_default()

    # Create a blank image
    image = Image.new("RGB", (width, height), color=background_color)
    draw = ImageDraw.Draw(image)

    # Text wrapping
    lines = []
    words = quote_text.split(" ")
    line = ""
    for word in words:
        bbox = draw.textbbox((0, 0), line + word, font=font)
        if bbox[2] < width - 100:  # 50px padding on each side
            line += word + " "
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)

    # Adjust the line height for bigger spacing
    line_height = 70  # Adjust the line spacing (increase this value)

    # Calculate total text height
    text_height = len(lines) * line_height

    # Position text in the center
    y = (height - text_height) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), line, fill=text_color, font=font)
        y += line_height  # Add more space between lines

    return image

# Generate the image
quote_image = create_quote_image(quote_of_the_day["quote"])
image_path = "quote_of_the_day.jpg"
quote_image.save(image_path)

print(f"Quote image created: {image_path}")

# Post to Telegram asynchronously
async def post_to_telegram():
    try:
        bot = Bot(token=BOT_TOKEN)
        with open(image_path, "rb") as photo:
            await bot.send_photo(chat_id=CHAT_ID, photo=photo, caption="Quote of the Day")
        print("Quote posted successfully!")
    except Exception as e:
        print(f"Error posting quote to Telegram: {e}")

# Run the async function
asyncio.run(post_to_telegram())
