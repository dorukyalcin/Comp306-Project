import sys
import os
sys.path.insert(0, '/app')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Wallet
from decimal import Decimal

def fix_missing_wallets():
    """
    Check for users without wallets and create default USD wallets for them
    """
    with app.app_context():
        print("🔍 Checking for users without wallets...")
        
        # Find users without wallets
        users_without_wallets = []
        all_users = User.query.all()
        
        for user in all_users:
            if not user.wallets:
                users_without_wallets.append(user)
        
        if not users_without_wallets:
            print("✅ All users have wallets!")
            return
        
        print(f"⚠️  Found {len(users_without_wallets)} users without wallets:")
        for user in users_without_wallets:
            print(f"   - {user.username} (ID: {user.user_id})")
        
        # Create default USD wallets for users without wallets
        print("\n💰 Creating default USD wallets...")
        
        wallets_created = 0
        for user in users_without_wallets:
            try:
                # Create a default USD wallet with $1000 starting balance
                wallet = Wallet(
                    user_id=user.user_id,
                    currency='USD',  # USD is always the default currency
                    balance=Decimal('1000.00')
                )
                db.session.add(wallet)
                wallets_created += 1
                print(f"   ✓ Created USD wallet for {user.username}")
                
            except Exception as e:
                print(f"   ✗ Failed to create wallet for {user.username}: {str(e)}")
        
        try:
            db.session.commit()
            print(f"\n✅ Successfully created {wallets_created} wallets!")
            
            # Verify all users now have wallets
            remaining_users_without_wallets = []
            for user in User.query.all():
                if not user.wallets:
                    remaining_users_without_wallets.append(user)
            
            if remaining_users_without_wallets:
                print(f"⚠️  Still {len(remaining_users_without_wallets)} users without wallets")
            else:
                print("🎉 All users now have wallets!")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing changes: {str(e)}")

if __name__ == "__main__":
    fix_missing_wallets() 