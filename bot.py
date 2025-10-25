import telebot
import requests
import os
import time
from dotenv import load_dotenv

# Загружаем токены
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 🧠 Функция обработки изображения через OpenAI
def ai_edit_image(image_path):
    url = "https://api.openai.com/v1/images/edits"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}"
    }
    files = {
        "image": open(image_path, "rb"),
        "mask": open(image_path, "rb")
    }
    data = {
        "model": "gpt-image-1",
        "prompt": "улучшить качество, осветлить, сделать лицо красивее и фон мягче"
    }

    response = requests.post(url, headers=headers, files=files, data=data)
    response.raise_for_status()
    result = response.json()
    return result["data"][0]["url"]

# 🟢 Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Привет! Отправь мне фото — я улучшу его с помощью ИИ ✨")

# 📸 Приём фото
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

        bot.reply_to(message, "🧠 Обрабатываю фото, подожди немного ☁️")
        result_url = ai_edit_image(img_path)
        bot.send_photo(message.chat.id, result_url, caption="✨ Вот улучшенная версия твоего фото!")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при обработке: {e}")

# 🚀 Безопасный запуск
if __name__ == "__main__":
    print("✅ Бот запущен (с защитой от двойного запуска)")

    while True:
        try:
            bot.polling(non_stop=True, interval=1, timeout=30)
        except Exception as e:
            # Если ошибка 409 — просто ждём и пробуем снова
            if "Conflict: terminated by other getUpdates request" in str(e):
                print("⚠️ Обнаружен второй экземпляр бота. Ожидание 15 сек...")
                time.sleep(15)
                continue
            else:
                print(f"🚨 Ошибка: {e}")
                time.sleep(10)
