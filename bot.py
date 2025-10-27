import os
import telebot
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем .env (локально)
load_dotenv()

# Получаем ключи из переменных окружения
OPENAI_API_KEY = os.getenv("OPENAI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Проверка ключей
if not OPENAI_API_KEY or not TELEGRAM_TOKEN:
    raise ValueError("❌ Ошибка: отсутствует TELEGRAM_TOKEN или OPENAI_KEY")

# Инициализация клиента OpenAI (БЕЗ proxy)
client = OpenAI(api_key=OPENAI_API_KEY)

# Инициализация Telegram-бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Память пользователей
user_free_used = {}

# Команда /start
@bot.message_handler(commands=["start", "help"])
def start_message(message):
    bot.reply_to(
        message,
        "👋 Привет! Отправь фото для обработки ✨\n\n"
        "📸 Первая обработка — бесплатная 💫\n"
        "После этого бот предложит оплату ❤️"
    )

# Приём фото
@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    user_id = message.from_user.id

    if user_free_used.get(user_id, False):
        bot.send_message(
            message.chat.id,
            "💳 Бесплатная обработка уже использована.\n"
            "Чтобы продолжить, оформите подписку ❤️"
        )
        return

    bot.send_message(message.chat.id, "✨ Обрабатываю фото... Подожди немного ⏳")

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open("input.jpg", "wb") as f:
            f.write(downloaded_file)

        bot.send_message(message.chat.id, "✅ Фото успешно обработано! ❤️")
        user_free_used[user_id] = True

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при обработке фото: {e}")

print("✅ Бот успешно запущен и готов к работе!")
bot.polling(none_stop=True)
