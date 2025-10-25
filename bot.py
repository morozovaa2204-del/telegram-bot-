import os
import telebot
from dotenv import load_dotenv
from openai import OpenAI

# Загружаем .env файл
load_dotenv()

# Загружаем ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Проверяем ключи
if not TELEGRAM_TOKEN or not OPENAI_KEY:
    print("❌ Ошибка: не найден TELEGRAM_TOKEN или OPENAI_KEY")
    exit()

# Инициализация
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_KEY)

# Храним последнее сообщение пользователя (описание задачи для фото)
user_prompts = {}

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я — ИИ-бот, который умеет редактировать и улучшать фотографии.\n\n"
        "Отправь мне фото и напиши, что нужно сделать — например:\n"
        "• Сделай кожу гладкой\n"
        "• Замени фон на пляж\n"
        "• Осветли лицо и добавь мягкий свет 💡"
    )

# Текст от пользователя
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_prompts[message.chat.id] = message.text.strip()
    bot.send_message(
        message.chat.id,
        "📸 Отлично! Теперь пришли фото, которое нужно обработать."
    )

# Фото от пользователя
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Получаем описание (если пользователь его отправил)
        prompt = user_prompts.get(
            message.chat.id,
            "улучши качество, осветли лицо, убери тени, сделай мягкое освещение"
        )

        bot.send_message(message.chat.id, f"✨ Обрабатываю фото через ИИ...\n🪄 Запрос: {prompt}")

        # Скачиваем фото
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open("photo.png", 'wb') as new_file:
            new_file.write(downloaded_file)

        # Обработка изображения через OpenAI
        with open("photo.png", "rb") as image_file:
            result = client.images.edits(
                model="gpt-image-1",
                image=image_file,
                prompt=prompt,
                size="1024x1024"
            )

        # Отправляем результат пользователю
        image_url = result.data[0].url
        bot.send_message(
            message.chat.id,
            f"✅ Готово! Вот обработанное фото:\n{image_url}"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при обработке фото: {e}")

# Запуск
if __name__ == "__main__":
    print("🤖 Бот запущен и работает с ИИ-обработкой изображений...")
    bot.polling(none_stop=True, interval=0)
