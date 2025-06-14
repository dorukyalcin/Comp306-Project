#!/usr/bin/env python3
"""
Database Reset Script - Clears all data from the database
This allows for fresh seeding when needed
"""

import sys
import os
sys.path.insert(0, '/app')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import *

def reset_database():
    """
    Reset the database by dropping and recreating all tables
    This will permanently delete all data
    """
    print("🗑️  DATABASE RESET - CLEARING ALL DATA")
    print("=" * 50)
    print("⚠️  WARNING: This will permanently delete ALL data!")
    print("   • All users and accounts")
    print("   • All wallets and transactions") 
    print("   • All game history and bets")
    print("   • All settings and templates")
    print()
    
    # Ask for confirmation
    confirmation = input("Type 'DELETE ALL DATA' to confirm: ")
    if confirmation != "DELETE ALL DATA":
        print("❌ Reset cancelled. No data was deleted.")
        return False
    
    print()
    print("🗑️  Dropping all database tables...")
    
    with app.app_context():
        try:
            # Drop all tables
            db.drop_all()
            print("   ✅ All tables dropped successfully!")
            
            # Recreate all tables
            print("📋 Recreating database tables...")
            db.create_all()
            print("   ✅ All tables recreated successfully!")
            
            print()
            print("✅ DATABASE RESET COMPLETE!")
            print("=" * 50)
            print("💡 The database is now empty and ready for fresh seeding")
            print("🌱 Run 'python seeding/comprehensive_seed.py' to add test data")
            print("🎮 Run 'python seeding/seed_games.py' to add games")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during database reset: {str(e)}")
            return False

if __name__ == "__main__":
    reset_database() 