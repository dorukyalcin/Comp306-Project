from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, User, Wallet, Transaction, Game, Round, Bet, Outcome, Horse, HorseRunner, HorseResult
from decimal import Decimal
from werkzeug.utils import secure_filename
from games import HorseRacing, Slots, Plinko, Blackjack

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://casino:casino_pass@localhost:5432/casino_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Change this in production!
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'profile_pics')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

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
    
    wallet = current_user.get_primary_wallet()
    
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
    wallet = current_user.get_primary_wallet() if current_user.wallets else None
    if not wallet:
        flash('No wallet found. Please contact support.', 'danger')
        return redirect(url_for('index'))
    
    # Get game data
    horse_game = hr.get_game()
    active_round = hr.get_active_round()
    recent_rounds = hr.get_recent_rounds()
    
    # Get all horses for name lookup
    from models import Horse
    all_horses = Horse.query.all()
    horses_dict = {horse.horse_id: horse for horse in all_horses}
    
    return render_template('horse_racing.html', 
                         game=horse_game, 
                         wallet=wallet,
                         active_round=active_round,
                         recent_rounds=recent_rounds,
                         horses_dict=horses_dict)

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

@app.route('/slots')
@login_required
def slots():
    """Main slot machine game page"""
    slots_game = Slots()
    
    # Validate game setup
    validation = slots_game.validate_game_setup()
    if not validation['valid']:
        flash(validation['message'], 'danger')
        return redirect(url_for('index'))
    
    # Get user's primary wallet (any currency)
    wallet = current_user.get_primary_wallet() if current_user.wallets else None
    if not wallet:
        flash('No wallet found. Please contact support.', 'danger')
        return redirect(url_for('index'))
    
    # Get game data
    game = slots_game.get_game()
    active_round = slots_game.get_active_round()
    symbols = slots_game.get_all_symbols()
    
    return render_template('slots.html', 
                         game=game, 
                         wallet=wallet,
                         active_round=active_round,
                         symbols=symbols)

@app.route('/api/slots/bet', methods=['POST'])
@login_required
def slots_bet():
    """Handle slot machine bet"""
    try:
        data = request.get_json()
        bet_amount = Decimal(str(data.get('amount', 0)))
        
        if bet_amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid bet amount'})
        
        slots_game = Slots()
        result = slots_game.place_bet(current_user.user_id, bet_amount)
        
        if result['success']:
            # Update wallet balance in response - use primary wallet
            wallet = current_user.get_primary_wallet() if current_user.wallets else None
            if wallet:
                result['wallet_balance'] = float(wallet.balance)
                result['wallet_currency'] = wallet.currency
            else:
                result['wallet_balance'] = 0.0
                result['wallet_currency'] = 'USD'
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/plinko')
@login_required
def plinko():
    """Plinko game page"""
    try:
        from games.plinko import Plinko
        
        plinko_game = Plinko()
        
        # Get default board data (high risk)
        board_data = plinko_game.get_board_data('high')
        
        # Get user's primary wallet
        wallet = current_user.get_primary_wallet() if current_user.wallets else None
        if not wallet:
            flash('No wallet found. Please contact support.', 'error')
            return redirect(url_for('index'))
        
        return render_template('plinko.html', 
                             board_data=board_data, 
                             wallet=wallet)
        
    except Exception as e:
        flash(f'Error loading Plinko: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/plinko/bet', methods=['POST'])
@login_required 
def api_plinko_bet():
    """Place a Plinko bet"""
    try:
        from games.plinko import Plinko
        
        data = request.get_json()
        bet_amount = float(data.get('amount', 0))
        risk_level = data.get('risk_level', 'high')
        
        print(f"🎰 PLINKO BET: User {current_user.username} betting {bet_amount} at {risk_level} risk")
        
        if bet_amount <= 0:
            print(f"❌ Invalid bet amount: {bet_amount}")
            return jsonify({'success': False, 'message': 'Invalid bet amount'})
        
        # Check user's wallet balance before betting
        wallet = current_user.get_primary_wallet()
        if wallet:
            print(f"💰 Current wallet balance: {wallet.balance} {wallet.currency}")
        else:
            print("❌ No wallet found")
            return jsonify({'success': False, 'message': 'No wallet found'})
        
        plinko = Plinko()
        result = plinko.place_bet(current_user.user_id, bet_amount, risk_level)
        
        print(f"🎲 Bet result: {result}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error in Plinko bet: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/plinko/board-data')
@login_required
def api_plinko_board_data():
    """Get board data for a specific risk level"""
    try:
        from games.plinko import Plinko
        
        risk_level = request.args.get('risk', 'high')
        plinko = Plinko()
        board_data = plinko.get_board_data(risk_level)
        
        return jsonify({
            'success': True,
            'board_data': board_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/blackjack')
@login_required
def blackjack():
    """Blackjack game page"""
    try:
        from games.blackjack import Blackjack
        
        blackjack_game = Blackjack()
        
        # Get user's primary wallet
        wallet = current_user.get_primary_wallet() if current_user.wallets else None
        if not wallet:
            flash('No wallet found. Please contact support.', 'error')
            return redirect(url_for('index'))
        
        # Get game statistics
        statistics = blackjack_game.get_statistics()
        
        return render_template('blackjack.html', 
                             wallet=wallet,
                             statistics=statistics)
        
    except Exception as e:
        flash(f'Error loading Blackjack: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/blackjack/bet', methods=['POST'])
@login_required 
def api_blackjack_bet():
    """Place a Blackjack bet and deal initial cards"""
    try:
        from games.blackjack import Blackjack
        
        data = request.get_json()
        bet_amount = float(data.get('amount', 0))
        
        if bet_amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid bet amount'})
        
        blackjack = Blackjack()
        result = blackjack.place_bet(current_user.user_id, bet_amount)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/blackjack/action', methods=['POST'])
@login_required
def api_blackjack_action():
    """Handle player action (hit, stand, double)"""
    try:
        from games.blackjack import Blackjack
        
        data = request.get_json()
        bet_id = data.get('bet_id')
        action = data.get('action')
        
        if not bet_id or not action:
            return jsonify({'success': False, 'message': 'Missing bet_id or action'})
        
        blackjack = Blackjack()
        result = blackjack.player_action(bet_id, action)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# Admin Routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard showing all users and their balances"""
    try:
        # Get all users with their wallets
        users = User.query.all()
        
        # Prepare user data with wallet information
        user_data = []
        for user in users:
            user_info = {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'created_at': user.created_at,
                'wallets': []
            }
            
            # Get all wallets for this user
            for wallet in user.wallets:
                wallet_info = {
                    'wallet_id': wallet.wallet_id,
                    'currency': wallet.currency,
                    'balance': float(wallet.balance)
                }
                user_info['wallets'].append(wallet_info)
            
            user_data.append(user_info)
        
        return render_template('admin/dashboard.html', users=user_data)
    
    except Exception as e:
        flash(f'Error loading admin dashboard: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/admin/user/<int:user_id>')
@login_required
@admin_required
def admin_user_detail(user_id):
    """View detailed information about a specific user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Get user's transactions
        transactions = []
        for wallet in user.wallets:
            wallet_transactions = Transaction.query.filter_by(wallet_id=wallet.wallet_id).order_by(Transaction.created_at.desc()).limit(50).all()
            for transaction in wallet_transactions:
                transactions.append({
                    'transaction_id': transaction.transaction_id,
                    'wallet_id': transaction.wallet_id,
                    'currency': wallet.currency,
                    'amount': float(transaction.amount),
                    'txn_type': transaction.txn_type,
                    'created_at': transaction.created_at
                })
        
        # Sort transactions by date (most recent first)
        transactions.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Get user's bets
        bets = Bet.query.filter_by(user_id=user_id).order_by(Bet.created_at.desc()).limit(20).all()
        
        return render_template('admin/user_detail.html', 
                             user=user, 
                             transactions=transactions[:50],  # Limit to 50 most recent
                             bets=bets)
    
    except Exception as e:
        flash(f'Error loading user details: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/<int:user_id>/balance', methods=['POST'])
@login_required
@admin_required
def admin_modify_balance(user_id):
    """Modify user's wallet balance"""
    try:
        user = User.query.get_or_404(user_id)
        
        wallet_id = request.form.get('wallet_id')
        action = request.form.get('action')  # 'add' or 'subtract'
        amount_str = request.form.get('amount', '0')
        reason = request.form.get('reason', 'Admin adjustment')
        
        # Validate inputs
        try:
            amount = Decimal(amount_str)
        except (ValueError, TypeError):
            flash('Invalid amount format.', 'danger')
            return redirect(url_for('admin_user_detail', user_id=user_id))
        
        if amount <= 0:
            flash('Amount must be greater than 0.', 'danger')
            return redirect(url_for('admin_user_detail', user_id=user_id))
        
        # Get the wallet
        wallet = Wallet.query.filter_by(wallet_id=wallet_id, user_id=user_id).first()
        if not wallet:
            flash('Wallet not found.', 'danger')
            return redirect(url_for('admin_user_detail', user_id=user_id))
        
        # Modify balance
        old_balance = wallet.balance
        if action == 'add':
            wallet.balance += amount
            txn_type = 'admin_credit'
            flash_message = f'Added {amount:.2f} {wallet.currency} to {user.username}\'s wallet'
        elif action == 'subtract':
            if amount > wallet.balance:
                flash('Cannot subtract more than current balance.', 'danger')
                return redirect(url_for('admin_user_detail', user_id=user_id))
            wallet.balance -= amount
            txn_type = 'admin_debit'
            flash_message = f'Subtracted {amount:.2f} {wallet.currency} from {user.username}\'s wallet'
        else:
            flash('Invalid action.', 'danger')
            return redirect(url_for('admin_user_detail', user_id=user_id))
        
        # Create transaction record
        transaction = Transaction(
            wallet_id=wallet.wallet_id,
            amount=amount,
            txn_type=txn_type
        )
        db.session.add(transaction)
        
        # Commit changes
        db.session.commit()
        
        flash(f'{flash_message}. Balance changed from {old_balance:.2f} to {wallet.balance:.2f}. Reason: {reason}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error modifying balance: {str(e)}', 'danger')
    
    return redirect(url_for('admin_user_detail', user_id=user_id))

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    """Delete a user and all associated data"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Safety checks
        if user.user_id == current_user.user_id:
            flash('You cannot delete your own account.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        if user.is_admin and User.query.filter_by(is_admin=True).count() <= 1:
            flash('Cannot delete the last admin user.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        username = user.username  # Store for flash message
        
        # Delete user and cascade delete related data
        # Note: The foreign key relationships should handle cascade deletion
        # But let's be explicit about what we're deleting
        
        # Delete user's bets (this will also delete outcomes due to cascade)
        Bet.query.filter_by(user_id=user_id).delete()
        
        # Delete user's transactions (via wallets)
        for wallet in user.wallets:
            Transaction.query.filter_by(wallet_id=wallet.wallet_id).delete()
        
        # Delete user's wallets
        Wallet.query.filter_by(user_id=user_id).delete()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User "{username}" and all associated data have been permanently deleted.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001) 

import subprocess

# Check the Python interpreter path
python_path = subprocess.check_output("which python", shell=True).decode("utf-8").strip()
print(f"Python interpreter path: {python_path}")

# Check the pip path
pip_path = subprocess.check_output("which pip", shell=True).decode("utf-8").strip()
print(f"pip path: {pip_path}")