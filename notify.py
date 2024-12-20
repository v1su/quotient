import requests
import sys

def send_telegram_message(bot_token, chat_id, message):
    """
    Send a message to a specified Telegram chat.
    
    Args:
    - bot_token: Telegram Bot Token
    - chat_id: Telegram chat ID or channel ID
    - message: Message to be sent
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print(f"Message sent: {message}")
    else:
        print(f"Failed to send message. Status Code: {response.status_code}")

if __name__ == "__main__":
    # Get parameters from the command line
    bot_token = sys.argv[1]  # Telegram Bot Token
    chat_id = sys.argv[2]    # Telegram Chat ID or Channel ID
    message = sys.argv[3]    # Message to send
    
    send_telegram_message(bot_token, chat_id, message)
