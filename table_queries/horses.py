import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Horse

def query_horses():
    """Execute SELECT * FROM horses equivalent query"""
    with app.app_context():
        print("🐎 HORSES TABLE - SELECT * FROM horses")
        print("=" * 50)
        
        horses = Horse.query.all()
        
        if not horses:
            print("No horses found in the database.")
            return
        
        print(f"Found {len(horses)} horses:\n")
        
        for horse in horses:
            print(f"Horse ID: {horse.horse_id}")
            print(f"Name: {horse.name}")
            print(f"Age: {horse.age}")
            print(f"Base Speed: {horse.base_speed}")
            print(f"Temperament: {horse.temperament}")
            print("-" * 30)

if __name__ == "__main__":
    query_horses() 