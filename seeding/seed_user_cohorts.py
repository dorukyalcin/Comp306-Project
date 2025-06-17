#!/usr/bin/env python3
"""
User Cohort Seeding Script
=========================

This script generates realistic betting behavior data for cohort analysis:
- Creates users with different registration dates (cohorts)
- Generates betting patterns over time
- Ensures data matches Query 5 requirements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Wallet, Transaction, Game, Round, Bet, Outcome
from werkzeug.security import generate_password_hash
from decimal import Decimal
import random
from datetime import datetime, timedelta
import json

def make_naive(dt):
    """Convert a datetime to naive (no timezone)"""
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

def seed_user_cohorts():
    """
    Create users with varied registration dates and betting patterns
    to support cohort analysis in Query 5.
    """
    with app.app_context():
        print("\n🎯 Seeding User Cohort Data...")
        
        # First, check if we have games
        games = Game.query.all()
        if not games:
            print("⚠️  No games found! Please run seed_games.py first.")
            return False
            
        # Create users across different cohorts (last 3 months)
        current_time = make_naive(datetime.now())
        cohort_months = [
            make_naive(current_time - timedelta(days=90)),  # 3 months ago
            make_naive(current_time - timedelta(days=60)),  # 2 months ago
            make_naive(current_time - timedelta(days=30)),  # 1 month ago
            make_naive(current_time - timedelta(days=15))   # Recent cohort
        ]
        
        users_per_cohort = 5  # 5 users per cohort = 20 total users
        users_created = []
        
        # Create users for each cohort
        for cohort_date in cohort_months:
            for i in range(users_per_cohort):
                username = f"cohort_{cohort_date.strftime('%Y%m')}_{i+1}"
                user = User(
                    username=username,
                    email=f"{username}@example.com",
                    pw_hash=generate_password_hash("password123"),
                    is_admin=False,
                    profile_picture="default_profile.png",
                    created_at=cohort_date + timedelta(days=random.randint(0, 5))  # Spread within month
                )
                db.session.add(user)
                db.session.flush()  # Get user ID
                
                # Create wallet with initial balance
                wallet = Wallet(
                    user_id=user.user_id,
                    currency='USD',
                    balance=Decimal(str(random.randint(500, 2000)))
                )
                db.session.add(wallet)
                db.session.flush()
                
                # Record initial deposit
                deposit = Transaction(
                    wallet_id=wallet.wallet_id,
                    amount=wallet.balance,
                    txn_type='deposit',
                    created_at=user.created_at + timedelta(minutes=random.randint(5, 60))
                )
                db.session.add(deposit)
                users_created.append(user)
        
        db.session.commit()
        print(f"✓ Created {len(users_created)} users across {len(cohort_months)} cohorts")
        
        # Generate betting activity for each user
        total_bets = 0
        total_rounds = 0
        
        for user in users_created:
            # Determine user's betting pattern
            is_active = random.random() < 0.7  # 70% chance of being active
            if not is_active:
                continue
                
            # Calculate betting period
            days_to_first_bet = random.randint(1, 10)  # Wait 1-10 days before first bet
            betting_start = make_naive(user.created_at + timedelta(days=days_to_first_bet))
            current_time = make_naive(datetime.now())
            betting_end = min(current_time, betting_start + timedelta(days=random.randint(20, 60)))
            
            # Generate 10-50 bets per active user
            num_bets = random.randint(10, 50)
            
            for _ in range(num_bets):
                # Pick a random game
                game = random.choice(games)
                
                # Create or reuse a round
                round_obj = None
                if random.random() < 0.3:  # 30% chance of reusing a round
                    round_obj = Round.query.filter_by(game_id=game.game_id)\
                                    .order_by(Round.started_at.desc()).first()
                    if round_obj:
                        outcome = Outcome.query.filter_by(round_id=round_obj.round_id).first()
                
                # Create new round if we couldn't reuse one
                if not round_obj:
                    bet_time = betting_start + timedelta(
                        days=random.randint(0, (betting_end - betting_start).days),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                    
                    round_obj = Round(
                        game_id=game.game_id,
                        started_at=bet_time,
                        ended_at=bet_time + timedelta(minutes=random.randint(1, 10)),
                        rng_seed=f"seed_{random.randint(100000, 999999)}"
                    )
                    db.session.add(round_obj)
                    db.session.flush()
                    total_rounds += 1
                    
                    # Create outcome
                    outcome = Outcome(
                        round_id=round_obj.round_id,
                        outcome_data={'result': random.randint(1, 36)},
                        payout_multiplier=Decimal(str(random.uniform(1.5, 3.0)))
                    )
                    db.session.add(outcome)
                    db.session.flush()
                
                # Create bet
                bet_amount = Decimal(str(random.uniform(10, 200)))
                won = random.random() < 0.4  # 40% win rate
                payout = bet_amount * outcome.payout_multiplier if won else Decimal('0')
                
                bet = Bet(
                    round_id=round_obj.round_id,
                    user_id=user.user_id,
                    amount=bet_amount,
                    choice_data={'type': 'number', 'choice': random.randint(1, 36)},
                    placed_at=round_obj.started_at - timedelta(minutes=random.randint(1, 5)),
                    settled_at=round_obj.ended_at,
                    outcome_id=outcome.outcome_id,
                    payout_amount=payout
                )
                db.session.add(bet)
                total_bets += 1
                
                # Update wallet and create transactions
                wallet = Wallet.query.filter_by(user_id=user.user_id).first()
                
                # Bet transaction (money out)
                bet_txn = Transaction(
                    wallet_id=wallet.wallet_id,
                    amount=bet_amount,
                    txn_type='bet_loss' if not won else 'bet',
                    created_at=bet.placed_at
                )
                db.session.add(bet_txn)
                wallet.balance -= bet_amount
                
                # Win transaction (if won)
                if won:
                    win_txn = Transaction(
                        wallet_id=wallet.wallet_id,
                        amount=payout,
                        txn_type='bet_win',
                        created_at=bet.settled_at
                    )
                    db.session.add(win_txn)
                    wallet.balance += payout
                
                # Commit every 50 bets to avoid huge transactions
                if total_bets % 50 == 0:
                    db.session.commit()
        
        db.session.commit()
        print(f"✓ Generated {total_bets} bets across {total_rounds} rounds")
        print(f"✓ Created realistic betting patterns for cohort analysis")
        return True

if __name__ == "__main__":
    if seed_user_cohorts():
        print("\n✅ User cohort seeding completed successfully!")
        print("You can now run Query 5 to see betting behavior analysis.")
    else:
        print("\n❌ Error seeding user cohort data.") 