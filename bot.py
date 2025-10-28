from openai import OpenAI
import telebot
import os
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверяем, что ключи найдены
if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Не найден TELEGRAM_TOKEN или OPENAI_API_KEY")

# Подключаем OpenAI без аргумента proxy
client = OpenAI(api_key=OPENAI_API_KEY)

# Создаём Telegram-бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь фото для обработки ✨")

@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    bot.reply_to(message, "Фото получено! 🪄 Обработка началась...")
    # Здесь можно добавить логику генерации / редактирования через OpenAI Images API

print("✅ Бот запущен и готов к работе!")
bot.infinity_polling()
