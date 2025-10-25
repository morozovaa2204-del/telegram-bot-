import os
import telebot
from dotenv import load_dotenv
from openai import OpenAI

# Загружаем переменные из .env
load_dotenv()

# Подключаем токены
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Проверяем, что ключи подгрузились
if not TELEGRAM_TOKEN or not OPENAI_KEY:
    print("❌ Ошибка: не найден TELEGRAM_TOKEN или OPENAI_KEY в .env файле.")
    exit()

# Инициализация бота и клиента OpenAI
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_KEY)

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я — ИИ бот. Отправь мне сообщение или фото, и я помогу тебе обработать или улучшить изображение!"
    )

# Обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    prompt = message.text.strip()
    bot.send_message(message.chat.id, "💭 Думаю над ответом...")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты — доброжелательный Telegram-бот, который помогает пользователю."},
                {"role": "user", "content": prompt}
            ]
        )

        answer = response.choices[0].message.content
        bot.send_message(message.chat.id, answer)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при ответе: {e}")

# Обработка фотографий
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.send_message(message.chat.id, "✨ Обрабатываю фото через ИИ, подожди немного...")

        # Скачиваем фото
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open("image.png", 'wb') as new_file:
            new_file.write(downloaded_file)

        # Отправляем фото в OpenAI для улучшения
        with open("image.png", "rb") as image_file:
            result = client.images.edits(
                model="gpt-image-1",
                image=image_file,
                prompt="улучши качество, осветли лицо, убери тени и сделай мягкое освещение"
            )

        # Получаем ссылку на улучшенное фото
        image_url = result.data[0].url
        bot.send_message(message.chat.id, f"✅ Готово! Вот улучшенное фото:\n{image_url}")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при обработке фото: {e}")

# Запуск бота
if __name__ == "__main__":
    print("🤖 Бот запущен и работает...")
    bot.polling(none_stop=True, interval=0)
