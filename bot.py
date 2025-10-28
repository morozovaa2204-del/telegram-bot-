import telebot
import os
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Ошибка: не найден TELEGRAM_TOKEN или OPENAI_API_KEY в .env")

# Инициализация клиентов
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Храним состояние пользователя (чтобы знать, кто уже использовал бесплатное фото)
user_free_photo = set()

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет, я твой ИИ-фотограф 🤖📸\n"
        "Отправь фото, и я его обработаю — бесплатно один раз 💫"
    )

# Получение фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.chat.id

    if user_id in user_free_photo:
        bot.send_message(
            user_id,
            "✨ Ты уже использовал бесплатную обработку.\n"
            "Хочешь ещё одно фото? 💎 Свяжись с поддержкой или оформи подписку!"
        )
        return

    bot.send_message(user_id, "🪄 Обрабатываю фото, подожди немного...")

    try:
        # Получаем файл
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраняем временно фото
        input_path = f"{user_id}_input.jpg"
        with open(input_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Отправляем в OpenAI для обработки (например, генерация нового изображения)
        with open(input_path, "rb") as img_file:
            result = client.images.generate(
                model="gpt-image-1",
                prompt="Сделай фото стильным, как профессиональная фотосессия, добавь мягкий свет",
                image=img_file
            )

        # Сохраняем результат
        image_url = result.data[0].url
        bot.send_photo(user_id, image_url, caption="Вот твоя обновлённая фотография! 💫")

        user_free_photo.add(user_id)

    except Exception as e:
        bot.send_message(user_id, f"⚠️ Ошибка: {e}")

# Обработка текстовых сообщений
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    bot.send_message(
        message.chat.id,
        "Отправь мне фото — я превращу его в шедевр 🎨✨"
    )

# Запуск бота
print("Бот запущен 🚀")
bot.polling(none_stop=True)
