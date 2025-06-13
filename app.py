from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, User, Wallet, Transaction
from decimal import Decimal
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/casino_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Change this in production!
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'profile_pics')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        currency = data.get('currency', 'USD')
        
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
            
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists.', 'danger')
            return render_template('register.html')
            
        pw_hash = generate_password_hash(password)
        user = User(username=username, email=email, pw_hash=pw_hash)
        db.session.add(user)
        db.session.commit()
        
        # Create wallet
        wallet = Wallet(user_id=user.user_id, currency=currency, balance=0)
        db.session.add(wallet)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            flash('All fields are required.', 'danger')
            return render_template('login.html')
            
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.pw_hash, password):
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')
            
        login_user(user)
        flash('Welcome back!', 'success')
        return redirect(url_for('index'))
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'profile_picture' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('profile'))
            
        file = request.files['profile_picture']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('profile'))
            
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{current_user.id}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Delete old profile picture if it exists and is not the default
            if current_user.profile_picture != 'default_profile.png':
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], current_user.profile_picture)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            
            file.save(filepath)
            current_user.profile_picture = filename
            db.session.commit()
            flash('Profile picture updated successfully!', 'success')
        else:
            flash('Invalid file type. Allowed types: png, jpg, jpeg, gif', 'danger')
            
    return render_template('profile.html', user=current_user)

@app.route('/wallet', methods=['GET', 'POST'])
@login_required
def wallet():
    if request.method == 'POST':
        action = request.form.get('action')
        amount = Decimal(request.form.get('amount', 0))
        
        if amount <= 0:
            flash('Amount must be greater than 0.', 'danger')
            return redirect(url_for('wallet'))
            
        wallet = current_user.wallets[0]
        
        if action == 'deposit':
            wallet.balance += amount
            transaction = Transaction(
                wallet_id=wallet.wallet_id,
                amount=amount,
                txn_type='deposit'
            )
            db.session.add(transaction)
            flash(f'Successfully deposited {amount:.2f} {wallet.currency}', 'success')
            
        elif action == 'withdraw':
            if amount > wallet.balance:
                flash('Insufficient funds.', 'danger')
                return redirect(url_for('wallet'))
                
            wallet.balance -= amount
            transaction = Transaction(
                wallet_id=wallet.wallet_id,
                amount=amount,
                txn_type='withdraw'
            )
            db.session.add(transaction)
            flash(f'Successfully withdrew {amount:.2f} {wallet.currency}', 'success')
            
        db.session.commit()
        return redirect(url_for('wallet'))
    
    # Get filter parameters
    txn_type = request.args.get('type', 'all')
    sort_by = request.args.get('sort', 'date')
    sort_order = request.args.get('order', 'desc')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Get wallet and transactions
    wallet = current_user.wallets[0]
    query = Transaction.query.filter_by(wallet_id=wallet.wallet_id)
    
    # Apply filters
    if txn_type != 'all':
        query = query.filter_by(txn_type=txn_type)
    if start_date:
        query = query.filter(Transaction.created_at >= start_date)
    if end_date:
        query = query.filter(Transaction.created_at <= end_date)
    
    # Apply sorting
    if sort_by == 'amount':
        if sort_order == 'asc':
            query = query.order_by(Transaction.amount.asc())
        else:
            query = query.order_by(Transaction.amount.desc())
    else:  # sort by date
        if sort_order == 'asc':
            query = query.order_by(Transaction.created_at.asc())
        else:
            query = query.order_by(Transaction.created_at.desc())
    
    transactions = query.all()
        
    return render_template('wallet.html', 
                         wallet=wallet,
                         transactions=transactions,
                         current_type=txn_type,
                         current_sort=sort_by,
                         current_order=sort_order,
                         start_date=start_date,
                         end_date=end_date)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 

import subprocess

# Check the Python interpreter path
python_path = subprocess.check_output("which python", shell=True).decode("utf-8").strip()
print(f"Python interpreter path: {python_path}")

# Check the pip path
pip_path = subprocess.check_output("which pip", shell=True).decode("utf-8").strip()
print(f"pip path: {pip_path}")