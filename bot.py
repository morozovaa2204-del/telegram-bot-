import os
import requests
import telebot
from dotenv import load_dotenv

# Загружаем ключи из .env
load_dotenv()

# 🔑 Твои ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Проверка, что ключи есть
if not TELEGRAM_TOKEN:
    raise SystemExit("❌ Ошибка: TELEGRAM_TOKEN не найден. Добавь его в .env")
if not OPENAI_KEY:
    raise SystemExit("❌ Ошибка: OPENAI_KEY не найден. Добавь его в .env")

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 💬 Функция общения с ChatGPT (через API)
def ask_chatgpt(message_text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",  # ✅ стабильная модель, работает у всех
        "messages": [
            {"role": "system", "content": "Ты дружелюбный и умный помощник."},
            {"role": "user", "content": message_text}
        ],
        "max_tokens": 1000,
        "temperature": 0.8
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 401:
        raise Exception("Ошибка 401 — неверный OpenAI API ключ. Проверь .env файл.")
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()

# 🟢 Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет 👋 Я твой AI-помощник! Напиши мне сообщение, и я отвечу как ChatGPT 😊")

# 💬 Обработка всех сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        answer = ask_chatgpt(message.text)
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {e}")

# 🚀 Запуск
if __name__ == "__main__":
    print("✅ Бот запущен и работает 24/7...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
