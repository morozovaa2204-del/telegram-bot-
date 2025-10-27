import os
import telebot
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем .env (для локального запуска)
load_dotenv()

# Берём ключи из окружения (на Render они задаются в Environment)
OPENAI_API_KEY = os.getenv("OPENAI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Проверяем, заданы ли ключи
if not OPENAI_API_KEY or not TELEGRAM_TOKEN:
    raise ValueError("❌ Ошибка: не найден TELEGRAM_TOKEN или OPENAI_KEY")

# Создаём клиента OpenAI (без proxy!)
client = OpenAI(api_key=OPENAI_API_KEY)

# Инициализация Telegram-бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Словарь: отслеживает, кто уже использовал бесплатную обработку
user_free_used = {}

# Команда /start
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        "👋 Привет! Отправь фото для обработки ✨\n\n"
        "📸 Первая обработка — бесплатная 💫\n"
        "После — будет предложена оплата ❤️"
    )

# Обработка фото
@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    user_id = message.from_user.id

    # Проверяем, использовал ли пользователь бесплатную обработку
    if user_free_used.get(user_id, False):
        bot.reply_to(
            message,
            "💳 Бесплатная обработка уже использована.\n"
            "Хочешь оформить подписку или оплатить обработку? 😊"
        )
        return

    bot.reply_to(message, "✨ Обрабатываю фото... Подожди немного ⏳")

    try:
        # Получаем файл
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open("input.jpg", "wb") as f:
            f.write(downloaded_file)

        # Здесь можно сделать обработку изображения
        # Например — отправить в OpenAI, сделать фильтр, улучшение и т.д.
        # Сейчас просто пример текстового отклика:
        bot.send_message(message.chat.id, "✅ Фото успешно обработано! ❤️")

        # Отмечаем, что пользователь использовал бесплатную обработку
        user_free_used[user_id] = True

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при обработке фото: {e}")

print("✅ Бот успешно запущен и готов к работе!")
bot.polling(none_stop=True)
