#!/usr/bin/env python3
"""
Clean Database Seeding Script
=============================

This script provides a clean slate for database seeding with improved wallet balance management.
It ensures all users have positive wallet balances throughout their transaction history.

Usage:
    python seeding/clean_seed.py

Features:
- Completely resets the database
- Seeds with improved financial data (guaranteed positive balances)
- Creates realistic user accounts and transaction history
- Populates gaming data and horse racing history
- Shows comprehensive summary of seeded data
"""

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import app, db
from models import User, Wallet, Transaction, Game, Bet, Horse, Round
from comprehensive_seed import comprehensive_seed

def clean_and_seed():
    """
    Perform a complete database reset and reseed with positive wallet balances
    """
    
    print("🧹 CLEAN DATABASE SEEDING")
    print("=" * 50)
    print("This will completely reset your database and create fresh seed data.")
    print("All wallet balances will be guaranteed positive.")
    print()
    
    # Skip confirmation if running from script
    if not sys.stdin.isatty():
        confirm = 'yes'
    else:
        # Confirm action
        confirm = input("Are you sure you want to proceed? (yes/no): ").lower().strip()
    
    if confirm not in ['yes', 'y']:
        print("❌ Seeding cancelled.")
        return
    
    with app.app_context():
        print("\n🗑️  Dropping all existing tables...")
        try:
            db.drop_all()
            print("   ✓ All tables dropped successfully")
        except Exception as e:
            print(f"   ⚠️  Warning during table drop: {e}")
        
        print("\n🏗️  Creating fresh database schema...")
        try:
            db.create_all()
            print("   ✓ Database schema created successfully")
        except Exception as e:
            print(f"   ❌ Error creating schema: {e}")
            return
        
        print("\n🌱 Running comprehensive seeding with positive balances...")
        try:
            comprehensive_seed()
            
            print("\n📊 SEEDING SUMMARY")
            print("=" * 50)
            
            # Count what was created
            user_count = User.query.count()
            admin_count = User.query.filter_by(is_admin=True).count()
            wallet_count = Wallet.query.count()
            transaction_count = Transaction.query.count()
            game_count = Game.query.count()
            bet_count = Bet.query.count()
            horse_count = Horse.query.count()
            round_count = Round.query.count()
            
            print(f"👥 Users: {user_count} total ({admin_count} admins, {user_count - admin_count} regular)")
            print(f"💰 Wallets: {wallet_count} across multiple currencies")
            print(f"💳 Transactions: {transaction_count} (all maintaining positive balances)")
            print(f"🎮 Games: {game_count} different game types")
            print(f"🎲 Bets: {bet_count} historical bets placed")
            print(f"🐎 Horses: {horse_count} for racing")
            print(f"🏁 Rounds: {round_count} completed game rounds")
            
            # Show wallet balance ranges
            print(f"\n💵 WALLET BALANCE SUMMARY:")
            for currency in ['USD', 'EUR', 'BTC']:
                wallets = Wallet.query.filter_by(currency=currency).all()
                if wallets:
                    balances = [float(w.balance) for w in wallets]
                    min_bal = min(balances)
                    max_bal = max(balances)
                    avg_bal = sum(balances) / len(balances)
                    print(f"   {currency}: {len(wallets)} wallets, Range: {min_bal:.2f} - {max_bal:.2f}, Avg: {avg_bal:.2f}")
            
            # Check for any negative balances (should be none)
            negative_wallets = Wallet.query.filter(Wallet.balance < 0).count()
            if negative_wallets == 0:
                print(f"\n✅ SUCCESS: All {wallet_count} wallets have positive balances!")
            else:
                print(f"\n⚠️  WARNING: {negative_wallets} wallets have negative balances")
            
            print(f"\n🔐 LOGIN CREDENTIALS:")
            print(f"   All users have password: 'password123'")
            print(f"   Admin users: admin_casino, admin_sarah")
            print(f"   Regular users: lucky_mike, gambler_jane, risk_taker_bob, etc.")
            
            print(f"\n🚀 Database seeding completed successfully!")
            print(f"   You can now start your Flask app and test with realistic data.")
            
        except Exception as e:
            print(f"   ❌ Error during seeding: {e}")
            import traceback
            traceback.print_exc()

def quick_balance_check():
    """
    Quick utility to check current wallet balances without reseeding
    """
    print("💰 WALLET BALANCE CHECK")
    print("=" * 30)
    
    with app.app_context():
        total_wallets = Wallet.query.count()
        negative_wallets = Wallet.query.filter(Wallet.balance < 0).count()
        positive_wallets = total_wallets - negative_wallets
        
        print(f"Total wallets: {total_wallets}")
        print(f"Positive balances: {positive_wallets}")
        print(f"Negative balances: {negative_wallets}")
        
        if negative_wallets > 0:
            print(f"\n⚠️  Found {negative_wallets} wallets with negative balances:")
            negative = Wallet.query.filter(Wallet.balance < 0).all()
            for wallet in negative:
                user = User.query.get(wallet.user_id)
                print(f"   {user.username}: {wallet.balance} {wallet.currency}")
            print(f"\n💡 Run 'python seeding/clean_seed.py' to fix this.")
        else:
            print(f"\n✅ All wallets have positive balances!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        quick_balance_check()
    else:
        clean_and_seed() 