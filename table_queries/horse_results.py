import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import HorseResult

def query_horse_results():
    """Execute SELECT * FROM horse_results equivalent query"""
    with app.app_context():
        print("🏆 HORSE_RESULTS TABLE - SELECT * FROM horse_results")
        print("=" * 50)
        
        results = HorseResult.query.all()
        
        if not results:
            print("No horse results found in the database.")
            return
        
        print(f"Found {len(results)} horse results:\n")
        
        for result in results:
            print(f"Round ID: {result.round_id}")
            print(f"Horse ID: {result.horse_id}")
            print(f"Lane Number: {result.lane_no}")
            print(f"Finish Place: {result.finish_place}")
            print(f"Race Time (seconds): {result.race_time_sec}")
            print("-" * 30)

if __name__ == "__main__":
    query_horse_results() 