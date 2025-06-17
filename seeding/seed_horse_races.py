#!/usr/bin/env python3
"""
Horse Racing Data Seeder

This script seeds horse racing data including:
- Race rounds
- Horse runners (horses participating in each race)
- Race results
- Bets placed on horses

It creates realistic racing scenarios with varied outcomes and betting patterns.
"""

import sys
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Game, Round, Horse, HorseRunner, HorseResult, User, Wallet, Bet
from sqlalchemy import func

def create_race_round(game_id, start_time):
    """Create a new race round"""
    round = Round(
        game_id=game_id,
        started_at=start_time,
        ended_at=start_time + timedelta(minutes=2)
    )
    db.session.add(round)
    db.session.flush()
    return round

def select_horses_for_race(num_horses=6):
    """Select random horses for a race, considering their rest periods"""
    available_horses = Horse.query.all()
    return random.sample(available_horses, min(num_horses, len(available_horses)))

def calculate_odds(horse):
    """Calculate odds based on horse characteristics"""
    base_odds = 10.0 - float(horse.base_speed)  # Faster horses have lower odds
    age_factor = abs(7 - horse.age) * 0.2  # Horses around age 7 get slightly better odds
    
    # Temperament adjustments
    temperament_factors = {
        'calm': -0.3,
        'confident': -0.2,
        'aggressive': 0.2,
        'nervous': 0.3,
        'unpredictable': 0.4
    }
    
    odds = base_odds + age_factor + temperament_factors.get(horse.temperament, 0)
    odds = max(1.5, min(20.0, odds))  # Keep odds between 1.5 and 20.0
    return Decimal(str(round(odds, 2)))

def create_race_runners(round_id, horses):
    """Create horse runners for a race with calculated odds"""
    runners = []
    for i, horse in enumerate(horses, 1):
        odds = calculate_odds(horse)
        runner = HorseRunner(
            round_id=round_id,
            horse_id=horse.horse_id,
            lane_no=i,
            odds=odds
        )
        db.session.add(runner)
        runners.append(runner)
    db.session.flush()
    return runners

def simulate_race_results(round_id, runners):
    """Simulate race results based on horse characteristics"""
    race_times = []
    for runner in runners:
        horse = Horse.query.get(runner.horse_id)
        
        # Base time calculation (faster base_speed = lower time)
        base_time = 120 - float(horse.base_speed) * 5
        
        # Age factor (horses around age 7 perform best)
        age_factor = abs(7 - horse.age) * 0.5
        
        # Temperament factor
        temperament_factors = {
            'calm': -1,
            'confident': -0.5,
            'aggressive': random.uniform(-2, 2),
            'nervous': random.uniform(0, 2),
            'unpredictable': random.uniform(-3, 3)
        }
        
        # Random factor for excitement
        random_factor = random.uniform(-2, 2)
        
        # Calculate final race time
        race_time = base_time + age_factor + temperament_factors.get(horse.temperament, 0) + random_factor
        race_times.append((runner.horse_id, race_time, runner.lane_no))
    
    # Sort by race time and create results
    race_times.sort(key=lambda x: x[1])
    for place, (horse_id, time, lane_no) in enumerate(race_times, 1):
        result = HorseResult(
            round_id=round_id,
            horse_id=horse_id,
            lane_no=lane_no,
            finish_place=place,
            race_time_sec=Decimal(str(round(time, 2)))
        )
        db.session.add(result)
    
    db.session.flush()
    return race_times

def create_bets_for_race(round_id, runners, num_bets=20):
    """Create realistic betting patterns for the race"""
    users = User.query.filter_by(is_admin=False).all()
    if not users:
        print("No users found for betting!")
        return
    
    for _ in range(num_bets):
        user = random.choice(users)
        wallet = Wallet.query.filter_by(user_id=user.user_id).first()
        if not wallet:
            continue
            
        runner = random.choice(runners)
        
        # Bet amount based on odds (people tend to bet more on favorites)
        base_amount = random.uniform(10, 100)
        if float(runner.odds) < 5:  # Favorite
            amount = base_amount * 1.5
        else:  # Underdog
            amount = base_amount * 0.7
            
        amount = Decimal(str(round(amount, 2)))
        
        # Create bet
        bet = Bet(
            user_id=user.user_id,
            round_id=round_id,
            amount=amount,
            choice_data={'horse_id': str(runner.horse_id)},
            placed_at=runner.round.started_at - timedelta(minutes=random.randint(1, 30))
        )
        
        # Calculate payout based on race results
        result = HorseResult.query.filter_by(
            round_id=round_id,
            horse_id=runner.horse_id
        ).first()
        
        if result and result.finish_place == 1:
            # Convert both to Decimal for multiplication
            payout = amount * Decimal(str(float(runner.odds)))
            bet.payout_amount = Decimal(str(round(float(payout), 2)))
        else:
            bet.payout_amount = Decimal('0')
            
        db.session.add(bet)
    
    db.session.flush()

def seed_horse_races(num_races=50):
    """Main function to seed horse racing data"""
    print("🏇 Starting horse race data seeding...")
    
    # Get horse racing game
    game = Game.query.filter_by(code='HORSE').first()
    if not game:
        print("❌ Horse racing game not found!")
        return False
        
    # Start time for first race
    start_time = datetime.now() - timedelta(days=30)
    
    races_created = 0
    for i in range(num_races):
        try:
            # Create race round
            round = create_race_round(game.game_id, start_time)
            
            # Select and create runners
            horses = select_horses_for_race()
            runners = create_race_runners(round.round_id, horses)
            
            # Simulate race results
            simulate_race_results(round.round_id, runners)
            
            # Create bets
            create_bets_for_race(round.round_id, runners)
            
            # Move to next race time
            start_time += timedelta(hours=random.randint(4, 12))
            races_created += 1
            
            # Commit every 10 races
            if i % 10 == 9:
                db.session.commit()
                print(f"   ✓ Created {races_created} races...")
                
        except Exception as e:
            print(f"   ✗ Error creating race {i+1}: {str(e)}")
            db.session.rollback()
            continue
    
    try:
        db.session.commit()
        print(f"🎉 Successfully seeded {races_created} horse races!")
        
        # Print summary statistics
        print("\n📊 Race Statistics:")
        print(f"   Total races: {Round.query.filter_by(game_id=game.game_id).count()}")
        print(f"   Total runners: {HorseRunner.query.count()}")
        print(f"   Total results: {HorseResult.query.count()}")
        
        # Use proper JSON operator for PostgreSQL
        total_bets = db.session.query(Bet).filter(
            Bet.choice_data.op('->>')('horse_id').isnot(None)
        ).count()
        print(f"   Total bets: {total_bets}")
        
        # Top winning horses
        top_winners = db.session.query(
            Horse.name,
            func.count(HorseResult.horse_id).label('wins')
        ).join(HorseResult).filter(
            HorseResult.finish_place == 1
        ).group_by(
            Horse.horse_id
        ).order_by(
            func.count(HorseResult.horse_id).desc()
        ).limit(3).all()
        
        print("\n🏆 Top Winning Horses:")
        for horse, wins in top_winners:
            print(f"   - {horse}: {wins} wins")
            
    except Exception as e:
        print(f"❌ Error in final commit: {str(e)}")
        db.session.rollback()
        return False
        
    return True

if __name__ == '__main__':
    with app.app_context():
        if seed_horse_races():
            print("✅ Horse race seeding completed successfully!")
        else:
            print("❌ Horse race seeding failed!")
            exit(1) 