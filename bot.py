import os
import telebot
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request

# === Настройка окружения ===
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ Ошибка: не найден TELEGRAM_TOKEN или OPENAI_API_KEY в .env")

# === Инициализация ===
client = OpenAI(api_key=OPENAI_API_KEY)  # без параметра proxies!
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# === Переменная для бесплатного фото ===
free_photo_given = set()


# === Обработчики команд ===
@bot.message_handler(commands=["start"])
def start_message(message):
    bot.reply_to(message, "👋 Привет! Отправь мне фото — и я сделаю его волшебным ✨")


@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    user_id = message.chat.id

    if user_id not in free_photo_given:
        bot.reply_to(message, "🎁 Твое первое фото бесплатно! 💫")
        free_photo_given.add(user_id)
        process_image(message)
    else:
        bot.reply_to(message, "🔒 Бесплатное фото уже использовано. Напиши админу, чтобы получить больше ✨")


def process_image(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        filename = f"image_{message.chat.id}.jpg"
        with open(filename, "wb") as new_file:
            new_file.write(downloaded_file)

        bot.reply_to(message, "🪄 Обрабатываю фото... чуть-чуть терпения...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты — волшебный художник, создающий магические описания к фото."},
                {"role": "user", "content": "Создай вдохновляющий текст, подходящий к красивому фото."}
            ]
        )

        description = response.choices[0].message.content
        bot.reply_to(message, f"✨ {description}")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при обработке фото: {e}")


# === Webhook (для Render) ===
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "!", 200


@app.route("/")
def index():
    return "🤖 Бот работает!", 200


# === Запуск ===
if __name__ == "__main__":
    # если это Render — активируем webhook
    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/{TELEGRAM_TOKEN}"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        print(f"✅ Вебхук установлен: {webhook_url}")
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    else:
        # локальный режим (твой компьютер)
        print("✅ Бот запущен локально!")
        bot.infinity_polling()
