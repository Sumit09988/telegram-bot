import requests
import time
import re
import json

BOT_TOKEN = "7671937313:AAGfz6zP6EXrp0yYb7T4ODQwY-dXcX3Ph1g"
API_KEY = "hKgZaEjblCvfpGmcp7PaV9px7EabQzkn"

ADMIN_ID = 7515864015
CHANNEL_USERNAME = "@SUMITDARKOSINT"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

users = set()
banned_users = set()
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

def check_join(user_id):
    url = BASE_URL + "getChatMember"
    params = {"chat_id": CHANNEL_USERNAME, "user_id": user_id}
    res = requests.get(url, params=params).json()
    status = res.get("result", {}).get("status")
    return status in ["member", "administrator", "creator"]

def is_valid_number(text):
    return re.match(r'^\+\d{10,15}$', text)

def get_number_info(number):
    headers = {"apikey": API_KEY}
    params = {"number": number}
    url = "https://api.apilayer.com/number_verification/validate"

    try:
        res = requests.get(url, headers=headers, params=params)
        data = res.json()

        if not data.get("valid"):
            return "❌ Invalid number."

        return f"""📱 Number Information:

🌍 Country: {data.get("countryname")}
📍 Location: {data.get("location")}
📡 Carrier: {data.get("carrier")}
📶 Line Type: {data.get("linetype")}

🔢 Number: {data.get("internationalformat")}
"""
    except:
        return "⚠️ Server error."

def broadcast(msg):
    for user in users:
        try:
            send_message(user, msg)
        except:
            pass

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
        user_id = msg["from"]["id"]
        text = msg.get("text", "")

        users.add(user_id)

        if user_id in banned_users:
            return

        if not check_join(user_id):
            send_message(chat_id, f"🚫 Join channel first:\n👉 {CHANNEL_USERNAME}")
            return

        if text == "/start":
            send_message(chat_id, "🤖 Welcome! Use buttons below.")

        elif text == "📱 Number Search":
            send_message(chat_id, "📲 Send number with country code\nExample: +919876543210")

        elif text == "📊 Bot Stats":
            send_message(chat_id, f"👥 Total Users: {len(users)}")

        elif text == "👨‍💻 Developer":
            send_message(chat_id, "👨‍💻 Developer: @T4HKR")

        elif text == "ℹ️ Help":
            send_message(chat_id, "ℹ️ Send number with country code\nExample: +919876543210")

        elif user_id == ADMIN_ID:

            if text.startswith("/ban"):
                uid = int(text.split()[1])
                banned_users.add(uid)
                send_message(chat_id, f"✅ Banned {uid}")

            elif text.startswith("/unban"):
                uid = int(text.split()[1])
                banned_users.discard(uid)
                send_message(chat_id, f"✅ Unbanned {uid}")

            elif text.startswith("/broadcast"):
                msg_text = text.replace("/broadcast ", "")
                broadcast(msg_text)
                send_message(chat_id, "✅ Broadcast sent")

        else:
            if not is_valid_number(text):
                send_message(chat_id, "⚠️ Invalid format.\nExample: +919876543210")
                return

            result = get_number_info(text)
            send_message(chat_id, result)

def main():
    while True:
        updates = get_updates()
        if updates.get("ok"):
            handle(updates)
        time.sleep(2)

if __name__ == "__main__":
    main()
