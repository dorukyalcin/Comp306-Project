import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, UserSettings, Wallet, Transaction, Game, Round, Outcome, Bet, SarcasTemp, Horse, HorseRunner, HorseResult
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
            for txn in transactions[:5]:  # Show only first 5 to avoid too much output
                print(f"  ID: {txn.txn_id}, Wallet ID: {txn.wallet_id}")
                print(f"      Amount: {txn.amount}, Type: {txn.txn_type}")
                print(f"      Created: {txn.created_at}")
            if len(transactions) > 5:
                print(f"  ... and {len(transactions) - 5} more transactions")
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
        else:
            print("  No games found")
        
        # Rounds table
        print("\n🎯 ROUNDS:")
        rounds = Round.query.all()
        if rounds:
            for round in rounds[:3]:  # Show only first 3
                print(f"  ID: {round.round_id}, Game ID: {round.game_id}")
                print(f"      Started: {round.started_at}, Ended: {round.ended_at}")
            if len(rounds) > 3:
                print(f"  ... and {len(rounds) - 3} more rounds")
        else:
            print("  No rounds found")
        
        # Bets table
        print("\n🎲 BETS:")
        bets = Bet.query.all()
        if bets:
            for bet in bets[:3]:  # Show only first 3
                print(f"  ID: {bet.bet_id}, User ID: {bet.user_id}")
                print(f"      Amount: {bet.amount}, Placed: {bet.placed_at}")
            if len(bets) > 3:
                print(f"  ... and {len(bets) - 3} more bets")
        else:
            print("  No bets found")
        
        # Horse Racing Tables
        print("\n🐎 HORSES:")
        horses = Horse.query.all()
        if horses:
            for horse in horses:
                print(f"  ID: {horse.horse_id}, Name: {horse.name}")
                print(f"      Age: {horse.age}, Speed: {horse.base_speed}, Temperament: {horse.temperament}")
        else:
            print("  No horses found")
        
        print("\n🏁 HORSE RUNNERS:")
        horse_runners = HorseRunner.query.all()
        if horse_runners:
            for runner in horse_runners:
                print(f"  Round: {runner.round_id}, Horse: {runner.horse_id}")
                print(f"      Lane: {runner.lane_no}, Odds: {runner.odds}")
        else:
            print("  No horse runners found")
        
        print("\n🏆 HORSE RESULTS:")
        horse_results = HorseResult.query.all()
        if horse_results:
            for result in horse_results:
                print(f"  Round: {result.round_id}, Horse: {result.horse_id}")
                print(f"      Lane: {result.lane_no}, Position: {result.finish_place}")
                print(f"      Time: {result.race_time_sec} seconds")
        else:
            print("  No horse results found")
        
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
        print(f"Total Horses: {len(horses)}")
        print(f"Total Horse Runners: {len(horse_runners)}")
        print(f"Total Horse Results: {len(horse_results)}")
        print(f"Total User Settings: {len(settings)}")
        print(f"Total Sarcastic Templates: {len(templates)}")
        print("=" * 60)

if __name__ == '__main__':
    view_database() 