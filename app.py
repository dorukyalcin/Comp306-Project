from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Wallet

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:zits0/tanker@localhost:3306/casino_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    currency = data.get('currency', 'USD')
    if not username or not email or not password:
        return jsonify({'error': 'Missing fields'}), 400
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'Username or email already exists'}), 409
    pw_hash = generate_password_hash(password)
    user = User(username=username, email=email, pw_hash=pw_hash)
    db.session.add(user)
    db.session.commit()
    # Create wallet
    wallet = Wallet(user_id=user.user_id, currency=currency, balance=0)
    db.session.add(wallet)
    db.session.commit()
    return jsonify({'message': 'User registered', 'user_id': user.user_id}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Missing fields'}), 400
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.pw_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    # For simplicity, return user_id (in production, use JWT or session)
    return jsonify({'message': 'Login successful', 'user_id': user.user_id}), 200

if __name__ == '__main__':
    app.run(debug=True) 