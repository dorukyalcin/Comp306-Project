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
from sqlalchemy.sql import text
from sqlalchemy.orm import joinedload

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

@app.route('/api/wallet/<int:wallet_id>/balance')
@login_required
def get_wallet_balance(wallet_id):
    """API endpoint to get current wallet balance"""
    try:
        # Get the wallet
        wallet = Wallet.query.filter_by(wallet_id=wallet_id, user_id=current_user.user_id).first()
        if not wallet:
            return jsonify({'success': False, 'error': 'Wallet not found'}), 404
        
        return jsonify({
            'success': True,
            'balance': float(wallet.balance),
            'currency': wallet.currency,
            'wallet_id': wallet.wallet_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
@app.route('/wallet/<int:wallet_id>', methods=['GET', 'POST'])
@login_required
def wallet(wallet_id=None):
    # Check if user has a wallet
    if not current_user.wallets:
        flash('No wallet found. Please contact support to create a wallet.', 'danger')
        return redirect(url_for('index'))
    
    # Get the specific wallet or default to primary wallet
    if wallet_id:
        wallet = Wallet.query.filter_by(wallet_id=wallet_id, user_id=current_user.user_id).first()
        if not wallet:
            flash('Wallet not found.', 'danger')
            return redirect(url_for('wallet'))
    else:
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
                return redirect(url_for('wallet', wallet_id=wallet.wallet_id))
            
            if amount <= 0:
                flash('Amount must be greater than 0.', 'danger')
                return redirect(url_for('wallet', wallet_id=wallet.wallet_id))
            
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
                    return redirect(url_for('wallet', wallet_id=wallet.wallet_id))
                    
                wallet.balance -= amount
                transaction = Transaction(
                    wallet_id=wallet.wallet_id,
                    amount=amount,
                    txn_type='withdraw'
                )
                db.session.add(transaction)
                flash(f'Successfully withdrew {amount:.2f} {wallet.currency}', 'success')
                
            elif action == 'donate':
                if amount > wallet.balance:
                    flash('Insufficient funds for donation.', 'danger')
                    return redirect(url_for('wallet', wallet_id=wallet.wallet_id))
                    
                wallet.balance -= amount
                transaction = Transaction(
                    wallet_id=wallet.wallet_id,
                    amount=amount,
                    txn_type='donate'
                )
                db.session.add(transaction)
                flash(f'Successfully donated {amount:.2f} {wallet.currency} to the casino. Thank you for your generosity!', 'success')
            else:
                flash('Invalid action.', 'danger')
                return redirect(url_for('wallet', wallet_id=wallet.wallet_id))
                
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            flash(f'Transaction failed: {str(e)}', 'danger')
            
        return redirect(url_for('wallet', wallet_id=wallet.wallet_id))
    
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
                             all_wallets=current_user.wallets,
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
@app.route('/horse-racing/<int:wallet_id>')
@login_required
def horse_racing(wallet_id=None):
    """Main horse racing game page"""
    hr = HorseRacing()
    
    # Validate game setup
    validation = hr.validate_game_setup()
    if not validation['valid']:
        flash(validation['message'], 'danger')
        return redirect(url_for('index'))
    
    # Get the specific wallet or default to primary wallet
    if wallet_id:
        wallet = Wallet.query.filter_by(wallet_id=wallet_id, user_id=current_user.user_id).first()
        if not wallet:
            flash('Wallet not found.', 'danger')
            return redirect(url_for('horse_racing'))
    else:
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
                         all_wallets=current_user.wallets,
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
    wallet_id = data.get('wallet_id')
    
    # Get the specified wallet or default to primary wallet
    if wallet_id:
        wallet = Wallet.query.filter_by(wallet_id=wallet_id, user_id=current_user.user_id).first()
        if not wallet:
            return jsonify({'success': False, 'message': 'Wallet not found'})
    else:
        wallet = current_user.get_primary_wallet()
        if not wallet:
            return jsonify({'success': False, 'message': 'No wallet found'})
    
    hr = HorseRacing()
    result = hr.place_bet(current_user.user_id, horse_id, bet_amount, bet_type, wallet_id=wallet.wallet_id)
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
@app.route('/slots/<int:wallet_id>')
@login_required
def slots(wallet_id=None):
    """Main slot machine game page"""
    slots_game = Slots()
    
    # Validate game setup
    validation = slots_game.validate_game_setup()
    if not validation['valid']:
        flash(validation['message'], 'danger')
        return redirect(url_for('index'))
    
    # Get the specific wallet or default to primary wallet
    if wallet_id:
        wallet = Wallet.query.filter_by(wallet_id=wallet_id, user_id=current_user.user_id).first()
        if not wallet:
            flash('Wallet not found.', 'danger')
            return redirect(url_for('slots'))
    else:
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
                         all_wallets=current_user.wallets,
                         active_round=active_round,
                         symbols=symbols)

@app.route('/api/slots/bet', methods=['POST'])
@login_required
def slots_bet():
    """Handle slot machine bet"""
    try:
        data = request.get_json()
        bet_amount = Decimal(str(data.get('amount', 0)))
        wallet_id = data.get('wallet_id')
        
        if bet_amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid bet amount'})
        
        # Get the specified wallet or default to primary wallet
        if wallet_id:
            wallet = Wallet.query.filter_by(wallet_id=wallet_id, user_id=current_user.user_id).first()
            if not wallet:
                return jsonify({'success': False, 'message': 'Wallet not found'})
        else:
            wallet = current_user.get_primary_wallet() if current_user.wallets else None
            if not wallet:
                return jsonify({'success': False, 'message': 'No wallet found'})
        
        slots_game = Slots()
        result = slots_game.place_bet(current_user.user_id, bet_amount, wallet_id=wallet.wallet_id)
        
        if result['success']:
            # Update wallet balance in response - use the specific wallet
            result['wallet_balance'] = float(wallet.balance)
            result['wallet_currency'] = wallet.currency
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/plinko')
@app.route('/plinko/<int:wallet_id>')
@login_required
def plinko(wallet_id=None):
    """Plinko game page"""
    try:
        from games.plinko import Plinko
        
        plinko_game = Plinko()
        
        # Get default board data (high risk)
        board_data = plinko_game.get_board_data('high')
        
        # Get the specific wallet or default to primary wallet
        if wallet_id:
            wallet = Wallet.query.filter_by(wallet_id=wallet_id, user_id=current_user.user_id).first()
            if not wallet:
                flash('Wallet not found.', 'danger')
                return redirect(url_for('plinko'))
        else:
            wallet = current_user.get_primary_wallet() if current_user.wallets else None
        
        if not wallet:
            flash('No wallet found. Please contact support.', 'error')
            return redirect(url_for('index'))
        
        return render_template('plinko.html', 
                             board_data=board_data, 
                             wallet=wallet,
                             all_wallets=current_user.wallets)
        
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
        wallet_id = data.get('wallet_id')
        
        print(f"🎰 PLINKO BET: User {current_user.username} betting {bet_amount} at {risk_level} risk")
        
        if bet_amount <= 0:
            print(f"❌ Invalid bet amount: {bet_amount}")
            return jsonify({'success': False, 'message': 'Invalid bet amount'})
        
        # Get the specified wallet or default to primary wallet
        if wallet_id:
            wallet = Wallet.query.filter_by(wallet_id=wallet_id, user_id=current_user.user_id).first()
            if not wallet:
                print("❌ Specified wallet not found")
                return jsonify({'success': False, 'message': 'Wallet not found'})
        else:
            wallet = current_user.get_primary_wallet()
            if not wallet:
                print("❌ No wallet found")
                return jsonify({'success': False, 'message': 'No wallet found'})
        
        print(f"💰 Current wallet balance: {wallet.balance} {wallet.currency}")
        
        plinko = Plinko()
        result = plinko.place_bet(current_user.user_id, bet_amount, risk_level, wallet_id=wallet.wallet_id)
        
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
@app.route('/blackjack/<int:wallet_id>')
@login_required
def blackjack(wallet_id=None):
    """Blackjack game page"""
    try:
        from games.blackjack import Blackjack
        
        blackjack_game = Blackjack()
        
        # Get the specific wallet or default to primary wallet
        if wallet_id:
            wallet = Wallet.query.filter_by(wallet_id=wallet_id, user_id=current_user.user_id).first()
            if not wallet:
                flash('Wallet not found.', 'danger')
                return redirect(url_for('blackjack'))
        else:
            wallet = current_user.get_primary_wallet() if current_user.wallets else None
        
        if not wallet:
            flash('No wallet found. Please contact support.', 'error')
            return redirect(url_for('index'))
        
        # Get game statistics
        statistics = blackjack_game.get_statistics()
        
        return render_template('blackjack.html', 
                             wallet=wallet,
                             all_wallets=current_user.wallets,
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
        wallet_id = data.get('wallet_id')
        
        if bet_amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid bet amount'})
        
        # Get the specified wallet or default to primary wallet
        if wallet_id:
            wallet = Wallet.query.filter_by(wallet_id=wallet_id, user_id=current_user.user_id).first()
            if not wallet:
                return jsonify({'success': False, 'message': 'Wallet not found'})
        else:
            wallet = current_user.get_primary_wallet()
            if not wallet:
                return jsonify({'success': False, 'message': 'No wallet found'})
        
        blackjack = Blackjack()
        result = blackjack.place_bet(current_user.user_id, bet_amount, wallet_id=wallet.wallet_id)
        
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
                    'transaction_id': transaction.txn_id,  # Fixed: use txn_id not transaction_id
                    'wallet_id': transaction.wallet_id,
                    'currency': wallet.currency,
                    'amount': float(transaction.amount),
                    'txn_type': transaction.txn_type,
                    'created_at': transaction.created_at
                })
        
        # Sort transactions by date (most recent first)
        transactions.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Get user's bets with related data to avoid lazy loading
        bets = Bet.query.filter_by(user_id=user_id)\
                        .options(joinedload(Bet.round).joinedload(Round.game),
                                joinedload(Bet.outcome))\
                        .order_by(Bet.placed_at.desc()).limit(20).all()
        
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

@app.route('/admin/analytics')
@login_required
@admin_required
def admin_analytics():
    """Execute complex SQL queries for database course requirements"""
    analytics_results = {
        'user_performance': [],
        'game_revenue': [],
        'horse_racing': [],
        'transaction_patterns': [],
        'betting_behavior': []
    }
    
    # Query 1: User Performance Analytics
    try:
        user_perf_sql = """
        WITH user_betting_stats AS (
            SELECT 
                u.user_id, u.username, u.created_at,
                COUNT(DISTINCT b.bet_id) as total_bets,
                COALESCE(SUM(b.amount), 0) as total_wagered,
                COALESCE(SUM(b.payout_amount), 0) as total_winnings,
                COALESCE(SUM(b.payout_amount), 0) - COALESCE(SUM(b.amount), 0) as net_profit,
                COUNT(CASE WHEN COALESCE(b.payout_amount, 0) > COALESCE(b.amount, 0) THEN 1 END) as winning_bets,
                COALESCE(AVG(b.amount), 0) as avg_bet_size,
                COUNT(DISTINCT g.code) as games_played
            FROM users u
            LEFT JOIN bets b ON u.user_id = b.user_id
            LEFT JOIN rounds r ON b.round_id = r.round_id  
            LEFT JOIN games g ON r.game_id = g.game_id
            WHERE u.is_admin = FALSE
            GROUP BY u.user_id, u.username, u.created_at
            HAVING COUNT(b.bet_id) > 0
        ),
        user_rankings AS (
            SELECT *,
                CASE 
                    WHEN total_bets > 0 THEN ROUND((winning_bets::NUMERIC / total_bets) * 100, 2)
                    ELSE 0 
                END as win_percentage,
                CASE 
                    WHEN total_wagered > 0 THEN ROUND((net_profit / total_wagered) * 100, 2)
                    ELSE 0 
                END as roi_percentage,
                RANK() OVER (ORDER BY net_profit DESC) as profit_rank,
                CASE 
                    WHEN avg_bet_size > 100 THEN 'High Roller'
                    WHEN avg_bet_size > 50 THEN 'Medium Risk'
                    WHEN avg_bet_size > 10 THEN 'Conservative'
                    ELSE 'Penny Player'
                END as risk_profile
            FROM user_betting_stats
        )
        SELECT username, total_bets, total_wagered, net_profit, 
               win_percentage, roi_percentage, profit_rank, risk_profile
        FROM user_rankings
        ORDER BY net_profit DESC
        LIMIT 10;
        """
        
        result = db.session.execute(text(user_perf_sql))
        analytics_results['user_performance'] = [dict(row._mapping) for row in result]
        db.session.commit()
        print("Query 1 executed successfully")
    except Exception as e:
        print(f"Error in Query 1: {str(e)}")
        db.session.rollback()
        analytics_results['user_performance'] = []

    # Query 2: Game Revenue Analysis  
    try:
        game_revenue_sql = """
        WITH game_stats AS (
            SELECT 
                g.code, g.house_edge,
                COUNT(DISTINCT r.round_id) as total_rounds,
                COUNT(DISTINCT b.user_id) as unique_players,
                COUNT(b.bet_id) as total_bets,
                COALESCE(SUM(b.amount), 0) as total_wagered,
                COALESCE(SUM(b.payout_amount), 0) as total_paid_out,
                COALESCE(SUM(b.amount), 0) - COALESCE(SUM(b.payout_amount), 0) as house_profit
            FROM games g
            LEFT JOIN rounds r ON g.game_id = r.game_id
            LEFT JOIN bets b ON r.round_id = b.round_id
            WHERE g.is_active = TRUE
            GROUP BY g.code, g.house_edge
        )
        SELECT code, COALESCE(house_edge * 100, 0) as theoretical_house_edge_pct,
               total_rounds, unique_players, total_bets,
               ROUND(COALESCE(total_wagered, 0), 2) as total_wagered,
               ROUND(COALESCE(house_profit, 0), 2) as house_profit,
               CASE 
                   WHEN COALESCE(total_wagered, 0) > 0 
                   THEN ROUND((COALESCE(house_profit, 0) / COALESCE(total_wagered, 1)) * 100, 3)
                   ELSE 0 
               END as actual_house_edge_pct
        FROM game_stats
        WHERE total_bets > 0
        ORDER BY COALESCE(house_profit, 0) DESC;
        """
        
        result = db.session.execute(text(game_revenue_sql))
        analytics_results['game_revenue'] = [dict(row._mapping) for row in result]
        db.session.commit()
        print("Query 2 executed successfully")
    except Exception as e:
        print(f"Error in Query 2: {str(e)}")
        db.session.rollback()
        analytics_results['game_revenue'] = []

    # Query 3: Horse Racing Analytics
    try:
        horse_racing_sql = """
        SELECT 
            h.name,
            h.age,
            h.temperament,
            COUNT(hr.round_id) as races_run,
            COUNT(CASE WHEN hr.finish_place = 1 THEN 1 END) as wins,
            COUNT(CASE WHEN hr.finish_place <= 3 THEN 1 END) as top3_finishes,
            ROUND(AVG(hr.finish_place)::NUMERIC, 2) as avg_finish_position,
            ROUND(MIN(hr.race_time_sec)::NUMERIC, 2) as best_time,
            ROUND(AVG(hr.race_time_sec)::NUMERIC, 2) as avg_time,
            CASE 
                WHEN COUNT(hr.round_id) > 0 THEN 
                    ROUND((COUNT(CASE WHEN hr.finish_place = 1 THEN 1 END)::NUMERIC / COUNT(hr.round_id) * 100), 1)
                ELSE 0 
            END as win_percentage,
            CASE 
                WHEN COUNT(hr.round_id) > 0 THEN 
                    ROUND((COUNT(CASE WHEN hr.finish_place <= 3 THEN 1 END)::NUMERIC / COUNT(hr.round_id) * 100), 1)
                ELSE 0 
            END as top3_percentage
        FROM horses h
        LEFT JOIN horse_results hr ON h.horse_id = hr.horse_id
        GROUP BY h.horse_id, h.name, h.age, h.temperament
        HAVING COUNT(hr.round_id) > 0
        ORDER BY COUNT(CASE WHEN hr.finish_place = 1 THEN 1 END) DESC, AVG(hr.finish_place) ASC;
        """
        
        result = db.session.execute(text(horse_racing_sql))
        analytics_results['horse_racing'] = [dict(row._mapping) for row in result]
        db.session.commit()
        print("Query 3 executed successfully")
    except Exception as e:
        print(f"Error in Query 3: {str(e)}")
        db.session.rollback()
        analytics_results['horse_racing'] = []

    # Query 4: Transaction Pattern Analysis
    try:
        transaction_sql = """
        WITH user_transaction_summary AS (
            SELECT 
                u.user_id,
                u.username,
                u.created_at as user_since,
                w.currency,
                w.balance as current_balance,
                COUNT(t.txn_id) as total_transactions,
                SUM(CASE WHEN t.txn_type IN ('deposit', 'admin_credit') THEN t.amount ELSE 0 END) as total_deposits,
                SUM(CASE WHEN t.txn_type IN ('withdraw', 'admin_debit') THEN t.amount ELSE 0 END) as total_withdrawals,
                SUM(CASE WHEN t.txn_type = 'bet_loss' THEN t.amount ELSE 0 END) as total_bet_losses,
                SUM(CASE WHEN t.txn_type = 'bet_win' THEN t.amount ELSE 0 END) as total_bet_wins,
                MIN(t.created_at) as first_transaction,
                MAX(t.created_at) as last_transaction,
                COUNT(DISTINCT DATE(t.created_at)) as active_transaction_days
            FROM users u
            JOIN wallets w ON u.user_id = w.user_id
            LEFT JOIN transactions t ON w.wallet_id = t.wallet_id
            WHERE u.is_admin = FALSE
            GROUP BY u.user_id, u.username, u.created_at, w.currency, w.balance
            HAVING COUNT(t.txn_id) > 0
        ),
        user_financial_metrics AS (
            SELECT *,
                EXTRACT(DAYS FROM (COALESCE(last_transaction, NOW()) - user_since)) + 1 as days_since_signup,
                EXTRACT(DAYS FROM (last_transaction - first_transaction)) + 1 as transaction_span_days,
                total_deposits - total_withdrawals as net_deposits,
                total_bet_wins - total_bet_losses as net_betting_result,
                CASE 
                    WHEN total_deposits > 0 
                    THEN ROUND((total_withdrawals / total_deposits) * 100, 2)
                    ELSE 0 
                END as withdrawal_ratio_pct,
                CASE 
                    WHEN active_transaction_days > 0 
                    THEN ROUND(total_transactions::NUMERIC / active_transaction_days, 2)
                    ELSE 0 
                END as avg_transactions_per_day,
                CASE 
                    WHEN total_deposits > 0 
                    THEN ROUND(((total_bet_losses + total_bet_wins) / total_deposits) * 100, 2)
                    ELSE 0 
                END as betting_intensity_pct
            FROM user_transaction_summary
        ),
        financial_health_scoring AS (
            SELECT *,
                CASE 
                    WHEN net_deposits > 0 AND withdrawal_ratio_pct < 50 THEN 'Healthy Depositor'
                    WHEN net_deposits > 0 AND withdrawal_ratio_pct < 80 THEN 'Balanced Player'  
                    WHEN net_deposits <= 0 AND current_balance > 0 THEN 'Profitable Player'
                    WHEN current_balance <= 0 THEN 'Depleted Account'
                    ELSE 'High Withdrawal Risk'
                END as financial_health_status,
                RANK() OVER (ORDER BY total_deposits DESC) as deposit_volume_rank,
                RANK() OVER (ORDER BY betting_intensity_pct DESC) as betting_activity_rank
            FROM user_financial_metrics
        )
        SELECT 
            username,
            currency,
            ROUND(current_balance, 2) as balance,
            total_transactions,
            ROUND(total_deposits, 2) as deposits,
            ROUND(total_withdrawals, 2) as withdrawals,
            ROUND(net_deposits, 2) as net_deposits,
            withdrawal_ratio_pct,
            betting_intensity_pct,
            avg_transactions_per_day,
            transaction_span_days,
            financial_health_status,
            deposit_volume_rank
        FROM financial_health_scoring
        WHERE total_deposits > 0
        ORDER BY total_deposits DESC
        LIMIT 15;
        """
        
        result = db.session.execute(text(transaction_sql))
        analytics_results['transaction_patterns'] = [dict(row._mapping) for row in result]
        db.session.commit()
        print("Query 4 executed successfully")
    except Exception as e:
        print(f"Error in Query 4: {str(e)}")
        db.session.rollback()
        analytics_results['transaction_patterns'] = []

    # Query 5: Betting Behavior Cohort Analysis
    try:
        cohort_sql = """
        WITH user_cohorts AS (
            SELECT 
                user_id,
                username,
                DATE_TRUNC('month', created_at) as cohort_month,
                created_at
            FROM users 
            WHERE is_admin = FALSE
        ),
        user_first_bet AS (
            SELECT 
                b.user_id,
                MIN(DATE(b.placed_at)) as first_bet_date,
                DATE_TRUNC('month', MIN(b.placed_at)) as first_bet_month
            FROM bets b
            GROUP BY b.user_id
        ),
        user_betting_journey AS (
            SELECT 
                uc.user_id,
                uc.username,
                uc.cohort_month,
                ufb.first_bet_date,
                ufb.first_bet_month,
                (ufb.first_bet_date - uc.created_at::DATE) as days_to_first_bet,
                COUNT(b.bet_id) as total_bets,
                COUNT(DISTINCT DATE(b.placed_at)) as betting_days,
                COUNT(DISTINCT r.game_id) as games_tried,
                SUM(b.amount) as total_wagered,
                AVG(b.amount) as avg_bet_size,
                STDDEV(b.amount) as bet_size_variance,
                MIN(b.placed_at) as betting_start,
                MAX(b.placed_at) as last_bet_date,
                (DATE(MAX(b.placed_at)) - DATE(MIN(b.placed_at))) + 1 as betting_lifespan_days
            FROM user_cohorts uc
            LEFT JOIN user_first_bet ufb ON uc.user_id = ufb.user_id
            LEFT JOIN bets b ON uc.user_id = b.user_id
            LEFT JOIN rounds r ON b.round_id = r.round_id
            GROUP BY uc.user_id, uc.username, uc.cohort_month, uc.created_at, ufb.first_bet_date, ufb.first_bet_month
            HAVING COUNT(b.bet_id) > 0
        ),
        user_behavior_segments AS (
            SELECT 
                user_id,
                username,
                cohort_month,
                first_bet_date,
                first_bet_month,
                days_to_first_bet,
                total_bets,
                betting_days,
                games_tried,
                total_wagered,
                avg_bet_size,
                bet_size_variance,
                betting_start,
                last_bet_date,
                betting_lifespan_days,
                CASE 
                    WHEN total_bets >= 50 AND betting_lifespan_days >= 60 THEN 'High Value Regular'
                    WHEN total_bets >= 20 AND betting_lifespan_days >= 30 THEN 'Active Player'
                    WHEN total_bets >= 10 THEN 'Casual Player'
                    WHEN total_bets >= 5 THEN 'Trial User'
                    ELSE 'One-time Player'
                END as player_segment,
                CASE 
                    WHEN avg_bet_size >= 100 THEN 'High Roller'
                    WHEN avg_bet_size >= 50 THEN 'Medium Stake'
                    WHEN avg_bet_size >= 20 THEN 'Regular Stake'
                    ELSE 'Low Stake'
                END as stake_category,
                CASE 
                    WHEN betting_days > 0 
                    THEN ROUND(total_bets::NUMERIC / betting_days, 2)
                    ELSE 0 
                END as bets_per_active_day
            FROM user_betting_journey
        )
        SELECT 
            username,
            cohort_month,
            days_to_first_bet,
            total_bets,
            betting_days,
            games_tried,
            ROUND(total_wagered, 2) as total_wagered,
            ROUND(avg_bet_size, 2) as avg_bet_size,
            betting_lifespan_days,
            bets_per_active_day,
            player_segment,
            stake_category,
            RANK() OVER (ORDER BY total_wagered DESC) as value_rank
        FROM user_behavior_segments
        ORDER BY total_wagered DESC
        LIMIT 15;
        """
        
        result = db.session.execute(text(cohort_sql))
        analytics_results['betting_behavior'] = [dict(row._mapping) for row in result]
        db.session.commit()
        print("Query 5 executed successfully")
    except Exception as e:
        print(f"Error in Query 5: {str(e)}")
        db.session.rollback()
        analytics_results['betting_behavior'] = []

    return render_template('admin/analytics.html', analytics=analytics_results)

# Debug route for horse racing query
@app.route('/admin/debug/horse-racing')
@login_required
@admin_required
def debug_horse_racing():
    try:
        # Basic query to check horse data
        basic_query = """
        SELECT h.horse_id, h.name, COUNT(hr.round_id) as races
        FROM horses h
        LEFT JOIN horse_results hr ON h.horse_id = hr.horse_id
        GROUP BY h.horse_id, h.name
        ORDER BY h.horse_id;
        """
        result = db.session.execute(text(basic_query))
        horses = [dict(row._mapping) for row in result]
        
        # Check bet data
        bet_query = """
        SELECT b.bet_id, b.choice_data, b.amount, b.payout_amount
        FROM bets b
        WHERE b.choice_data->>'horse_id' IS NOT NULL
        LIMIT 5;
        """
        result = db.session.execute(text(bet_query))
        bets = [dict(row._mapping) for row in result]
        
        return jsonify({
            'horses': horses,
            'bets': bets,
            'message': 'Debug data retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

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