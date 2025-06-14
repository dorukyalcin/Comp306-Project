#!/usr/bin/env python3
"""
Horse Racing Seeding Script

This script seeds the horses table with realistic horse data.
Each horse has unique characteristics that affect racing performance.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Horse
from decimal import Decimal

def seed_horses():
    """Seed the horses table with diverse horse data"""
    
    # Create all tables first
    print("🔨 Creating database tables...")
    db.create_all()
    print("   ✓ Database tables created")
    
    # Horse data with varied stats for interesting racing dynamics
    horses_data = [
        # Young speedsters
        {"name": "Lightning Bolt", "age": 3, "base_speed": Decimal("9.2"), "temperament": "confident"},
        {"name": "Thunder Strike", "age": 4, "base_speed": Decimal("8.8"), "temperament": "aggressive"},
        {"name": "Wind Runner", "age": 2, "base_speed": Decimal("9.0"), "temperament": "nervous"},
        
        # Prime age horses with balanced stats
        {"name": "Fire Dash", "age": 5, "base_speed": Decimal("8.5"), "temperament": "calm"},
        {"name": "Storm Chaser", "age": 6, "base_speed": Decimal("8.3"), "temperament": "confident"},
        {"name": "Star Galloper", "age": 7, "base_speed": Decimal("8.1"), "temperament": "calm"},
        
        # Experienced but variable horses
        {"name": "Midnight Express", "age": 8, "base_speed": Decimal("7.8"), "temperament": "unpredictable"},
        {"name": "Golden Arrow", "age": 9, "base_speed": Decimal("7.5"), "temperament": "calm"},
        {"name": "Silver Streak", "age": 10, "base_speed": Decimal("7.2"), "temperament": "aggressive"},
        
        # Veteran horses with character
        {"name": "Old Thunder", "age": 12, "base_speed": Decimal("6.8"), "temperament": "calm"},
        {"name": "Wise Runner", "age": 11, "base_speed": Decimal("7.0"), "temperament": "confident"},
        {"name": "Iron Will", "age": 13, "base_speed": Decimal("6.5"), "temperament": "unpredictable"},
        
        # Wild cards - horses with extreme characteristics
        {"name": "Chaos Theory", "age": 4, "base_speed": Decimal("8.9"), "temperament": "unpredictable"},
        {"name": "Zen Master", "age": 6, "base_speed": Decimal("8.0"), "temperament": "calm"},
        {"name": "Hot Head", "age": 5, "base_speed": Decimal("8.7"), "temperament": "aggressive"},
        
        # Newcomers with potential
        {"name": "Rising Star", "age": 3, "base_speed": Decimal("8.4"), "temperament": "nervous"},
        {"name": "Dream Chaser", "age": 4, "base_speed": Decimal("8.6"), "temperament": "confident"},
        {"name": "Night Fury", "age": 5, "base_speed": Decimal("8.2"), "temperament": "aggressive"},
        
        # Character horses with backstories
        {"name": "Phoenix Rising", "age": 7, "base_speed": Decimal("7.9"), "temperament": "confident"},
        {"name": "Desert Storm", "age": 8, "base_speed": Decimal("7.6"), "temperament": "unpredictable"},
        {"name": "Arctic Wind", "age": 6, "base_speed": Decimal("8.1"), "temperament": "calm"},
        {"name": "Volcanic Ash", "age": 9, "base_speed": Decimal("7.3"), "temperament": "aggressive"},
        
        # The underdogs
        {"name": "Lucky Charm", "age": 10, "base_speed": Decimal("6.9"), "temperament": "nervous"},
        {"name": "Dark Horse", "age": 11, "base_speed": Decimal("7.1"), "temperament": "unpredictable"},
    ]
    
    print("🐎 Starting horse seeding...")
    
    # Clear existing horses
    existing_count = Horse.query.count()
    if existing_count > 0:
        print(f"   Clearing {existing_count} existing horses...")
        Horse.query.delete()
        db.session.commit()
    
    # Add new horses
    horses_created = 0
    for horse_data in horses_data:
        try:
            horse = Horse(**horse_data)
            db.session.add(horse)
            horses_created += 1
        except Exception as e:
            print(f"   ✗ Failed to add {horse_data['name']}: {str(e)}")
    
    try:
        db.session.commit()
        print(f"🎉 Successfully seeded {horses_created} horses!")
        
        # Print summary stats
        print(f"\n📊 Horse Statistics:")
        print(f"   Total horses: {Horse.query.count()}")
        print(f"   Average age: {db.session.query(db.func.avg(Horse.age)).scalar():.1f}")
        print(f"   Average speed: {db.session.query(db.func.avg(Horse.base_speed)).scalar():.1f}")
        
        # Count by temperament
        temperaments = db.session.query(Horse.temperament, db.func.count(Horse.horse_id))\
                                .group_by(Horse.temperament).all()
        print(f"   Temperament distribution:")
        for temp, count in temperaments:
            print(f"     - {temp.title()}: {count}")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error committing horses: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    with app.app_context():
        if seed_horses():
            print("✅ Horse seeding completed successfully!")
        else:
            print("❌ Horse seeding failed!")
            exit(1) 