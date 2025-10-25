import telebot
import requests
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# 🔑 Твои ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 🧠 Функция для запросов к OpenAI
def ask_chatgpt(message_text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Ты дружелюбный помощник, который помогает людям."},
            {"role": "user", "content": message_text}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Ошибка при обращении к OpenAI: {e}"

# 🟢 Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Привет! Я твой AI-бот. Отправь мне фото или сообщение — и я помогу!")

# 💬 Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        reply = ask_chatgpt(message.text)
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {e}")

# 🧷 Защита от двойного запуска
if __name__ == "__main__":
    print("✅ Бот запущен и работает 24/7...")
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"⚠️ Бот остановлен из-за ошибки: {e}")
