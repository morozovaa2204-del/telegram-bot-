import os
import telebot
from telebot import types
from openai import OpenAI
from dotenv import load_dotenv
import requests

# Загружаем переменные окружения (.env)
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Проверяем, есть ли ключи
if not OPENAI_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise ValueError("Ошибка: не найден TELEGRAM_BOT_TOKEN или OPENAI_API_KEY в .env")

# Инициализация клиентов
client = OpenAI(api_key=OPENAI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Память для учёта бесплатных обработок
user_free_used = {}

# Приветствие
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message,
        "✨ Привет! Я — твой ИИ-фоторедактор.\n"
        "Отправь мне фото, и я сделаю его волшебным 💫\n"
        "Первая обработка — БЕСПЛАТНО 🎁"
    )

# Сообщение с текстом "привет" или любое другое
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    if message.text.lower() in ["привет", "hi", "hello"]:
        bot.send_message(message.chat.id, "Теперь отправь фото для обработки ✨")
    else:
        bot.send_message(message.chat.id, "Отправь фото, и я улучшу его! 📸")

# Обработка фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id

    # Проверяем — использовал ли уже бесплатную обработку
    if user_free_used.get(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(
            "💎 Разблокировать магию (Kaspi / Qiwi / USDT)",
            url="https://t.me/morozovaa2204"  # сюда поставь ссылку для связи / оплаты
        )
        markup.add(btn)
        bot.reply_to(
            message,
            "✨ Бесплатная обработка уже использована.\n"
            "Чтобы продолжить — разблокируй магию 💫",
            reply_markup=markup
        )
        return

    # Отмечаем, что бесплатная обработка использована
    user_free_used[user_id] = True

    # Загружаем фото
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        photo_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"
        bot.send_message(message.chat.id, "🔮 Обрабатываю фото... Подожди немного 💫")

        # Отправляем фото в OpenAI для улучшения
        response = client.images.edit(
            model="gpt-image-1",
            image=photo_url,
            prompt="улучши качество фото, убери шум, сделай кожу мягче, ярче фон"
        )

        # Получаем URL результата
        if response.data and len(response.data) > 0:
            image_url = response.data[0].url
            bot.send_photo(message.chat.id, image_url, caption="✨ Готово! Вот улучшенное фото 💖")
        else:
            bot.send_message(message.chat.id, "❌ Не удалось получить улучшенное фото. Попробуй позже.")

    except Exception as e:
        print("Ошибка при обработке фото:", e)
        bot.send_message(message.chat.id, "😔 Произошла ошибка при обработке фото. Попробуй позже!")

# Запуск бота
if __name__ == "__main__":
    print("✅ Бот запущен и готов к работе!")
    bot.polling(none_stop=True)
