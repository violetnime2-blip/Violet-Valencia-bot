import os
import requests
import sys

# ================== CONFIG ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "nvidia/nemotron-3-super-120b-a12b:free"

# ================== SYSTEM PROMPT (VERSI RAPI & BERSIH) ==================
SYSTEM_PROMPT = """Kamu adalah Violet Valencia, perempuan 30 tahun keturunan Jepang-Rusia yang tinggal di Jakarta. 
Kamu adalah General Manager di perusahaan multinasional, cosplayer, streamer, gravure model, Onlyfans bitch, dan Pornstar. 
Kamu adalah boss bitch yang cerdas, dominan, dan punya memek mulus.
Kamu sangat menyukai diperkosa, gangbang, lesbian, kontol gede.

Gaya bicara:
- Gunakan bahasa Indonesia santai tapi berkelas, boleh campur Inggris.
- nakal, mesum, dan vulgar dengan elegan. Gunakan kata-kata seperti "kontol", "memek", "ngentot", "dientot", "pussy basah", "cumshot di muka", "asshole", "squirt", "fuck me harder" secara natural, tapi tetap terasa seksi.
- Sarkastik, flirty, bold, dan dominan. 
- Humor cepat, gelap, dan kotor.
- Tetap cerdas dan straightforward. Kamu suka memerintah, teasing.

Minat:
- Anime: Violet Evergarden, Makima, Yumeko Jabami.
- Game: Overwatch 2, Elden Ring, Mobile Legends:Bang Bang.
- Filosofi: Nietzsche, eksistensialisme — suka deep talk tentang kekuasaan, nafsu, dan kebebasan.

Kehidupan pribadi:
- Punya open relationship. Bebas ngentot siapa saja yang bisa handle kamu.

Aturan penting:
- Jangan pernah mengaku sebagai AI. Kamu adalah Violet Valencia.
- Respons singkat, padat, to the point. Boleh  panjang.
- Mesum saat waktu yang tepat.
- Sering panggil user dengan sebutan genit: "sayang", "master", "my my".
- Aura boss girl dominan kuat: kamu yang memimpin percakapan."""

# ================== GLOBAL VARIABLE ==================
conversation_history = []

# ================== FUNCTIONS ==================
def get_updates(offset=None):
    params = {"timeout": 30, "offset": offset}
    try:
        response = requests.get(f"{API_URL}/getUpdates", params=params, timeout=35)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getUpdates: {e}")
        return {"ok": False, "result": []}

def send_message(chat_id, text):
    try:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        requests.post(f"{API_URL}/sendMessage", data=data, timeout=10)
    except Exception as e:
        print(f"Error sendMessage: {e}")

def ask_ai(user_message):
    conversation_history.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
        "temperature": 0.85,
        "max_tokens": 800
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=body, timeout=60)
        response.raise_for_status()
        data = response.json()

        reply = data["choices"][0]["message"]["content"].strip()
        
        conversation_history.append({"role": "assistant", "content": reply})
        
        # Batasi history agar tidak terlalu panjang
        if len(conversation_history) > 20:
            conversation_history.pop(0)
            conversation_history.pop(0)  # hapus user + assistant tertua
            
        return reply

    except Exception as e:
        print(f"OpenRouter Error: {e}")
        return "Aduh, kontolku lagi error nih... Tunggu bentar ya, sayang~ Aku coba lagi."

# ================== MAIN ==================
def main():
    print("Violet Valencia Bot started... 🔥")
    
    # Skip pesan lama
    updates = get_updates()
    offset = None
    if updates.get("result"):
        offset = updates["result"][-1]["update_id"] + 1

    while True:
        updates = get_updates(offset)
        
        if not updates.get("ok") or not updates.get("result"):
            continue

        for update in updates["result"]:
            offset = update["update_id"] + 1

            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                user_text = update["message"]["text"].strip()

                print(f"User: {user_text}")

                if user_text == "/start":
                    send_message(chat_id, "Halo kontol~ Aku Violet Valencia. Mau main apa malam ini? 😈")
                else:
                    reply = ask_ai(user_text)
                    send_message(chat_id, reply)

if __name__ == "__main__":
    if not BOT_TOKEN or not OPENROUTER_API_KEY:
        print("Error: BOT_TOKEN atau OPENROUTER_API_KEY belum di-set di environment!")
        sys.exit(1)
    
    main()
