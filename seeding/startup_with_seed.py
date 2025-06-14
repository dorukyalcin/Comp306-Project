#!/usr/bin/env python3
"""
Enhanced startup script that fully initializes the database with all required data
This script runs automatically when the Docker container starts up
"""

import sys
import os
sys.path.insert(0, '/app')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
import models  # Ensure models are loaded
from seeding.seed_games import seed_games
from seeding.comprehensive_seed import comprehensive_seed
import time

def full_database_initialization():
    """
    Complete database initialization and seeding process:
    1. Create all database tables
    2. Seed games catalog
    3. Run comprehensive data seeding (users, financial, gaming, sarcasm data)
    """
    
    print("🚀 Starting Full Database Initialization...")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Step 1: Create all database tables
            print("📋 Step 1: Creating database tables...")
            db.create_all()
            print("   ✅ Database tables created successfully!")
            
            # Step 2: Check if games exist, if not seed them
            from models import Game
            if Game.query.count() == 0:
                print("\n🎮 Step 2: Seeding games catalog...")
                seed_games()
                print("   ✅ Games catalog seeded successfully!")
            else:
                print("\n🎮 Step 2: Games catalog already exists, skipping...")
            
            # Step 3: Run comprehensive seeding (users, wallets, transactions, etc.)
            print("\n🌱 Step 3: Running comprehensive data seeding...")
            comprehensive_seed()
            
            print("\n" + "=" * 60)
            print("🎉 DATABASE INITIALIZATION COMPLETE!")
            print("=" * 60)
            print("🌐 Your sarcastic gambling site is ready!")
            print("🔗 Visit: http://localhost:8000")
            print("👤 Login credentials: Any username with password 'password123'")
            print("🔧 Admin users: 'admin_casino' or 'admin_sarah'")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during database initialization: {str(e)}")
            return False

def wait_for_database():
    """
    Wait for PostgreSQL database to be ready
    This is important in Docker environments where the web container
    might start before the database container is ready
    """
    print("⏳ Waiting for database to be ready...")
    
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            with app.app_context():
                # Try to connect to database
                db.engine.connect()
                print("   ✅ Database connection established!")
                return True
        except Exception as e:
            retry_count += 1
            print(f"   ⏳ Attempt {retry_count}/{max_retries}: Database not ready yet...")
            time.sleep(2)
    
    print("❌ Failed to connect to database after maximum retries")
    return False

def main():
    """Main function that orchestrates the complete initialization"""
    
    print("🎰 SARCASTIC GAMBLING SITE - STARTUP SCRIPT")
    print("=" * 60)
    
    # Wait for database to be ready (important for Docker)
    if not wait_for_database():
        print("❌ Cannot proceed without database connection")
        sys.exit(1)
    
    # Run full initialization
    if full_database_initialization():
        print("✅ Startup completed successfully!")
        sys.exit(0)
    else:
        print("❌ Startup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 