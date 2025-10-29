import telebot
import os
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверяем, что ключи найдены
if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Ошибка: не найден TELEGRAM_TOKEN или OPENAI_API_KEY в .env")

# Инициализация клиентов
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Команда /start
@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, "👋 Привет! Я GPT-бот. Напиши мне сообщение, и я отвечу!")

# Обработка всех сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_message = message.text

        # Отправляем запрос в OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # или gpt-4-turbo, если есть доступ
            messages=[
                {"role": "system", "content": "Ты дружелюбный Telegram-бот-помощник."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )

        bot.reply_to(message, response.choices[0].message.content)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {e}")

# Запуск бота
if __name__ == "__main__":
    print("✅ Бот запущен и готов к работе!")
    bot.polling(none_stop=True)
