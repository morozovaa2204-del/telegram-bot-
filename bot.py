import os
import telebot
from dotenv import load_dotenv
from openai import OpenAI

# Загружаем .env
load_dotenv()

# Загружаем токены
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Проверяем ключи
if not TELEGRAM_TOKEN or not OPENAI_KEY:
    print("❌ Ошибка: не найден TELEGRAM_TOKEN или OPENAI_KEY")
    exit()

# Инициализация клиентов
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_KEY)  # Без аргумента proxy!

# Сохраняем текст запроса пользователя
user_prompts = {}

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я — ИИ-бот для редактирования фото.\n"
        "Отправь мне текст и фото, и я улучшу изображение с помощью нейросети 💫\n\n"
        "Напиши, например:\n"
        "— Сделай кожу гладкой\n"
        "— Замени фон на море\n"
        "— Улучши освещение"
    )

# Текст от пользователя
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_prompts[message.chat.id] = message.text.strip()
    bot.send_message(message.chat.id, "📸 Теперь отправь фото для обработки.")

# Фото от пользователя
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        prompt = user_prompts.get(
            message.chat.id,
            "улучши качество фото, сделай свет мягче и убери тени"
        )

        bot.send_message(message.chat.id, f"✨ Обрабатываю фото...\n🪄 Запрос: {prompt}")

        # Скачиваем фото
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open("photo.png", "wb") as new_file:
            new_file.write(downloaded_file)

        # Отправляем в OpenAI
        with open("photo.png", "rb") as image_file:
            result = client.images.edits(
                model="gpt-image-1",
                image=image_file,
                prompt=prompt,
                size="1024x1024"
            )

        image_url = result.data[0].url
        bot.send_message(message.chat.id, f"✅ Готово! Вот улучшенное фото:\n{image_url}")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")
        print(f"Ошибка при обработке: {e}")

# Запуск
if __name__ == "__main__":
    print("🤖 Бот запущен без прокси, Render готов 🚀")
    bot.polling(none_stop=True, interval=0)
