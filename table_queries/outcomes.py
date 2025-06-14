import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Outcome

def query_outcomes():
    """Execute SELECT * FROM outcomes equivalent query"""
    with app.app_context():
        print("📝 OUTCOMES TABLE - SELECT * FROM outcomes")
        print("=" * 50)
        
        outcomes = Outcome.query.all()
        
        if not outcomes:
            print("No outcomes found in the database.")
            return
        
        print(f"Found {len(outcomes)} outcomes:\n")
        
        for outcome in outcomes:
            print(f"Outcome ID: {outcome.outcome_id}")
            print(f"Round ID: {outcome.round_id}")
            print(f"Payout Multiplier: {outcome.payout_multiplier}")
            print(f"Outcome Data: {outcome.outcome_data}")
            print("-" * 30)

if __name__ == "__main__":
    query_outcomes() 