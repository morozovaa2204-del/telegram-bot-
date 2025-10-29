import telebot
import os
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

# Получаем токены
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Ошибка: отсутствует TELEGRAM_TOKEN или OPENAI_API_KEY в .env")

# Инициализация клиентов
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Новый способ инициализации клиента OpenAI (без proxies)
client = OpenAI(api_key=OPENAI_API_KEY)

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Привет! Я твой AI-помощник. Задай мне любой вопрос!")

# Основная логика ответов
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_text = message.text.strip()

        # Запрос к OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты дружелюбный помощник Telegram-бота."},
                {"role": "user", "content": user_text},
            ]
        )

        ai_answer = response.choices[0].message.content
        bot.reply_to(message, ai_answer)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {str(e)}")

# Запуск
if __name__ == "__main__":
    print("✅ Бот успешно запущен на Render!")
    bot.polling(none_stop=True)
