from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Integer, default=0)
    clicks_today = db.Column(db.Integer, default=0)
    last_click = db.Column(db.DateTime, nullable=True)
    last_reset = db.Column(db.DateTime, nullable=True)

class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    referred_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def init_db():
    with app.app_context():
        db.create_all()
        print("База данных инициализирована")

@app.route('/')
def index():
    user_id = request.args.get('user_id')
    print(f"Получен запрос на / с user_id: {user_id}")
    
    if user_id:
        try:
            user_id = int(user_id)
            user = User.query.get(user_id)
            if not user:
                user = User(id=user_id)
                db.session.add(user)
                db.session.commit()
                print(f"Создан новый пользователь с ID: {user.id}")
        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

    return render_template('index.html', user_id=user.id, balance=user.balance)

@app.route('/start', methods=['GET'])
def start():
    user_id = request.args.get('user_id')
    print(f"Получен запрос на /start с user_id: {user_id}")
    
    if user_id:
        try:
            user_id = int(user_id)
            user = User.query.get(user_id)
            if not user:
                user = User(id=user_id)
                db.session.add(user)
                db.session.commit()
                print(f"Создан новый пользователь с ID: {user.id}")
        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

    return render_template('index.html', user_id=user.id, balance=user.balance)

@app.route('/static')
def static_page():
    user_id = request.args.get('user_id')
    print(f"Получен запрос на /static с user_id: {user_id}")

    if user_id:
        try:
            user_id = int(user_id)
            referrals = db.session.query(Referral, User).join(User, User.id == Referral.referred_id).filter(Referral.referrer_id == user_id).all()
            referral_data = [{'user_id': u.id, 'balance': u.balance} for r, u in referrals]
            return render_template('static.html', referral_data=referral_data)
        except ValueError:
            return "Invalid user ID", 400
    else:
        return "User ID missing", 400

@app.route('/click', methods=['POST'])
def click():
    user_id = int(request.form.get('user_id'))
    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    current_time = datetime.now()
    if user.last_reset and (current_time - user.last_reset) >= timedelta(hours=24):
        user.clicks_today = 0
        user.last_reset = current_time

    if user.clicks_today >= 2000:
        return jsonify({"message": "Click limit reached for today"}), 429

    user.clicks_today += 1
    user.balance += 1000
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
    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    return jsonify({
        "clicks_today": user.clicks_today,
        "clicks_remaining": 2000 - user.clicks_today
    }), 200

@app.route('/referral/<int:referrer_id>')
def referral(referrer_id):
    referrer = User.query.get(referrer_id)
    if not referrer:
        return "Referrer not found", 404

    new_user = User(balance=0, clicks_today=0, last_click=None, last_reset=None)
    db.session.add(new_user)
    db.session.commit()

    referral = Referral(referrer_id=referrer_id, referred_id=new_user.id)
    db.session.add(referral)
    db.session.commit()

    return render_template('index.html', user_id=new_user.id, balance=new_user.balance)

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
