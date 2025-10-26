import os
import telebot
from dotenv import load_dotenv
from openai import OpenAI

# Загружаем .env
load_dotenv()

# Удаляем системные прокси, чтобы Render не ломал клиента
for var in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"]:
    if var in os.environ:
        del os.environ[var]

# Ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Проверка
if not TELEGRAM_TOKEN or not OPENAI_KEY:
    print("❌ Ошибка: не найден TELEGRAM_TOKEN или OPENAI_KEY")
    exit()

# Клиенты
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_KEY)

# Храним последний текст запроса
user_prompts = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я умею улучшать фотографии с помощью ИИ.\n"
        "Отправь текст и фото — и я всё сделаю!\n\n"
        "Например:\n"
        "— Убери фон\n"
        "— Сделай кожу мягче\n"
        "— Осветли фото"
    )

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_prompts[message.chat.id] = message.text.strip()
    bot.send_message(message.chat.id, "📸 Теперь отправь фото для обработки!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        prompt = user_prompts.get(message.chat.id, "улучши качество изображения")
        bot.send_message(message.chat.id, f"✨ Обрабатываю фото...\n🪄 Запрос: {prompt}")

        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)

        with open("photo.png", "wb") as f:
            f.write(downloaded)

        with open("photo.png", "rb") as image_file:
            result = client.images.edits(
                model="gpt-image-1",
                image=image_file,
                prompt=prompt,
                size="1024x1024"
            )

        image_url = result.data[0].url
        bot.send_message(message.chat.id, f"✅ Готово! Вот результат:\n{image_url}")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при обработке: {e}")
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    print("🤖 Бот запущен без прокси, Render готов 🚀")
    bot.polling(none_stop=True, interval=0)
