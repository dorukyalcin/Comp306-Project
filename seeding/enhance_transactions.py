#!/usr/bin/env python3
"""
Enhance Transaction Data for Query 4
====================================

This seeder adds some withdrawal and additional deposit transactions
to enhance the financial pattern analysis in Query 4.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Wallet, Transaction
from sqlalchemy import text
from datetime import datetime, timedelta
import random
from decimal import Decimal

def enhance_transaction_data():
    """Add varied transaction patterns to existing users"""
    
    print("💳 Enhancing Transaction Data for Query 4...")
    
    # Get users who have placed bets (cohort users)
    users_with_bets = db.session.execute(text("""
        SELECT DISTINCT u.user_id, u.username 
        FROM users u 
        JOIN bets b ON u.user_id = b.user_id 
        WHERE u.username LIKE 'cohort_user_%'
        ORDER BY u.user_id 
        LIMIT 20
    """)).fetchall()
    
    if not users_with_bets:
        print("❌ No cohort users found. Please run cohort seeder first.")
        return
    
    print(f"📊 Adding varied transactions for {len(users_with_bets)} users...")
    
    for user_row in users_with_bets:
        user_id = user_row[0]
        username = user_row[1]
        
        # Get user's wallet
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            continue
            
        # Random number of additional transactions (0-5)
        num_additional_transactions = random.randint(0, 5)
        
        for _ in range(num_additional_transactions):
            # Random transaction type
            if random.random() < 0.7:  # 70% chance of deposit
                txn_type = 'deposit'
                amount = Decimal(str(random.randint(50, 500)))
                wallet.balance += amount
            else:  # 30% chance of withdrawal
                txn_type = 'withdraw'
                # Withdraw between 10-50% of current balance
                max_withdraw = wallet.balance * Decimal('0.5')
                if max_withdraw > 10:
                    amount = Decimal(str(random.uniform(10, float(max_withdraw))))
                    wallet.balance -= amount
                else:
                    continue  # Skip if balance too low
            
            # Random date within last 90 days
            days_ago = random.randint(1, 90)
            transaction_date = datetime.now() - timedelta(days=days_ago)
            
            # Create transaction
            transaction = Transaction(
                wallet_id=wallet.wallet_id,
                txn_type=txn_type,
                amount=amount,
                created_at=transaction_date
            )
            db.session.add(transaction)
    
    db.session.commit()
    print("✅ Enhanced transaction data successfully!")
    print("📊 Query 4 should now show more diverse financial patterns!")

def main():
    """Main function to run the transaction enhancer"""
    with app.app_context():
        try:
            enhance_transaction_data()
            print("\n🎉 Transaction enhancement completed!")
        except Exception as e:
            print(f"❌ Error enhancing transactions: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    main() 