from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, User, Wallet, Transaction, Game, Round, Bet, Outcome, Horse, HorseRunner, HorseResult
from decimal import Decimal
from werkzeug.utils import secure_filename
from games import HorseRacing

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
    # Check if user has a wallet
    if not current_user.wallets:
        flash('No wallet found. Please contact support to create a wallet.', 'danger')
        return redirect(url_for('index'))
    
    wallet = current_user.wallets[0]
    
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            amount_str = request.form.get('amount', '0')
            
            # Validate amount input
            try:
                amount = Decimal(amount_str)
            except (ValueError, TypeError):
                flash('Invalid amount format. Please enter a valid number.', 'danger')
                return redirect(url_for('wallet'))
            
            if amount <= 0:
                flash('Amount must be greater than 0.', 'danger')
                return redirect(url_for('wallet'))
            
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
            else:
                flash('Invalid action.', 'danger')
                return redirect(url_for('wallet'))
                
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            flash(f'Transaction failed: {str(e)}', 'danger')
            
        return redirect(url_for('wallet'))
    
    # GET request - display wallet page
    try:
        # Get filter parameters
        txn_type = request.args.get('type', 'all')
        sort_by = request.args.get('sort', 'date')
        sort_order = request.args.get('order', 'desc')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Get transactions
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
                             
    except Exception as e:
        flash(f'Error loading wallet: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/horse-racing')
@login_required
def horse_racing():
    """Main horse racing game page"""
    hr = HorseRacing()
    
    # Validate game setup
    validation = hr.validate_game_setup()
    if not validation['valid']:
        flash(validation['message'], 'danger')
        return redirect(url_for('index'))
    
    # Get user's wallet
    wallet = current_user.wallets[0] if current_user.wallets else None
    if not wallet:
        flash('No wallet found. Please contact support.', 'danger')
        return redirect(url_for('index'))
    
    # Get game data
    horse_game = hr.get_game()
    active_round = hr.get_active_round()
    recent_rounds = hr.get_recent_rounds()
    
    return render_template('horse_racing.html', 
                         game=horse_game, 
                         wallet=wallet,
                         active_round=active_round,
                         recent_rounds=recent_rounds)

@app.route('/horse-racing/start-race', methods=['POST'])
@login_required
def start_horse_race():
    """Start a new horse race round"""
    hr = HorseRacing()
    result = hr.start_new_race()
    return jsonify(result)

@app.route('/horse-racing/place-bet', methods=['POST'])
@login_required
def place_horse_bet():
    """Place a bet on a horse"""
    data = request.get_json()
    
    horse_id = data.get('horse_id')
    bet_amount = Decimal(str(data.get('amount', 0)))
    bet_type = data.get('bet_type', 'win')
    
    hr = HorseRacing()
    result = hr.place_bet(current_user.user_id, horse_id, bet_amount, bet_type)
    return jsonify(result)

@app.route('/horse-racing/run-race', methods=['POST'])
@login_required
def run_horse_race():
    """Execute the horse race and determine winner"""
    hr = HorseRacing()
    result = hr.run_race()
    return jsonify(result)

@app.route('/horse-racing/race-status')
@login_required
def horse_race_status():
    """Get current race status"""
    hr = HorseRacing()
    result = hr.get_race_status(current_user.user_id)
    return jsonify(result)

@app.route('/horse-racing/betting-stats')
@login_required
def horse_betting_stats():
    """Get betting statistics for current race"""
    hr = HorseRacing()
    result = hr.get_betting_stats()
    return jsonify(result)

@app.route('/horse-racing/horse-info')
@login_required
def horse_info():
    """Get horse information"""
    hr = HorseRacing()
    result = hr.get_horse_info()
    return jsonify(result)

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