import telebot
import requests
from openai import OpenAI
import os
from dotenv import load_dotenv
from telebot import types

# Загружаем .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not OPENAI_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise ValueError("Ошибка: не найден OPENAI_API_KEY или TELEGRAM_BOT_TOKEN!")

# Подключаем OpenAI и Telegram
client = OpenAI(api_key=OPENAI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Счётчик бесплатных фото
user_free_photos = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! 🌸 Отправь мне фото — я обработаю его для тебя с помощью ИИ ✨")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Проверяем, использовал ли пользователь бесплатную обработку
    if user_free_photos.get(user_id, 0) >= 1:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💎 Разблокировать магию", url="https://kaspi.kz"))
        bot.send_message(
            chat_id,
            "✨ Ты уже использовал бесплатную обработку!\n"
            "Разблокируй безлимитную магию фото 💫 — всего 500₸.",
            reply_markup=markup
        )
        return

    bot.reply_to(message, "✨ Обрабатываю твоё фото... подожди немного 💫")

    # Получаем файл
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"
    response = requests.get(file_url)

    # Отправляем в OpenAI для улучшения
    result = client.images.edit(
        model="gpt-image-1",
        image=response.content,
        prompt="Улучшить качество, сделать мягкий свет и лёгкий гламурный стиль, сохранить естественность"
    )

    # Получаем ссылку
    image_url = result.data[0].url

    # Отправляем пользователю
    bot.send_photo(chat_id, image_url, caption="💖 Готово! Вот твоё улучшенное фото 🌸")

    # Отмечаем, что пользователь использовал бесплатное фото
    user_free_photos[user_id] = user_free_photos.get(user_id, 0) + 1

# Запуск
print("✅ Бот запущен и готов к магии!")
bot.polling(none_stop=True)
