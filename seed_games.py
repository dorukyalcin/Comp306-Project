from app import db
from models import Game

def seed_games():
    games = [
        Game(code='HORSE', house_edge=0.06, min_bet=1.00, max_bet=1000.00, is_active=True, payout_rule_json={"type":"pari-mutuel","runners":6}),
        Game(code='BJ21', house_edge=0.015, min_bet=1.00, max_bet=500.00, is_active=True, payout_rule_json={"dealer_stands_on":17,"blackjack_pays":"3:2"}),
        Game(code='ROULETTE', house_edge=0.027, min_bet=1.00, max_bet=1000.00, is_active=True, payout_rule_json={"wheel":"single-zero"}),
        Game(code='SLOT', house_edge=0.04, min_bet=0.20, max_bet=50.00, is_active=True, payout_rule_json={"reels":5,"paylines":20,"rtp":96}),
        Game(code='PLINKO', house_edge=0.03, min_bet=0.10, max_bet=200.00, is_active=True, payout_rule_json={"rows":16,"multipliers":[0.5,1,2,5,10]}),
        Game(code='MINESWEEP', house_edge=0.05, min_bet=0.10, max_bet=200.00, is_active=True, payout_rule_json={"grid":"5x5","mines":1,"no_hints":True}),
    ]
    db.session.bulk_save_objects(games)
    db.session.commit()

if __name__ == '__main__':
    with db.session.begin():
        seed_games()
    print('Seeded games table.') 