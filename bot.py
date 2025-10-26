import os
import telebot
from dotenv import load_dotenv
import openai

# Загружаем переменные окружения
load_dotenv()

# Очищаем системные прокси Render (чтобы не ломали соединение)
for var in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy"]:
    os.environ.pop(var, None)

# Токены
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

if not TELEGRAM_TOKEN or not OPENAI_KEY:
    print("❌ Ошибка: не найден TELEGRAM_TOKEN или OPENAI_KEY")
    exit()

# Настраиваем OpenAI
openai.api_key = OPENAI_KEY
openai.proxy = None  # Явно отключаем любые прокси

# Инициализируем Telegram-бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Храним последние запросы пользователей
user_prompts = {}

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я умею улучшать фотографии через ИИ.\n"
        "Отправь мне текст (например: 'удали фон' или 'улучши освещение'), "
        "а затем фото 📸"
    )

# Обрабатываем текст
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_prompts[message.chat.id] = message.text.strip()
    bot.send_message(message.chat.id, "Теперь отправь фото для обработки ✨")

# Обрабатываем фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        prompt = user_prompts.get(message.chat.id, "улучши качество фото")
        bot.send_message(message.chat.id, f"✨ Обрабатываю фото...\n🪄 Запрос: {prompt}")

        # Скачиваем фото
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        with open("photo.png", "wb") as f:
            f.write(downloaded)

        # Отправляем запрос в OpenAI
        with open("photo.png", "rb") as image:
            response = openai.images.edits(
                model="gpt-image-1",
                image=image,
                prompt=prompt,
                size="1024x1024"
            )

        # Получаем URL результата
        image_url = response.data[0].url
        bot.send_message(message.chat.id, f"✅ Готово! Вот твое фото:\n{image_url}")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при обработке: {e}")
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    print("🤖 Бот успешно запущен без прокси и работает через OpenAI API 🚀")
    bot.polling(none_stop=True)
