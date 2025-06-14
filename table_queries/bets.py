import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Bet

def query_bets():
    """Execute SELECT * FROM bets equivalent query"""
    with app.app_context():
        print("💰 BETS TABLE - SELECT * FROM bets")
        print("=" * 50)
        
        bets = Bet.query.all()
        
        if not bets:
            print("No bets found in the database.")
            return
        
        print(f"Found {len(bets)} bets:\n")
        
        for bet in bets:
            print(f"Bet ID: {bet.bet_id}")
            print(f"Round ID: {bet.round_id}")
            print(f"User ID: {bet.user_id}")
            print(f"Amount: {bet.amount}")
            print(f"Payout Amount: {bet.payout_amount}")
            print(f"Choice Data: {bet.choice_data}")
            print("-" * 30)

if __name__ == "__main__":
    query_bets() 