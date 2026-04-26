import os
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

print(f"BOT_TOKEN exists: {bool(BOT_TOKEN)}")
print(f"OPENROUTER_API_KEY exists: {bool(OPENROUTER_API_KEY)}")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-3.1-8b-instruct:free"

SYSTEM_PROMPT = "You are a helpful and friendly assistant. Reply in the same language the user uses."

conversation_history = []

def get_updates(offset=None):
    params = {"timeout": 30, "offset": offset}
    response = requests.get(f"{API_URL}/getUpdates", params=params)
    return response.json()

def send_message(chat_id, text):
    data = {"chat_id": chat_id, "text": text}
    requests.post(f"{API_URL}/sendMessage", data=data)

def ask_ai(user_message):
    conversation_history.append({"role": "user", "content": user_message})
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history
    }
    response = requests.post(OPENROUTER_URL, headers=headers, json=body)
    data = response.json()
    print(f"OpenRouter response: {data}")
    reply = data["choices"][0]["message"]["content"]
    conversation_history.append({"role": "assistant", "content": reply})
    return reply

def main():
    print("Bot started...")
    offset = None
    while True:
        updates = get_updates(offset)
        print(f"Updates: {updates}")
        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    user_text = update["message"]["text"]
                    print(f"User: {user_text}")
                    if user_text == "/start":
                        send_message(chat_id, "Halo! Aku asisten virtualmu. Ada yang bisa aku bantu?")
                    else:
                        reply = ask_ai(user_text)
                        send_message(chat_id, reply)

if __name__ == "__main__":
    main()
