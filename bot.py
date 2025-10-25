import telebot
import requests
import os
import time
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# 🔑 Ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 🧠 Текстовый ответ ChatGPT
def ask_chatgpt(message_text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Ты дружелюбный помощник, который помогает людям с текстом и фото."},
            {"role": "user", "content": message_text}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=40)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Ошибка при обращении к OpenAI: {e}"

# 🧩 Обработка фото (ИИ-фотошоп)
def process_image_with_ai(image_bytes):
    url = "https://api.openai.com/v1/images/edits"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    files = {"image": ("photo.png", image_bytes)}
    data = {
        "model": "gpt-4o-mini",
        "prompt": "улучши фото, сделай лицо чётким, кожу естественной, фон нейтральным и красивым"
    }

    try:
        response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result["data"][0]["url"]
    except Exception as e:
        return f"⚠️ Ошибка при обработке фото: {e}"

# 🟢 Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Привет! Я ИИ-бот. Отправь фото или текст — и я помогу 📸🤖")

# 💬 Обработка текста
@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    reply = ask_chatgpt(message.text)
    bot.reply_to(message, reply)

# 🖼 Обработка фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.reply_to(message, "✨ Обрабатываю фото через ИИ, подожди немного...")

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        result_url = process_image_with_ai(downloaded_file)

        if isinstance(result_url, str) and result_url.startswith("http"):
            bot.send_photo(message.chat.id, result_url, caption="Вот готовое фото ✨")
        else:
            bot.reply_to(message, result_url)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при загрузке фото: {e}")

# 🔁 Автоматический перезапуск при сбое
def run_bot():
    while True:
        try:
            print("✅ Бот запущен и работает 24/7...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            print("♻️ Перезапуск через 10 секунд...")
            time.sleep(10)

# 🚀 Запуск
if __name__ == "__main__":
    run_bot()
