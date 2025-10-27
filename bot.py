import telebot
import os
from dotenv import load_dotenv
from openai import OpenAI

# Загружаем .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not OPENAI_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ Ошибка: не найден TELEGRAM_BOT_TOKEN или OPENAI_API_KEY в .env")

# ✅ Создаём OpenAI-клиент (без прокси!)
client = OpenAI(api_key=OPENAI_API_KEY)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "👋 Привет! Отправь фото для обработки ✨")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "🪄 Обрабатываю фото, подожди пару секунд...")

        # Скачиваем фото
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open("input.jpg", "wb") as f:
            f.write(downloaded_file)

        # Отправляем в OpenAI
        response = client.images.edit(
            model="gpt-image-1",
            image=open("input.jpg", "rb"),
            prompt="Enhance the image, improve lighting and clarity."
        )

        edited_url = response.data[0].url
        bot.send_photo(message.chat.id, edited_url, caption="✅ Готово! Фото улучшено 💫")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при обработке: {e}")

print("✅ Бот запущен и готов к работе!")
bot.infinity_polling()
