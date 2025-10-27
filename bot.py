import telebot
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

# Загружаем переменные окружения (.env)
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not OPENAI_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ Ошибка: не найден TELEGRAM_BOT_TOKEN или OPENAI_API_KEY в .env")

# ✅ Правильное создание клиента OpenAI (без proxy!)
client = OpenAI(api_key=OPENAI_API_KEY)

# Создаём Telegram-бота
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# 💬 Приветственное сообщение
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✨ Привет! Отправь фото для обработки 💫")

# 🖼 Обработка фото от пользователя
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "🔮 Обработка фото... Подожди немного 💫")

        # Получаем файл фотографии
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраняем временный файл
        with open("image.jpg", "wb") as new_file:
            new_file.write(downloaded_file)

        # Отправляем фото в OpenAI для улучшения (пример)
        response = client.images.edit(
            model="gpt-image-1",
            image=open("image.jpg", "rb"),
            prompt="Enhance this portrait photo — make it clearer, brighter, and more detailed."
        )

        # Получаем URL улучшенного изображения
        image_url = response.data[0].url

        # Отправляем пользователю результат
        bot.send_photo(message.chat.id, image_url, caption="✨ Фото улучшено!")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при обработке фото: {e}")

# 🚀 Запуск бота
print("✅ Бот запущен и готов к работе!")
bot.infinity_polling()
