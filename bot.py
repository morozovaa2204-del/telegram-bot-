import telebot
import requests
import os
from dotenv import load_dotenv

# Загружаем токены из .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 🧠 Функция для ИИ обработки изображения
def ai_edit_image(image_path):
    url = "https://api.openai.com/v1/images/edits"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}"
    }
    files = {
        "image": open(image_path, "rb"),
        "mask": open(image_path, "rb")  # можно использовать ту же картинку
    }
    data = {
        "model": "gpt-image-1",
        "prompt": "улучшить качество изображения, осветлить, сделать лицо красивее и фон мягче"
    }

    response = requests.post(url, headers=headers, files=files, data=data)
    response.raise_for_status()
    result = response.json()
    image_url = result["data"][0]["url"]
    return image_url

# 🟢 Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Привет! Отправь мне фотографию, и я улучшю её с помощью ИИ ✨")

# 📸 Приём фотографий
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
        img_data = requests.get(file_url).content

        img_path = "input.jpg"
        with open(img_path, "wb") as f:
            f.write(img_data)

        bot.reply_to(message, "🧠 Обрабатываю фото... подожди немного ☁️")

        result_url = ai_edit_image(img_path)
        bot.send_photo(message.chat.id, result_url, caption="✨ Вот улучшенная версия твоего фото!")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при обработке: {e}")

# 🚀 Запуск
if __name__ == "__main__":
    print("✅ Бот запущен и готов улучшать фотографии!")
    bot.polling(non_stop=True)
