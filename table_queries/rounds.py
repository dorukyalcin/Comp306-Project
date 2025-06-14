import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Round

def query_rounds():
    """Execute SELECT * FROM rounds equivalent query"""
    with app.app_context():
        print("🎯 ROUNDS TABLE - SELECT * FROM rounds")
        print("=" * 50)
        
        rounds = Round.query.all()
        
        if not rounds:
            print("No rounds found in the database.")
            return
        
        print(f"Found {len(rounds)} rounds:\n")
        
        for round in rounds:
            print(f"Round ID: {round.round_id}")
            print(f"Game ID: {round.game_id}")
            print(f"Started At: {round.started_at}")
            print(f"Ended At: {round.ended_at}")
            print(f"RNG Seed: {round.rng_seed}")
            print("-" * 30)

if __name__ == "__main__":
    query_rounds() 