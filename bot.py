import telebot
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 🧠 Генерация нового фото на основе старого
def process_photo(image_path, prompt_text):
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
    }

    with open(image_path, "rb") as image_file:
        files = {
            "image": image_file,
        }
        data = {
            "model": "gpt-image-1",
            "prompt": prompt_text,
        }

        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        result = response.json()
        return result["data"][0]["url"]

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет 👋 Отправь мне фото и напиши, что нужно сделать (например: 'сделай фото как будто я на фоне моря').")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}'
        file_data = requests.get(file_url)
        file_path = f"photo_{message.chat.id}.jpg"

        with open(file_path, "wb") as f:
            f.write(file_data.content)

        bot.reply_to(message, "✨ Обрабатываю фото через ИИ, подожди немного...")

        # 🧠 Изменяем изображение по запросу пользователя
        edited_image_url = process_photo(file_path, "Сделай это фото более красивым, улучшенным и с эффектом фотостудии.")
        bot.send_photo(message.chat.id, edited_image_url)
        os.remove(file_path)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при обработке фото: {e}")

if __name__ == "__main__":
    print("✅ Бот запущен и готов к ИИ обработке!")
    bot.polling(non_stop=True)
