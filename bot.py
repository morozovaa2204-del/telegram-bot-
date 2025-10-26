import os
import io
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🧩 Загрузка переменных окружения
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_KEY:
    raise ValueError("❌ Ошибка: не найден TELEGRAM_BOT_TOKEN или OPENAI_API_KEY в .env")

# 🧠 Инициализация OpenAI клиента
client = OpenAI(api_key=OPENAI_KEY)

# 📂 Файл для хранения пользователей
USERS_FILE = "users.json"

# Загружаем или создаём базу пользователей
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = {}

def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# 🚀 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.first_name

    if user_id not in users:
        users[user_id] = {"free_used": False}
        save_users()

    text = (
        f"👋 Привет, {user_name}!\n\n"
        "Я — твой ИИ-фотохудожник 🎨✨\n"
        "Я умею улучшать, раскрашивать и преображать твои фотографии с помощью искусственного интеллекта.\n\n"
        "📸 Отправь мне своё первое фото — и я обработаю его *бесплатно!*"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# 💬 Обработка текстов
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.chat.send_action(action="typing")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты умный и вежливый ассистент."},
                {"role": "user", "content": user_message},
            ],
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")

# 🖼️ Обработка фотографий
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user = users.get(user_id, {"free_used": False})

    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_path = file.file_path

        await update.message.reply_text("✨ Обрабатываю твоё фото, подожди немного...")

        # ИИ-обработка через OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты ИИ-фоторедактор. Оцени и опиши фото как будто оно после улучшения."},
                {"role": "user", "content": [{"type": "image_url", "image_url": file_path}]},
            ],
        )
        result_text = response.choices[0].message.content

        # Если фото бесплатное
        if not user["free_used"]:
            user["free_used"] = True
            users[user_id] = user
            save_users()

            await update.message.reply_text(
                "💎 Твоя первая обработка *абсолютно бесплатна!* 🩵\n\n"
                f"Вот результат:\n\n{result_text}",
                parse_mode="Markdown"
            )

        else:
            # Красивое сообщение с предложением оплаты
            pay_text = (
                "🌌 *Магия вдохновения ждёт тебя снова...*\n\n"
                "Твоё фото уже побывало в руках ИИ-творца, и теперь ты знаешь, как он видит красоту 💫\n\n"
                "Хочешь, чтобы каждое новое изображение сияло совершенством?\n\n"
                "👉 Получи *безлимитные улучшения* всего за 299₸.\n\n"
                "Нажми ❤️ *«Разблокировать магию»* и отправь следующую фотографию!"
            )

            await update.message.reply_text(pay_text, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при обработке фото: {e}")

# 🧩 Основной запуск
def main():
    print("✅ Бот с бесплатным фото и платным фотошопом запущен!")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()
