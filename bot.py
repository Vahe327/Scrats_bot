import subprocess
import requests
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackContext

# Телеграм токен
TELEGRAM_TOKEN = 'Token'  # Замените на ваш токен

# URL вашего приложения
FLASK_APP_URL = 'https://bot.cryptosymbiotic.com'

# Логирование
logging.basicConfig(level=logging.INFO)

# Функция запуска Flask-приложения
def start_flask():
    logging.info("Запуск Flask-приложения...")
    flask_process = subprocess.Popen(['python3', 'app.py'])
    logging.info(f"Flask-приложение запущено с PID: {flask_process.pid}")
    return flask_process

def get_telegram_username(user_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getChat"
    params = {'chat_id': user_id}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        logging.info(f"Telegram API Response: {data}")
        if data['ok']:
            return data['result'].get('username', None)
    else:
        logging.error(f"Failed to fetch username: {response.text}")
    return None

# Функция для обработки новых пользователей через реферальную ссылку
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id  # Извлечение user_id из сообщения
    referral_arg = context.args[0] if context.args else None  # Извлечение referral_id из аргументов команды
    referral_id = referral_arg.replace('user_', '') if referral_arg else None

    # Получение и обновление имени пользователя Telegram
    telegram_username = get_telegram_username(user_id)
    if telegram_username:
        logging.info(f"Получено имя пользователя: {telegram_username}")
        # Отправляем запрос на сервер для обновления имени пользователя
        update_url = f"{FLASK_APP_URL}/update_username/{user_id}?username={telegram_username}"
        update_response = requests.get(update_url)
        logging.info(f"Ответ от сервера Flask: {update_response.text}")
    else:
        logging.warning(f"Не удалось получить имя пользователя для user_id: {user_id}")

    # Создание записи реферала, если referral_id определен
    if referral_id:
        referral_url = f"{FLASK_APP_URL}/create_referral"
        referral_data = {'user_id': user_id, 'referral_id': int(referral_id)}
        referral_response = requests.post(referral_url, json=referral_data)
        logging.info(f"Ответ от сервера Flask при создании реферала: {referral_response.text}")

    # Создание кнопок с WebAppInfo
    keyboard = [
        [InlineKeyboardButton(text="START the GAME", web_app=WebAppInfo(url=f'{FLASK_APP_URL}/start?user_id={user_id}'))],
        [InlineKeyboardButton(text="ROADMAP", web_app=WebAppInfo(url=f'{FLASK_APP_URL}/roadmap.html'))],
        [InlineKeyboardButton(text="Characteristic", web_app=WebAppInfo(url=f'{FLASK_APP_URL}/Characteristic.html'))],
        [InlineKeyboardButton(text="Объяснение Игр", web_app=WebAppInfo(url=f'{FLASK_APP_URL}/ob.html'))]  # Новая кнопка
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Текст приветствия
    welcome_text = (
        "Добро пожаловать в Игру SCRATS! Наша игра создана для того, чтобы у людей был шанс играть и зарабатывать токены SCRATS на проекте SCRATS. "
        "Вы можете заработать токены, кликая на логотипе SCRATS, и еще больше, подписываясь на наши социальные сети и приглашая рефералов.\n\n"
        "У нас абсолютно новая система вознаграждений за приглашение рефералов. В нашей системе не имеет значения, кто пригласил реферала — все получат по 100 SCRATS.\n\n"
        "Игра продлится не более двух месяцев. После окончания этих двух месяцев мы выйдем на биржи и откроем вывод токенов, чтобы вы могли вывести свои токены и продать их. Спешите заработать токены SCRATS!\n\n"
        "Система игры:\n"
        "1. Кликай и зарабатывай: Получайте по 1000 SCRATS в день за 2000 кликов, что составляет 2 000 000 SCRATS.\n"
        "2. Подписывайтесь на соцсети: Подпишитесь на наш Telegram и X.com (Twitter) и получите по 50 000 SCRATS за каждую подписку.\n"
        "3. Приглашайте новых пользователей: За каждого нового пользователя вы получите по 20000 SCRATS и 5%.\n\n"
    )

    # Отправляем изображение и сообщение с кнопками
    await update.message.reply_photo(photo=open('static/nk.webp', 'rb'), caption=f'{welcome_text}Hello, yours User ID: {user_id}', reply_markup=reply_markup)

def main():
    logging.info("Запуск Telegram-бота...")
    flask_process = start_flask()

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    application.run_polling()
    logging.info("Telegram-бот запущен")

    # Завершаем Flask-приложение при завершении работы бота
    flask_process.terminate()

if __name__ == '__main__':
    main()

