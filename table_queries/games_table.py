import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Game

def query_games():
    """Execute SELECT * FROM games equivalent query"""
    with app.app_context():
        print("🎮 GAMES TABLE - SELECT * FROM games")
        print("=" * 50)
        
        games = Game.query.all()
        
        if not games:
            print("No games found in the database.")
            return
        
        print(f"Found {len(games)} games:\n")
        
        for game in games:
            print(f"Game ID: {game.game_id}")
            print(f"Code: {game.code}")
            print(f"House Edge: {game.house_edge}")
            print(f"Min Bet: {game.min_bet}")
            print(f"Max Bet: {game.max_bet}")
            print(f"Is Active: {game.is_active}")
            print(f"Payout Rule JSON: {game.payout_rule_json}")
            print("-" * 30)

if __name__ == "__main__":
    query_games() 