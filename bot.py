import os
import io
import requests
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔹 Загружаем токены из .env
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_KEY:
    raise ValueError("❌ Ошибка: не найден TELEGRAM_BOT_TOKEN или OPENAI_API_KEY в .env")

# 🔹 Инициализация OpenAI клиента
client = OpenAI(api_key=OPENAI_KEY)

# 🔹 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я ИИ-бот.\n"
        "Отправь мне фото — я его улучшу с помощью искусственного интеллекта 💫"
    )

# 🔹 Обработка текстовых сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.chat.send_action(action="typing")

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты умный и дружелюбный ассистент."},
                {"role": "user", "content": user_message},
            ],
        )
        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при обработке текста: {e}")

# 🔹 Обработка фотографий
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("🧠 Обрабатываю фото, подожди немного...")

        # Получаем файл из Telegram
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_path = file.file_path

        # Загружаем изображение в память
        img_data = requests.get(file_path).content

        # Отправляем запрос в OpenAI (визуальный анализ)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Ты — профессиональный ИИ-фоторедактор. Улучши изображение: убери шум, улучшай цвет, сделай более чётким и красивым.",
                },
                {"role": "user", "content": [{"type": "image_url", "image_url": file_path}]},
            ],
        )

        description = response.choices[0].message.content

        # Отправляем пользователю результат (описание и оригинал)
        await update.message.reply_text(f"✨ Фото улучшено! Вот результат:\n{description}")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при обработке фото: {e}")

# 🔹 Основная функция
def main():
    print("✅ Бот с ИИ-фотошопом запущен!")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()
