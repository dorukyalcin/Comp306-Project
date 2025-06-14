import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import HorseRunner

def query_horse_runners():
    """Execute SELECT * FROM horse_runners equivalent query"""
    with app.app_context():
        print("🏁 HORSE_RUNNERS TABLE - SELECT * FROM horse_runners")
        print("=" * 50)
        
        runners = HorseRunner.query.all()
        
        if not runners:
            print("No horse runners found in the database.")
            return
        
        print(f"Found {len(runners)} horse runners:\n")
        
        for runner in runners:
            print(f"Round ID: {runner.round_id}")
            print(f"Horse ID: {runner.horse_id}")
            print(f"Lane Number: {runner.lane_no}")
            print(f"Odds: {runner.odds}")
            print("-" * 30)

if __name__ == "__main__":
    query_horse_runners() 