from app import app, db
from models import Bet

with app.app_context():
    bet = Bet.query.filter(Bet.choice_data.isnot(None)).first()
    if bet:
        print("Sample bet:")
        print(f"ID: {bet.bet_id}")
        print(f"Amount: {bet.amount}")
        print(f"Choice data: {bet.choice_data}")
    else:
        print("No bets with choice_data found") 