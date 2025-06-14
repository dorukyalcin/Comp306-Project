from app import app, db
from models import User, UserSettings, Wallet, Transaction, Game, Round, Outcome, Bet, SarcasTemp
from sqlalchemy import text

def view_database():
    with app.app_context():
        print("=" * 60)
        print("DATABASE OVERVIEW")
        print("=" * 60)
        
        # List all tables
        print("\n📋 TABLES IN DATABASE:")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        for table in tables:
            print(f"  • {table}")
        
        print("\n" + "=" * 60)
        print("TABLE CONTENTS")
        print("=" * 60)
        
        # Users table
        print("\n👥 USERS:")
        users = User.query.all()
        if users:
            for user in users:
                print(f"  ID: {user.user_id}, Username: {user.username}, Email: {user.email}")
                print(f"      Admin: {user.is_admin}, Created: {user.created_at}")
                print(f"      Profile Picture: {user.profile_picture}")
                print(f"      Password Hash: {user.pw_hash}")
                print()
        else:
            print("  No users found")
        
        # Wallets table
        print("\n💰 WALLETS:")
        wallets = Wallet.query.all()
        if wallets:
            for wallet in wallets:
                print(f"  ID: {wallet.wallet_id}, User ID: {wallet.user_id}")
                print(f"      Currency: {wallet.currency}, Balance: {wallet.balance}")
        else:
            print("  No wallets found")
        
        # Transactions table
        print("\n💳 TRANSACTIONS:")
        transactions = Transaction.query.all()
        if transactions:
            for txn in transactions:
                print(f"  ID: {txn.txn_id}, Wallet ID: {txn.wallet_id}")
                print(f"      Amount: {txn.amount}, Type: {txn.txn_type}")
                print(f"      Created: {txn.created_at}")
        else:
            print("  No transactions found")
        
        # Games table
        print("\n🎮 GAMES:")
        games = Game.query.all()
        if games:
            for game in games:
                print(f"  ID: {game.game_id}, Code: {game.code}")
                print(f"      House Edge: {game.house_edge}, Min Bet: {game.min_bet}")
                print(f"      Max Bet: {game.max_bet}, Active: {game.is_active}")
                print(f"      Rules: {game.payout_rule_json}")
        else:
            print("  No games found")
        
        # Rounds table
        print("\n🎯 ROUNDS:")
        rounds = Round.query.all()
        if rounds:
            for round in rounds:
                print(f"  ID: {round.round_id}, Game ID: {round.game_id}")
                print(f"      Started: {round.started_at}, Ended: {round.ended_at}")
        else:
            print("  No rounds found")
        
        # Bets table
        print("\n🎲 BETS:")
        bets = Bet.query.all()
        if bets:
            for bet in bets:
                print(f"  ID: {bet.bet_id}, User ID: {bet.user_id}")
                print(f"      Amount: {bet.amount}, Placed: {bet.placed_at}")
        else:
            print("  No bets found")
        
        # User Settings table
        print("\n⚙️ USER SETTINGS:")
        settings = UserSettings.query.all()
        if settings:
            for setting in settings:
                print(f"  User ID: {setting.user_id}")
                print(f"      Sarcasm Level: {setting.sarcasm_level}, Theme: {setting.theme}")
        else:
            print("  No user settings found")
        
        # Sarcastic Templates table
        print("\n😏 SARCASTIC TEMPLATES:")
        templates = SarcasTemp.query.all()
        if templates:
            for template in templates:
                print(f"  ID: {template.template_id}")
                print(f"      Text: {template.template_text}")
                print(f"      Severity: {template.severity_level}")
        else:
            print("  No sarcastic templates found")
        
        print("\n" + "=" * 60)
        print("DATABASE SUMMARY")
        print("=" * 60)
        print(f"Total Users: {len(users)}")
        print(f"Total Wallets: {len(wallets)}")
        print(f"Total Transactions: {len(transactions)}")
        print(f"Total Games: {len(games)}")
        print(f"Total Rounds: {len(rounds)}")
        print(f"Total Bets: {len(bets)}")
        print("=" * 60)

if __name__ == '__main__':
    view_database() 