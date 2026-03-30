import requests
import time
import re
import json
import os

BOT_TOKEN = os.getenv("7671937313:AAGfz6zP6EXrp0yYb7T4ODQwY-dXcX3Ph1g")
API_KEY = os.getenv("hKgZaEjblCvfpGmcp7PaV9px7EabQzkn")

ADMIN_ID = 7515864015
CHANNEL_USERNAME = "@SUMITDARKOSINT"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

users = set()
last_update_id = None

def footer(text):
    return text + "\n\n━━━━━━━━━━━━━━\n👨‍💻 Developer: @T4HKR"

def get_keyboard():
    keyboard = {
        "keyboard": [
            [{"text": "📱 Number Search"}],
            [{"text": "📊 Bot Stats"}, {"text": "👨‍💻 Developer"}],
            [{"text": "ℹ️ Help"}]
        ],
        "resize_keyboard": True
    }
    return json.dumps(keyboard)

def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    data = {
        "chat_id": chat_id,
        "text": footer(text),
        "reply_markup": get_keyboard()
    }
    requests.post(url, data=data)

# ✅ Number auto fix (no country code needed)
def format_number(num):
    num = num.strip().replace(" ", "")
    
    if num.startswith("+"):
        return num
    
    # India default
    if len(num) == 10:
        return "+91" + num
    
    return None

def get_number_info(number):
    url = f"http://apilayer.net/api/validate?access_key={API_KEY}&number={number}"

    try:
        res = requests.get(url)
        data = res.json()

        if not data.get("valid"):
            return "❌ Invalid number or no data found."

        return f"""📱 Number Information:

🌍 Country: {data.get("country_name")}
📍 Location: {data.get("location")}
📡 Carrier: {data.get("carrier")}
📶 Line Type: {data.get("line_type")}

🔢 Number: {data.get("international_format")}
"""
    except:
        return "⚠️ API error."

def get_updates():
    global last_update_id
    url = BASE_URL + "getUpdates"
    params = {"timeout": 100}

    if last_update_id:
        params["offset"] = last_update_id + 1

    return requests.get(url, params=params).json()

def handle(updates):
    global last_update_id

    for update in updates.get("result", []):
        last_update_id = update["update_id"]

        if "message" not in update:
            continue

        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        if text == "/start":
            send_message(chat_id, "🤖 Welcome! Use buttons below.")

        elif text == "📱 Number Search":
            send_message(chat_id, "📲 Send any number (no need country code)")

        elif text == "📊 Bot Stats":
            send_message(chat_id, f"👥 Users: {len(users)}")

        elif text == "👨‍💻 Developer":
            send_message(chat_id, "👨‍💻 Developer: @T4HKR")

        elif text == "ℹ️ Help":
            send_message(chat_id, "ℹ️ Send any mobile number (10 digits)")

        else:
            users.add(chat_id)

            number = format_number(text)

            if not number:
                send_message(chat_id, "⚠️ Send valid number (10 digits)")
                return

            result = get_number_info(number)
            send_message(chat_id, result)

def main():
    while True:
        updates = get_updates()
        if updates.get("ok"):
            handle(updates)
        time.sleep(2)

if __name__ == "__main__":
    main()
