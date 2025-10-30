import telebot
import os
from openai import OpenAI
from flask import Flask, request
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

# Получаем токены
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Ошибка: отсутствует TELEGRAM_TOKEN или OPENAI_API_KEY в .env")

# Инициализация клиентов
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)

# Корневой маршрут для проверки
@app.route('/')
def home():
    return "🤖 Бот работает через webhook!", 200

# Маршрут для получения сообщений от Telegram
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    json_update = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_update)
    bot.process_new_updates([update])
    return '', 200

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Привет! Я бот с искусственным интеллектом. Напиши что-нибудь или попроси создать фото!")

# Основная логика общения
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_text = message.text.strip().lower()

        # Если пользователь просит фото
        if any(word in user_text for word in ["сделай фото", "создай картинку", "нарисуй", "generate image"]):
            prompt = message.text
            bot.reply_to(message, "🎨 Создаю изображение, подожди немного...")

            image = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024"
            )
            image_url = image.data[0].url
            bot.send_photo(message.chat.id, image_url, caption="Вот твоё изображение 😊")
            return

        # Ответ от ChatGPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты дружелюбный Telegram-ассистент."},
                {"role": "user", "content": user_text},
            ]
        )

        ai_answer = response.choices[0].message.content
        bot.reply_to(message, ai_answer)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {str(e)}")

# Запуск Flask-сервера
if __name__ == "__main__":
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    port = int(os.environ.get("PORT", 5000))

    bot.remove_webhook()
    if render_url:
        bot.set_webhook(url=f"{render_url}/{TELEGRAM_TOKEN}")
        print(f"✅ Webhook установлен: {render_url}/{TELEGRAM_TOKEN}")
    else:
        print("⚠️ Переменная RENDER_EXTERNAL_URL не найдена")

    app.run(host="0.0.0.0", port=port)
