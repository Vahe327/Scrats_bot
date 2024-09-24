import os
import sqlite3
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from aiogram.utils.deep_linking import decode_payload
from apscheduler.schedulers.background import BackgroundScheduler
import pytz  # Импортируем pytz
import requests
import logging

app = Flask(__name__)
db_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

TELEGRAM_TOKEN = 'Token'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_dir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)



class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    telegram_username = db.Column(db.String(50), unique=True, nullable=True)
    balance = db.Column(db.Integer, default=0)
    clicks_today = db.Column(db.Integer, default=0)
    last_click = db.Column(db.DateTime, nullable=True)
    last_reset = db.Column(db.DateTime, nullable=True)
    subscribed_telegram = db.Column(db.Boolean, default=False)
    subscribed_xcom = db.Column(db.Boolean, default=False)
    daily_earnings = db.Column(db.Integer, default=0)
    last_end_time_scrats = db.Column(db.DateTime, nullable=True)
    last_start_time_scrats = db.Column(db.DateTime, nullable=True)
    last_end_time_boll = db.Column(db.DateTime, nullable=True)
    last_start_time_boll = db.Column(db.DateTime, nullable=True)
    last_end_time_cube = db.Column(db.DateTime, nullable=True)
    last_start_time_cube = db.Column(db.DateTime, nullable=True)
    last_end_time_slots = db.Column(db.DateTime, nullable=True)
    last_start_time_slots = db.Column(db.DateTime, nullable=True)
    subscribed_container_1 = db.Column(db.Boolean, default=False)
    subscribed_container_2 = db.Column(db.Boolean, default=False)
    subscribed_container_3 = db.Column(db.Boolean, default=False)
    subscribed_container_4 = db.Column(db.Boolean, default=False)
    subscribed_container_5 = db.Column(db.Boolean, default=False)
    subscribed_container_6 = db.Column(db.Boolean, default=False)
    subscribed_container_7 = db.Column(db.Boolean, default=False)
    subscribed_container_8 = db.Column(db.Boolean, default=False)
    subscribed_container_9 = db.Column(db.Boolean, default=False)
    subscribed_container_10 = db.Column(db.Boolean, default=False)
    subscribed_container_11 = db.Column(db.Boolean, default=False)
    subscribed_container_12 = db.Column(db.Boolean, default=False)
    subscribed_container_13 = db.Column(db.Boolean, default=False)
    total_rewards = db.Column(db.Integer, default=0)
   
class Referral(db.Model):
    __tablename__ = 'referral'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    referred_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    referral_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def init_db():
    with app.app_context():
        db.create_all()
        print("База данных инициализирована")

def get_telegram_username(user_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getChat"
    params = {'chat_id': user_id}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['ok']:
            return data['result'].get('username', None)
    return None

def update_telegram_usernames():
    with app.app_context():
        users = User.query.filter(User.id >= 15000).all()
        for user in users:
            if not user.telegram_username:
                username = get_telegram_username(user.id)
                if username:
                    user.telegram_username = username
        db.session.commit()

@app.route('/')
def index():
    user_id = request.args.get('user_id')
    if user_id:
        try:
            user_id = int(user_id)
            user = db.session.get(User, user_id)
            if not user:
                user = User(id=user_id, daily_earnings=0)  # Инициализируем daily_earnings
                db.session.add(user)
                db.session.commit()
        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

    return render_template('index.html', user_id=user.id, balance=user.balance, telegram_username=user.telegram_username)

@app.route('/index.html')
def index_html():
    user_id = request.args.get('user_id')
    if user_id:
        try:
            user_id = int(user_id)
            user = db.session.get(User, user_id)
            if not user:
                user = User(id=user_id, daily_earnings=0)  # Инициализируем daily_earnings
                db.session.add(user)
                db.session.commit()
                # Обновление имени пользователя
                update_telegram_username(user)
        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

    return render_template('index.html', user_id=user.id, balance=user.balance, telegram_username=user.telegram_username)

@app.route('/start', methods=['GET'])
def start():
    referral_code = request.args.get('start')
    user_id = request.args.get('user_id')

    # Проверка и создание пользователя по user_id
    if user_id:
        try:
            user_id = int(user_id)
            user = db.session.get(User, user_id)
            if not user:
                user = User(id=user_id, daily_earnings=0)  # Инициализируем daily_earnings
                db.session.add(user)
                db.session.commit()
        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

    # Обработка реферального кода
    if referral_code:
        try:
            # Декодирование реферального кода
            referral_id = int(referral_code.replace("user_", ""))
            referrer = db.session.get(User, referral_id)
            if not referrer:
                return "User not found", 404

            # Создание нового пользователя
            new_user = User(balance=0, clicks_today=0, last_click=None, last_reset=None, daily_earnings=0)
            db.session.add(new_user)
            db.session.flush()  # Используем flush() для получения нового ID пользователя

            app.logger.debug(f"New user ID: {new_user.id}")

            # Обновление или создание записи реферала
            new_referral = Referral(user_id=referrer.id, referral_id=referrer.id, referred_user_id=new_user.id)
            existing_referral = db.session.query(Referral).filter_by(referral_id=referrer.id, referred_user_id=new_user.id).first()
            if not existing_referral:
                db.session.add(new_referral)
                db.session.commit()

            print(f"Создана запись реферала: referral_id={referrer.id}, referred_user_id={new_user.id}")

            # Начисление 100 токенов всем пользователям, кроме нового пользователя
            total_users = User.query.count()
            if total_users <= 1000000:
                users = User.query.all()
                for user in users:
                    if user.id != new_user.id:  # Исключаем нового пользователя
                        user.balance += 100
                        db.session.merge(user)  # Добавляем пользователя в сессию
                        print(f"Пользователь с ID: {user.id} получил 100 токенов. Новый баланс: {user.balance}")
                db.session.commit()
                print(f"Начислено 100 токенов каждому пользователю, кроме нового пользователя")

            return render_template('index.html', user_id=new_user.id, balance=new_user.balance)

        except (IndexError, ValueError) as e:
            print(f"Ошибка при обработке реферального кода: {e}")
            return "Invalid referral code", 400

    # Если нет referral_code, проверяем и создаем запись реферала, если ее нет
    if user_id:
        try:
            user_id = int(user_id)
            user = db.session.get(User, user_id)
            if not user:
                return "User not found", 404
            
            # Проверка и создание записи реферала
            existing_referral = db.session.query(Referral).filter_by(user_id=user_id).first()
            if not existing_referral:
                new_referral = Referral(user_id=user_id, referral_id=user_id)
                db.session.add(new_referral)
                db.session.commit()

        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

    return render_template('index.html', user_id=user.id, balance=user.balance)


@app.route('/register_with_referral', methods=['POST'])
def register_with_referral():
    data = request.get_json()
    referral_id = data.get('referral_id')
    new_user_id = data.get('new_user_id')

    if not referral_id or not new_user_id:
        return jsonify({"message": "Referral ID or New User ID missing"}), 400

    referral_user = db.session.get(User, referral_id)
    new_user = db.session.get(User, new_user_id)

    if not referral_user:
        return jsonify({"message": "Referral not found"}), 404
    if not new_user:
        return jsonify({"message": "New User not found"}), 404

    # Создаем запись реферала
    new_referral = Referral(user_id=referral_id, referred_user_id=new_user_id, referral_id=referral_id)
    db.session.add(new_referral)
    db.session.commit()
    print(f"Создана запись реферала: user_id={referral_id}, referred_user_id={new_user_id}")

    referral_user.balance += 20000  # Добавляем баланс рефереру
    db.session.commit()
    print(f"Баланс пользователя с ID {referral_id} увеличен на 20000")

    # Начисление 100 токенов всем пользователям, кроме нового пользователя
    total_users = User.query.count()
    if total_users <= 1000000:
        users = User.query.all()
        for user in users:
            if user.id != new_user.id:  # Исключаем нового пользователя
                user.balance += 100
        db.session.commit()  # Сохраняем изменения сразу после изменения балансов
        print(f"Начислено 100 токенов каждому пользователю, кроме нового пользователя")

    return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 200

@app.route('/update_rewards', methods=['POST'])
def update_rewards():
    data = request.json
    user_id = data['user_id']
    reward = data['reward']
    
    user = User.query.filter_by(id=user_id).first()
    if user:
        user.total_rewards += reward
        db.session.commit()
        return jsonify({'status': 'success', 'total_rewards': user.total_rewards})
    return jsonify({'status': 'error', 'message': 'User not found'})

@app.route('/get_rewards', methods=['GET'])
def get_rewards():
    user_id = request.args.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    if user:
        return jsonify({'status': 'success', 'total_rewards': user.total_rewards})
    return jsonify({'status': 'error', 'message': 'User not found'})
    
@app.route('/check_balances', methods=['GET'])
def check_balances():
    users = User.query.all()
    for user in users:
        print(f"User ID: {user.id}, Balance: {user.balance}")
    return "Check console for balances"

@app.route('/static')
def static_page():
    user_id = request.args.get('user_id')
    if user_id:
        try:
            user_id = int(user_id)
            if user_id >= 10000:
                top_users = User.query.order_by(User.balance.desc()).limit(10).all()
                user_data = [{'id': user.id, 'telegram_username': user.telegram_username or 'N/A', 'balance': user.balance} for user in top_users]
                return render_template('static.html', user_id=user_id, users=user_data)
            else:
                top_users = User.query.filter(User.id >= 10000).order_by(User.balance.desc()).limit(10).all()
                user_data = [{'id': user.id, 'telegram_username': user.telegram_username or 'N/A', 'balance': user.balance} for user in top_users]
                return render_template('static.html', user_id=user_id, users=user_data)
        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

@app.route('/click', methods=['POST'])
def click():
    user_id = int(request.form.get('user_id'))
    user = db.session.get(User, user_id)
    if not user:
        return "User not found", 404

    dubai_tz = pytz.timezone('Asia/Dubai')  # GMT+4 timezone
    current_time = datetime.now(dubai_tz)
    if user.last_reset:
        # Преобразование user.last_reset в offset-aware datetime
        user_last_reset_aware = user.last_reset.replace(tzinfo=dubai_tz)
        if (current_time - user_last_reset_aware) >= timedelta(hours=24):
            user.clicks_today = 0
            user.last_reset = current_time
            user.daily_earnings = 0  # Сброс дневного заработка
    else:
        user.last_reset = current_time
        user.clicks_today = 0
        user.daily_earnings = 0  # Инициализируем daily_earnings

    if user.clicks_today >= 2000:
        return jsonify({"message": "Click limit reached for today"}), 429

    user.clicks_today += 1
    user.balance += 1000
    user.daily_earnings += 1000  # Увеличение дневного заработка
    user.last_click = current_time

    db.session.commit()

    return jsonify({
        "message": "Success",
        "clicks_today": user.clicks_today,
        "clicks_remaining": 2000 - user.clicks_today
    }), 200

@app.route('/clicks', methods=['GET'])
def get_clicks():
    user_id = int(request.args.get('user_id'))
    user = db.session.get(User, user_id)
    if not user:
        return "User not found", 404

    return jsonify({
        "clicks_today": user.clicks_today,
        "clicks_remaining": 2000 - user.clicks_today
    }), 200

def reset_clicks():
    dubai_tz = pytz.timezone('Asia/Dubai')  # GMT+4 timezone
    current_time = datetime.now(dubai_tz)
    users = User.query.all()
    for user in users:
        user.clicks_today = 0
        user.last_reset = current_time
        user.daily_earnings = 0  # Сбрасываем daily_earnings каждый день
    db.session.commit()
    print(f"Clicks reset at {current_time}")

scheduler = BackgroundScheduler(timezone='Asia/Dubai')
scheduler.add_job(reset_clicks, 'cron', hour=0, minute=0)  # 00:00 GMT+4
scheduler.start()

@app.route('/balance')
def get_balance():
    user_id = request.args.get('user_id')
    conn = sqlite3.connect(os.path.join(db_dir, 'data.db'))
    cursor = conn.cursor()
    
    cursor.execute("SELECT balance FROM user WHERE id = ?", (user_id,))
    balance = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify(balance=balance)

@app.route('/referral-info', methods=['GET'])
def referral_info():
    user_id = request.args.get('user_id')
    if user_id:
        try:
            user_id = int(user_id)
            referrals = db.session.query(Referral, User).join(User, User.id == Referral.referred_user_id).filter(Referral.referral_id == user_id).all()
            referral_data = [{"id": u.id, "telegram_username": u.telegram_username, "balance": u.balance, "earned": u.daily_earnings * 0.05} for r, u in referrals]
            total_users = User.query.count()

            print(f"Referrals for user_id {user_id}: {referral_data}")

            total_earned = sum([r["earned"] for r in referral_data])

            return jsonify({
                "referrals": referral_data,
                "total_users": total_users,
                "total_earned": total_earned
            })
        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    user_id = data.get('user_id')
    container_id = data.get('container_id')
    reward = data.get('reward', 50)  # По умолчанию 50, если не указано

    if not user_id or not container_id:
        logging.error("Missing user_id or container_id")
        return jsonify({"message": "Missing user_id or container_id"}), 400

    user = db.session.get(User, user_id)
    if not user:
        logging.error(f"User {user_id} not found")
        return jsonify({"message": "User not found"}), 404

    subscription_field = f"subscribed_container_{container_id}"
    
    logging.debug(f"User ID: {user_id}, Container ID: {container_id}, Field: {subscription_field}")

    if getattr(user, subscription_field):
        logging.info(f"User {user_id} already subscribed to container {container_id}")
        return jsonify({"message": f"Already subscribed to container {container_id}"}), 200

    user.balance += reward
    setattr(user, subscription_field, True)
    db.session.commit()
    
    logging.info(f"User {user_id} subscribed to container {container_id} and balance updated to {user.balance}")
    return jsonify({"message": f"Subscribed to container {container_id}, balance updated", "balance": user.balance}), 200

@app.route('/check_subscriptions', methods=['GET'])
def check_subscriptions():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({"message": "User ID missing"}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    subscriptions = [
        {"container_id": i, "subscribed": getattr(user, f"subscribed_container_{i}")}
        for i in range(1, 14)
    ]

    return jsonify({"subscriptions": subscriptions})

@app.route('/create_referral', methods=['POST'])
def create_referral():
    data = request.get_json()
    user_id = data.get('user_id')
    referral_id = data.get('referral_id')

    if not user_id or not referral_id:
        return jsonify({"message": "User ID or Referral ID missing"}), 400

    try:
        user_id = int(user_id)
        referral_id = int(referral_id)
        
        user = User.query.get(user_id)
        if not user:
            # Создаем нового пользователя, если он не существует
            user = User(id=user_id, daily_earnings=0)  # Инициализируем daily_earnings
            db.session.add(user)
            db.session.commit()

        referrer = User.query.get(referral_id)
        if not referrer:
            return jsonify({"message": "Referrer not found"}), 404

        # Проверка на существование записи реферала
        existing_referral = Referral.query.filter_by(user_id=user_id, referral_id=referral_id).first()
        if existing_referral:
            return jsonify({"message": "Referral already exists"}), 400

        # Создание новой записи реферала
        referral = Referral(user_id=user_id, referral_id=referral_id, referred_user_id=user.id)
        db.session.add(referral)
        db.session.commit()

        user.balance += 20000  # Добавляем баланс пользователю
        db.session.commit()
        print(f"Баланс пользователя с ID {referral_id} увеличен на 20000")

        return jsonify({"message": "Referral created successfully"}), 200

    except ValueError:
        return jsonify({"message": "Invalid User ID or Referral ID"}), 400

@app.route('/referrals/<int:user_id>')
def show_referrals(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return "User not found", 404

    # Получение рефералов пользователя
    referrals = db.session.query(Referral, User).join(User, User.id == Referral.referred_user_id).filter(Referral.referral_id == user_id).all()

    referral_data = []
    total_earned = 0
    for referral, referred_user in referrals:
        earned = referred_user.daily_earnings * 0.05  # 5% от дневного заработка реферала
        total_earned += earned
        referral_data.append({
            'telegram_username': referred_user.telegram_username or referred_user.id,
            'balance': referred_user.balance,
            'earned': earned
        })

    return render_template('referrals.html', user_id=user.id, telegram_username=user.telegram_username, referrals=referral_data, total_earned=total_earned)

@app.route('/withdraw_earnings', methods=['POST'])
def withdraw_earnings():
    data = request.get_json()
    user_id = data.get('user_id')
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    referrals = db.session.query(Referral, User).join(User, User.id == Referral.referred_user_id).filter(Referral.referral_id == user_id).all()
    total_earned = sum(referred_user.daily_earnings * 0.05 for _, referred_user in referrals)
    
    user.balance += total_earned
    db.session.commit()

    return jsonify({'success': True, 'message': 'Earnings withdrawn successfully', 'new_balance': user.balance})

@app.route('/add_new_user', methods=['POST'])
def add_new_user():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return "User ID missing", 400

    try:
        user_id = int(user_id)
        user = User.query.filter_by(id=user_id).first()
        if not user:
            user = User(id=user_id, daily_earnings=0)  # Инициализируем daily_earnings
            db.session.add(user)
            db.session.commit()

            # Начисление бонуса всем пользователям, кроме только что добавленного
            all_users = User.query.filter(User.id != user_id).all()
            for user in all_users:
                user.balance += 100
            db.session.commit()

            return "New user added successfully. Bonuses added to all existing users.", 200
        else:
            return "User with this ID already exists", 400
    except ValueError:
        return "Invalid user ID", 400

@app.route('/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect(os.path.join(db_dir, 'data.db'))
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    
    conn.close()
    
    return jsonify(users)

@app.route('/roadmap.html', methods=['GET'])
def roadmap():
    # Здесь можно добавить логику, если необходимо
    return render_template('roadmap.html')

@app.route('/Characteristic.html', methods=['GET'])
def characteristic():
    # Здесь можно добавить логику, если необходимо
    return render_template('Characteristic.html')

@app.route('/ob.html', methods=['GET'])
def ob():
    return render_template('ob.html')

@app.route('/update_username/<int:user_id>')
def update_username(user_id):
    username = request.args.get('username')
    if not username:
        return "Username missing", 400
    
    user = User.query.get(user_id)
    if user:
        user.telegram_username = username
        db.session.commit()
        return f"Username updated for user {user_id}: {username}"
    else:
        return "User not found", 404

@app.route('/all-users-info', methods=['GET'])
def all_users_info():
    users = User.query.all()
    user_data = [{'telegram_username': user.telegram_username, 'balance': user.balance} for user in users]
    return jsonify({'users': user_data})

@app.route('/referrals.html')
def referrals():
    user_id = request.args.get('user_id')
    if user_id:
        try:
            user_id = int(user_id)
            user = db.session.get(User, user_id)
            if user:
                return render_template('referrals.html', user_id=user_id)
        except ValueError:
            return "Invalid user ID", 400
    return "User ID missing", 400

@app.route('/game.html')
def game_html():
    user_id = request.args.get('user_id')
    game_type = request.args.get('game_type')  # Получаем тип игры из запроса
    
    if user_id:
        try:
            user_id = int(user_id)
            user = db.session.get(User, user_id)
            if not user:
                user = User(id=user_id, daily_earnings=0)  # Инициализируем daily_earnings
                db.session.add(user)
                db.session.commit()
        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

    can_play = True
    remaining_time = 0
    if game_type == 'SCRATS' and user.last_start_time_scrats:
        elapsed_time = datetime.utcnow() - user.last_start_time_scrats
        if elapsed_time < timedelta(hours=2):
            can_play = False
            remaining_time = (timedelta(hours=2) - elapsed_time).total_seconds()
    elif game_type == 'BOLL' and user.last_start_time_boll:
        elapsed_time = datetime.utcnow() - user.last_start_time_boll
        if elapsed_time < timedelta(hours=1):
            can_play = False
            remaining_time = (timedelta(hours=1) - elapsed_time).total_seconds()
    elif game_type == 'CUBE' and user.last_start_time_cube:
        elapsed_time = datetime.utcnow() - user.last_start_time_cube
        if elapsed_time < timedelta(hours=4):
            can_play = False
            remaining_time = (timedelta(hours=4) - elapsed_time).total_seconds()
    elif game_type == 'SLOT' and user.last_start_time_slots:
        elapsed_time = datetime.utcnow() - user.last_start_time_slots
        if elapsed_time < timedelta(hours=1):
            can_play = False
            remaining_time = (timedelta(hours=1) - elapsed_time).total_seconds()

    return render_template('game.html', user_id=user.id, can_play=can_play, remaining_time=remaining_time)

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.get_json()
    user_id = data.get('user_id')
    game_type = data.get('game_type')

    if not user_id or not game_type:
        return jsonify({'status': 'error', 'message': 'User ID or game type missing'}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    if game_type == 'SCRATS':
        user.last_start_time_scrats = datetime.utcnow()
    elif game_type == 'BOLL':
        user.last_start_time_boll = datetime.utcnow()
    elif game_type == 'CUBE':
        user.last_start_time_cube = datetime.utcnow()
    elif game_type == 'SLOT':
        user.last_start_time_slots = datetime.utcnow()

    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/update_balance', methods=['POST'])
def update_balance():
    data = request.get_json()
    user_id = data['user_id']
    balance = data['balance']
    game_type = data['game_type']

    user = db.session.get(User, user_id)
    if user:
        user.balance += balance
        user.daily_earnings += balance  # Увеличение дневного заработка
        if game_type == 'SCRATS':
            user.last_end_time_scrats = datetime.utcnow()
        elif game_type == 'BOLL':
            user.last_end_time_boll = datetime.utcnow()
        elif game_type == 'CUBE':
            user.last_end_time_cube = datetime.utcnow()
        elif game_type == 'SLOT':
            user.last_end_time_slots = datetime.utcnow()
        db.session.commit()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

@app.route('/can_play', methods=['GET'])
def can_play():
    user_id = request.args.get('user_id')
    game_type = request.args.get('game_type')

    if not user_id or not game_type:
        return jsonify({'status': 'error', 'message': 'User ID or game type missing'}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    current_time = datetime.utcnow()
    remaining_time = 0

    if game_type == 'SCRATS':
        if user.last_end_time_scrats:
            elapsed_time = current_time - user.last_end_time_scrats
            if elapsed_time < timedelta(hours=2):
                remaining_time = (timedelta(hours=2) - elapsed_time).total_seconds()
                return jsonify({'can_play': False, 'remaining_time': remaining_time})
    elif game_type == 'BOLL':
        if user.last_end_time_boll:
            elapsed_time = current_time - user.last_end_time_boll
            if elapsed_time < timedelta(hours=1):
                remaining_time = (timedelta(hours=1) - elapsed_time).total_seconds()
                return jsonify({'can_play': False, 'remaining_time': remaining_time})
    elif game_type == 'CUBE':
        if user.last_end_time_cube:
            elapsed_time = current_time - user.last_end_time_cube
            if elapsed_time < timedelta(hours=4):
                remaining_time = (timedelta(hours=4) - elapsed_time).total_seconds()
                return jsonify({'can_play': False, 'remaining_time': remaining_time})
    elif game_type == 'SLOT':
        if user.last_end_time_slots:
            elapsed_time = current_time - user.last_end_time_slots
            if elapsed_time < timedelta(hours=1):
                remaining_time = (timedelta(hours=1) - elapsed_time).total_seconds()
                return jsonify({'can_play': False, 'remaining_time': remaining_time})

    return jsonify({'can_play': True})

@app.route('/scrats.html')
def scrats_html():
    user_id = request.args.get('user_id')
    if user_id:
        try:
            user_id = int(user_id)
            user = db.session.get(User, user_id)
            if not user:
                user = User(id=user_id, daily_earnings=0)  # Инициализируем daily_earnings
                db.session.add(user)
                db.session.commit()
        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

    return render_template('scrats.html', user_id=user.id, balance=user.balance)

@app.route('/boll.html')
def boll_html():
    user_id = request.args.get('user_id')
    if user_id:
        try:
            user_id = int(user_id)
            user = db.session.get(User, user_id)
            if not user:
                user = User(id=user_id, daily_earnings=0)  # Инициализируем daily_earnings
                db.session.add(user)
                db.session.commit()
        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

    return render_template('boll.html', user_id=user.id, balance=user.balance)

@app.route('/cube.html')
def cube_html():
    user_id = request.args.get('user_id')
    if user_id:
        try:
            user_id = int(user_id)
            user = db.session.get(User, user_id)
            if not user:
                user = User(id=user_id, daily_earnings=0)  # Инициализируем daily_earnings
                db.session.add(user)
                db.session.commit()
        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

    return render_template('cube.html', user_id=user.id, balance=user.balance)

@app.route('/slot.html')
def slot_html():
    user_id = request.args.get('user_id')
    if user_id:
        try:
            user_id = int(user_id)
            user = db.session.get(User, user_id)
            if not user:
                user = User(id=user_id, daily_earnings=0)  # Инициализируем daily_earnings
                db.session.add(user)
                db.session.commit()
        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

    return render_template('slot.html', user_id=user.id, balance=user.balance)

#def update_existing_users():
  #  with app.app_context():
  #      users = User.query.all()
  #      for user in users:
  #         if user.daily_earnings is None:
  #              user.daily_earnings = 0
 #       db.session.commit()
#
#update_existing_users()

@app.route('/admin')
def admin():
    users = User.query.all()
    referrals = Referral.query.all()
    return render_template('admin.html', users=users, referrals=referrals)

@app.route('/admin1')
def admin1():
    users = User.query.all()
    referrals = Referral.query.all()
    return render_template('admin1.html', users=users, referrals=referrals)

@app.route('/user_activity', methods=['GET'])
def user_activity():
    users = User.query.filter(User.id >= 1007).all()
    user_data = []

    for user in users:
        activity = None
        if user.last_start_time_scrats and (datetime.utcnow() - user.last_start_time_scrats).total_seconds() < 7200:
            activity = 'Playing SCRATS'
        elif user.last_start_time_boll and (datetime.utcnow() - user.last_start_time_boll).total_seconds() < 3600:
            activity = 'Playing BOLL'
        elif user.last_start_time_cube and (datetime.utcnow() - user.last_start_time_cube).total_seconds() < 14400:
            activity = 'Playing CUBE'
        elif user.last_start_time_slots and (datetime.utcnow() - user.last_start_time_slots).total_seconds() < 3600:
            activity = 'Playing SLOTS'
        elif user.last_click and (datetime.utcnow() - user.last_click).total_seconds() < 60:
            activity = 'Clicking'

        user_data.append({
            'id': user.id,
            'telegram_username': user.telegram_username,
            'balance': user.balance,
            'activity': activity
        })

    return jsonify(user_data)
    
@app.route('/block_user/<int:user_id>', methods=['POST'])
def block_user(user_id):
    data = request.get_json()
    game_type = data.get('game_type')
    
    if not game_type:
        return jsonify({'status': 'error', 'message': 'Game type is required'}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    current_time = datetime.utcnow()
    
    if game_type == 'SCRATS':
        user.last_end_time_scrats = current_time
    elif game_type == 'BOLL':
        user.last_end_time_boll = current_time
    elif game_type == 'CUBE':
        user.last_end_time_cube = current_time
    elif game_type == 'SLOT':
        user.last_end_time_slots = current_time
    else:
        return jsonify({'status': 'error', 'message': 'Invalid game type'}), 400

    db.session.commit()

    return jsonify({'status': 'success', 'message': f'User blocked from playing {game_type} for 24 hours'})

from datetime import datetime, timedelta

from datetime import datetime, timedelta

@app.route('/user_game_info/<int:user_id>', methods=['GET'])
def user_game_info(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'Пользователь не найден'}), 404

    def format_time(time):
        return time.strftime('%Y-%m-%d %H:%M:%S') if time else 'Неизвестно'

    game_info = {
        'SCRATS': {
            'last_start': format_time(user.last_start_time_scrats),
            'last_end': format_time(user.last_end_time_scrats),
            'earnings': user.daily_earnings,
        },
        'BOLL': {
            'last_start': format_time(user.last_start_time_boll),
            'last_end': format_time(user.last_end_time_boll),
            'earnings': user.daily_earnings,
        },
        'CUBE': {
            'last_start': format_time(user.last_start_time_cube),
            'last_end': format_time(user.last_end_time_cube),
            'earnings': user.daily_earnings,
        },
        'SLOT': {
            'last_start': format_time(user.last_start_time_slots),
            'last_end': format_time(user.last_end_time_slots),
            'earnings': user.daily_earnings,
        }
    }

    server_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    return jsonify({
        'status': 'success',
        'game_info': game_info,
        'server_time': server_time
    })

@app.route('/send_message', methods=['POST'])
def send_message_route():
    data = request.get_json()
    user_id = data.get('user_id')
    message = data.get('message')

    if not user_id or not message:
        return jsonify({'status': 'error', 'message': 'User ID или сообщение отсутствует'}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'Пользователь не найден'}), 404

    send_message(user.id, message)
    return jsonify({'status': 'success', 'message': 'Сообщение отправлено'})

def send_message(user_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': user_id,
        'text': message
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"Сообщение отправлено пользователю {user_id}")
    else:
        print(f"Ошибка при отправке сообщения пользователю {user_id}: {response.text}")

@app.route('/send_message_all', methods=['POST'])
def send_message_all():
    data = request.get_json()
    message = data.get('message')

    if not message:
        return jsonify({'status': 'error', 'message': 'Message text missing'}), 400

    users = User.query.all()
    for user in users:
        send_message(user.id, message)

    return jsonify({'status': 'success', 'message': 'Message sent to all users'})

@app.route('/earn.html')
def earn_html():
    user_id = request.args.get('user_id')
    if user_id:
        try:
            user_id = int(user_id)
            user = db.session.get(User, user_id)
            if not user:
                user = User(id=user_id, daily_earnings=0)  # Инициализируем daily_earnings
                db.session.add(user)
                db.session.commit()
        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

    subscriptions = [
        {"container_id": i, "subscribed": getattr(user, f"subscribed_container_{i}")}
        for i in range(1, 14)
    ]

    return render_template('earn.html', user_id=user.id, balance=user.balance, subscriptions=subscriptions)

@app.route('/add_balance', methods=['POST'])
def add_balance():
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount')

    if user_id is None or amount is None:
        return jsonify({'status': 'error', 'message': 'Неверные данные'}), 400

    user = User.query.get(user_id)
    if user is None:
        return jsonify({'status': 'error', 'message': 'Пользователь не найден'}), 404

    user.balance += amount
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Баланс обновлен'})

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

