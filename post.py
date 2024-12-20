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

# Process the quote and replace backticks with double quotes
quote_text = quote_of_the_day["quote"].replace("`", '"').capitalize()

# Create an image for the quote
def create_quote_image(quote_text):
    # Image settings
    width, height = 1080, 1080
    text_color = "#FFFFFF"
    gradient_start = (30, 87, 153)  # Blue
    gradient_end = (125, 185, 232)  # Light Blue

    # Font settings
    font_path = "./assets/fonts/Roboto-Regular.ttf"  # Path to your provided font
    quote_font_size = 120  # Adjusted font size for quote
    signature_font_size = 100  # Same size for signature as well

    try:
        quote_font = ImageFont.truetype(font_path, quote_font_size)
    except IOError:
        print(f"Font file not found at {font_path}. Using default font.")
        quote_font = ImageFont.load_default()

    # Create a blank image with gradient background
    image = Image.new("RGB", (width, height))
    for y in range(height):
        r = gradient_start[0] + (gradient_end[0] - gradient_start[0]) * y // height
        g = gradient_start[1] + (gradient_end[1] - gradient_start[1]) * y // height
        b = gradient_start[2] + (gradient_end[2] - gradient_start[2]) * y // height
        for x in range(width):
            image.putpixel((x, y), (r, g, b))

    draw = ImageDraw.Draw(image)

    # Text wrapping for the quote
    lines = []
    words = quote_text.split(" ")
    line = ""
    for word in words:
        bbox = draw.textbbox((0, 0), line + word, font=quote_font)
        if bbox[2] < width - 100:  # 50px padding on each side
            line += word + " "
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)

    # Calculate total text height
    line_height = 100
    text_height = len(lines) * line_height

    # Position text in the center
    y = (height - text_height) // 2 - 50
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=quote_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), line, fill=text_color, font=quote_font)
        y += line_height

    # Add signature below the quote with the same font
    signature_text = "@QuotientOfLife"  # Signature remains as provided
    bbox = draw.textbbox((0, 0), signature_text, font=quote_font)
    signature_width = bbox[2] - bbox[0]
    signature_x = (width - signature_width) // 2
    signature_y = y + 50
    draw.text((signature_x, signature_y), signature_text, fill=text_color, font=quote_font)

    return image

# Generate the image
quote_image = create_quote_image(quote_text)
image_path = "quote_of_the_day.jpg"
quote_image.save(image_path)

print(f"Quote image created: {image_path}")

# Post to Telegram asynchronously
async def post_to_telegram():
    try:
        bot = Bot(token=BOT_TOKEN)
        with open(image_path, "rb") as photo:
            # Remove backticks from caption and replace with double quotes
            caption = f"{quote_text}\n\n✍🏻 Join @QuotientOfLife for your daily dose of inspiration and wisdom!"
            caption = caption.replace("`", '"')  # Ensure backticks are replaced by double quotes in caption
            await bot.send_photo(chat_id=CHAT_ID, photo=photo, caption=caption)
        print("Quote posted successfully!")
    except Exception as e:
        print(f"Error posting quote to Telegram: {e}")

# Run the async function
asyncio.run(post_to_telegram())
