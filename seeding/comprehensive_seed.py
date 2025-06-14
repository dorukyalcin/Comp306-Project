import sys
import os
sys.path.insert(0, '/app')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, UserSettings, Wallet, Transaction, Game, Round, Outcome, Bet, SarcasTemp
from werkzeug.security import generate_password_hash
from decimal import Decimal
import random
from datetime import datetime, timedelta
import json

def comprehensive_seed():
    """
    Comprehensive database seeding script that populates:
    1. Users & Authentication (sample accounts)
    2. Financial Data (wallets, balances, transactions)
    3. Gaming Data (rounds, bets, outcomes)
    4. Sarcasm System (templates, user settings)
    """
    
    with app.app_context():
        print("🌱 Starting comprehensive database seeding...")
        
        # Check if data already exists to avoid duplicates
        if User.query.count() > 0:
            print("⚠️  Database already contains users. Skipping seeding to avoid duplicates.")
            print("💡 Run 'python seeding/reset_db.py' first if you want to reseed from scratch.")
            return
        
        # 1. SEED SARCASTIC TEMPLATES FIRST (needed for user settings)
        seed_sarcastic_templates()
        
        # 2. SEED USERS & AUTHENTICATION
        users = seed_users_and_authentication()
        
        # 3. SEED FINANCIAL DATA (wallets and transactions)
        wallets = seed_financial_data(users)
        
        # 4. SEED GAMING DATA (rounds, outcomes, bets)
        seed_gaming_data(users)
        
        # 5. SEED USER SETTINGS (links to sarcastic templates)
        seed_user_settings(users)
        
        db.session.commit()
        print("✅ Comprehensive seeding completed successfully!")
        print_seeding_summary()

def seed_sarcastic_templates():
    """
    REQUIREMENT 4: Sarcasm System - Sarcastic Templates
    Creates 15 sarcastic templates with varying severity levels (1-5)
    """
    print("\n😏 Seeding Sarcastic Templates...")
    
    templates = [
        # Severity Level 1 (Mild)
        {"text": "Oh wow, another brilliant bet! 🙄", "severity": 1},
        {"text": "Sure, let's double down on that genius move!", "severity": 1},
        {"text": "I'm absolutely shocked you lost that one... NOT!", "severity": 1},
        
        # Severity Level 2 (Light)
        {"text": "Congratulations! You've mastered the art of losing money! 🎉", "severity": 2},
        {"text": "Your betting strategy is truly... unique. Keep it up! 😬", "severity": 2},
        {"text": "Don't worry, the house always wins... except when you're playing!", "severity": 2},
        
        # Severity Level 3 (Medium)
        {"text": "I see you've chosen the 'donate to casino' strategy. Very charitable! 💸", "severity": 3},
        {"text": "Your luck is so bad, even a broken clock is right more often than you! ⏰", "severity": 3},
        {"text": "Maybe try a different game? Or a different hobby? Or a different planet? 🚀", "severity": 3},
        
        # Severity Level 4 (Strong)
        {"text": "At this rate, you'll be broke faster than a chocolate teapot melts! 🍫☕", "severity": 4},
        {"text": "Your betting skills are about as sharp as a bowling ball! 🎳", "severity": 4},
        {"text": "I've seen better decision-making from a Magic 8-Ball! 🎱", "severity": 4},
        
        # Severity Level 5 (Maximum)
        {"text": "Congratulations! You've achieved the impossible: making the house feel bad for you! 🏠💔", "severity": 5},
        {"text": "Your gambling prowess is legendary... in all the wrong ways! 🏆", "severity": 5},
        {"text": "Maybe it's time to switch to monopoly money? At least then you can't lose real cash! 💰", "severity": 5},
    ]
    
    sarcas_temps = []
    for template_data in templates:
        template = SarcasTemp(
            template_text=template_data["text"],
            severity_level=template_data["severity"]
        )
        sarcas_temps.append(template)
        db.session.add(template)
    
    db.session.flush()  # Get IDs without committing
    print(f"   ✓ Created {len(sarcas_temps)} sarcastic templates (severity levels 1-5)")
    return sarcas_temps

def seed_users_and_authentication():
    """
    REQUIREMENT 1: Users & Authentication
    Creates 12 sample user accounts:
    - 2 admin users
    - 10 regular users
    With varied usernames, emails, and profile settings
    """
    print("\n👥 Seeding Users & Authentication...")
    
    users_data = [
        # Admin Users
        {"username": "admin_casino", "email": "admin@casino.com", "is_admin": True, "profile": "admin_profile.png"},
        {"username": "admin_sarah", "email": "sarah.admin@casino.com", "is_admin": True, "profile": "sarah_admin.png"},
        
        # Regular Users
        {"username": "lucky_mike", "email": "mike.lucky@email.com", "is_admin": False, "profile": "mike_profile.png"},
        {"username": "gambler_jane", "email": "jane.gambler@email.com", "is_admin": False, "profile": "jane_profile.png"},
        {"username": "risk_taker_bob", "email": "bob.risk@email.com", "is_admin": False, "profile": "bob_profile.png"},
        {"username": "slot_queen_amy", "email": "amy.slots@email.com", "is_admin": False, "profile": "amy_profile.png"},
        {"username": "blackjack_tom", "email": "tom.bj@email.com", "is_admin": False, "profile": "tom_profile.png"},
        {"username": "roulette_lisa", "email": "lisa.roulette@email.com", "is_admin": False, "profile": "lisa_profile.png"},
        {"username": "plinko_pete", "email": "pete.plinko@email.com", "is_admin": False, "profile": "pete_profile.png"},
        {"username": "horse_henry", "email": "henry.horse@email.com", "is_admin": False, "profile": "henry_profile.png"},
        {"username": "mine_mary", "email": "mary.mines@email.com", "is_admin": False, "profile": "mary_profile.png"},
        {"username": "newbie_nick", "email": "nick.newbie@email.com", "is_admin": False, "profile": "default_profile.png"},
    ]
    
    users = []
    for user_data in users_data:
        # Use simple password for testing: "password123"
        pw_hash = generate_password_hash("password123")
        
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            pw_hash=pw_hash,
            is_admin=user_data["is_admin"],
            profile_picture=user_data["profile"],
            created_at=datetime.now() - timedelta(days=random.randint(1, 90))  # Random join dates
        )
        users.append(user)
        db.session.add(user)
    
    db.session.flush()  # Get user IDs without committing
    print(f"   ✓ Created {len(users)} users (2 admins, 10 regular users)")
    print("   ✓ All users have password: 'password123'")
    return users

def seed_financial_data(users):
    """
    REQUIREMENT 2: Financial Data
    Creates wallets and transactions for all users:
    - Each user gets multiple currency wallets (USD, EUR, BTC)
    - Starting balances vary realistically
    - 3-8 transactions per user (deposits, withdrawals, wins, losses)
    """
    print("\n💰 Seeding Financial Data...")
    
    currencies = ["USD", "EUR", "BTC"]
    starting_balances = {
        "USD": [500, 1000, 1500, 2000, 2500, 3000],
        "EUR": [400, 800, 1200, 1600, 2000, 2400],
        "BTC": [0.1, 0.25, 0.5, 0.75, 1.0, 1.5]
    }
    
    wallets = []
    transactions = []
    
    for user in users:
        # Each user gets 1-3 currency wallets
        user_currencies = random.sample(currencies, random.randint(1, 3))
        
        for currency in user_currencies:
            # Create wallet with starting balance
            balance = Decimal(str(random.choice(starting_balances[currency])))
            wallet = Wallet(
                user_id=user.user_id,
                currency=currency,
                balance=balance
            )
            wallets.append(wallet)
            db.session.add(wallet)
            db.session.flush()  # Get wallet ID
            
            # Create 3-8 transactions per wallet
            num_transactions = random.randint(3, 8)
            current_balance = Decimal('0')
            
            for i in range(num_transactions):
                # Transaction types and amounts
                txn_types = ["deposit", "withdraw", "bet_win", "bet_loss"]
                txn_type = random.choice(txn_types)
                
                if currency == "BTC":
                    amount = Decimal(str(round(random.uniform(0.01, 0.5), 4)))
                elif currency == "EUR":
                    amount = Decimal(str(round(random.uniform(10, 500), 2)))
                else:  # USD
                    amount = Decimal(str(round(random.uniform(10, 600), 2)))
                
                # Ensure withdrawals don't exceed balance
                if txn_type == "withdraw" and amount > current_balance:
                    amount = current_balance * Decimal('0.8')  # Withdraw 80% max
                
                transaction = Transaction(
                    wallet_id=wallet.wallet_id,
                    amount=amount,
                    txn_type=txn_type,
                    created_at=datetime.now() - timedelta(days=random.randint(0, 60))
                )
                transactions.append(transaction)
                db.session.add(transaction)
                
                # Update running balance
                if txn_type in ["deposit", "bet_win"]:
                    current_balance += amount
                else:
                    current_balance -= amount
            
            # Set final wallet balance
            wallet.balance = current_balance
    
    print(f"   ✓ Created {len(wallets)} wallets across {len(set(w.currency for w in wallets))} currencies")
    print(f"   ✓ Created {len(transactions)} transactions (deposits, withdrawals, wins, losses)")
    return wallets

def seed_gaming_data(users):
    """
    REQUIREMENT 3: Gaming Data
    Creates realistic gaming activity:
    - 25 game rounds across different games
    - Each round has an outcome
    - Multiple bets per round from different users
    - Realistic bet amounts and payouts
    """
    print("\n🎮 Seeding Gaming Data...")
    
    games = Game.query.all()
    if not games:
        print("   ⚠️  No games found! Run 'python seed_games.py' first.")
        return
    
    rounds = []
    outcomes = []
    bets = []
    
    # Create 25 game rounds
    for i in range(25):
        game = random.choice(games)
        
        # Create round
        start_time = datetime.now() - timedelta(days=random.randint(0, 30))
        end_time = start_time + timedelta(minutes=random.randint(1, 60))
        
        round_obj = Round(
            game_id=game.game_id,
            started_at=start_time,
            ended_at=end_time,
            rng_seed=f"seed_{random.randint(100000, 999999)}"
        )
        rounds.append(round_obj)
        db.session.add(round_obj)
        db.session.flush()  # Get round ID
        
        # Create outcome for round
        outcome_data, payout_multiplier = generate_outcome_for_game(game.code)
        outcome = Outcome(
            round_id=round_obj.round_id,
            outcome_data=outcome_data,
            payout_multiplier=payout_multiplier
        )
        outcomes.append(outcome)
        db.session.add(outcome)
        db.session.flush()  # Get outcome ID
        
        # Create 2-6 bets for this round
        num_bets = random.randint(2, 6)
        round_users = random.sample(users, min(num_bets, len(users)))
        
        for user in round_users:
            # Generate bet amount within game limits
            min_bet = float(game.min_bet)
            max_bet = float(game.max_bet)
            bet_amount = Decimal(str(round(random.uniform(min_bet, min(max_bet, min_bet * 50)), 2)))
            
            # Generate choice data based on game type
            choice_data = generate_choice_for_game(game.code)
            
            # Calculate payout (some bets win, some lose)
            win_chance = 0.45  # 45% win rate (house edge)
            if random.random() < win_chance:
                payout_amount = bet_amount * payout_multiplier
            else:
                payout_amount = Decimal('0')
            
            bet = Bet(
                round_id=round_obj.round_id,
                user_id=user.user_id,
                amount=bet_amount,
                choice_data=choice_data,
                placed_at=start_time + timedelta(seconds=random.randint(0, 300)),
                settled_at=end_time,
                outcome_id=outcome.outcome_id,
                payout_amount=payout_amount
            )
            bets.append(bet)
            db.session.add(bet)
    
    print(f"   ✓ Created {len(rounds)} game rounds across {len(set(r.game_id for r in rounds))} different games")
    print(f"   ✓ Created {len(outcomes)} game outcomes")
    print(f"   ✓ Created {len(bets)} bets with realistic win/loss ratios")

def seed_user_settings(users):
    """
    REQUIREMENT 4: Sarcasm System - User Settings
    Creates personalized settings for each user:
    - Sarcasm levels (1-5)
    - Theme preferences
    - Links to sarcastic templates
    """
    print("\n⚙️ Seeding User Settings...")
    
    templates = SarcasTemp.query.all()
    themes = ["dark", "light", "casino", "neon", "classic", "modern"]
    
    user_settings = []
    for user in users:
        # Assign random sarcasm level and theme
        sarcasm_level = random.randint(1, 5)
        theme = random.choice(themes)
        
        # Pick a template matching their sarcasm tolerance
        suitable_templates = [t for t in templates if t.severity_level <= sarcasm_level]
        chosen_template = random.choice(suitable_templates) if suitable_templates else templates[0]
        
        settings = UserSettings(
            user_id=user.user_id,
            sarcasm_level=sarcasm_level,
            theme=theme,
            sarcas_template_id=chosen_template.template_id
        )
        user_settings.append(settings)
        db.session.add(settings)
    
    print(f"   ✓ Created {len(user_settings)} user setting profiles")
    print(f"   ✓ Assigned themes: {', '.join(set(s.theme for s in user_settings))}")
    print(f"   ✓ Sarcasm levels range from 1 to 5")

def generate_outcome_for_game(game_code):
    """Generate realistic outcome data based on game type"""
    if game_code == "HORSE":
        order = list(range(1, 7))
        random.shuffle(order)
        return {"order": order}, Decimal("2.5")
    
    elif game_code == "BJ21":
        results = ["win", "lose", "push", "blackjack"]
        result = random.choice(results)
        multipliers = {"win": 2.0, "lose": 0.0, "push": 1.0, "blackjack": 2.5}
        return {"dealer": [10, "A"], "result": result}, Decimal(str(multipliers[result]))
    
    elif game_code == "ROULETTE":
        number = random.randint(0, 36)
        return {"number": number}, Decimal("35.0") if random.random() < 0.027 else Decimal("0.0")
    
    elif game_code == "SLOT":
        payout = random.choice([0, 5, 10, 25, 50, 100, 250])
        return {"reel_stop": [4, 3, 7, 3, 4], "payout": payout}, Decimal(str(payout / 10))
    
    elif game_code == "PLINKO":
        multiplier = random.choice([0.5, 1, 2, 5, 10])
        return {"bin": 3, "multiplier": multiplier}, Decimal(str(multiplier))
    
    elif game_code == "MINESWEEP":
        mine_hit = random.choice([True, False])
        return {"mine_hit": mine_hit}, Decimal("0.0") if mine_hit else Decimal("2.0")
    
    return {}, Decimal("1.0")

def generate_choice_for_game(game_code):
    """Generate realistic choice data based on game type"""
    if game_code == "HORSE":
        return {"bet_type": "win", "horse": random.randint(1, 6)}
    elif game_code == "BJ21":
        return {"actions": ["H", "S"], "hand": [10, 6]}
    elif game_code == "ROULETTE":
        return {"bet_type": "straight", "number": random.randint(0, 36)}
    elif game_code == "SLOT":
        return {"lines": [1, 2, 3]}
    elif game_code == "PLINKO":
        return {}
    elif game_code == "MINESWEEP":
        return {"squares_revealed": random.randint(1, 10)}
    return {}

def print_seeding_summary():
    """Print a summary of seeded data"""
    print("\n" + "="*60)
    print("📊 SEEDING SUMMARY")
    print("="*60)
    
    with app.app_context():
        print(f"👥 Users: {User.query.count()} (Admin: {User.query.filter_by(is_admin=True).count()})")
        print(f"💰 Wallets: {Wallet.query.count()}")
        print(f"💳 Transactions: {Transaction.query.count()}")
        print(f"🎮 Games: {Game.query.count()}")
        print(f"🎯 Rounds: {Round.query.count()}")
        print(f"🎲 Bets: {Bet.query.count()}")
        print(f"📝 Outcomes: {Outcome.query.count()}")
        print(f"⚙️  User Settings: {UserSettings.query.count()}")
        print(f"😏 Sarcastic Templates: {SarcasTemp.query.count()}")
        
        # Calculate total money in system
        total_usd = sum(w.balance for w in Wallet.query.filter_by(currency='USD').all())
        total_eur = sum(w.balance for w in Wallet.query.filter_by(currency='EUR').all())
        total_btc = sum(w.balance for w in Wallet.query.filter_by(currency='BTC').all())
        
        print(f"\n💰 Total Money in System:")
        if total_usd: print(f"   USD: ${total_usd:,.2f}")
        if total_eur: print(f"   EUR: €{total_eur:,.2f}")
        if total_btc: print(f"   BTC: ₿{total_btc:.4f}")
        
    print("="*60)
    print("✅ Ready for testing! Login with any username and password 'password123'")

if __name__ == "__main__":
    comprehensive_seed() 