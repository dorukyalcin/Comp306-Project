import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text

def rename_id_column():
    with app.app_context():
        # Check if the column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'id'
        """))
        
        if result.fetchone():
            # Rename the column
            db.session.execute(text("""
                ALTER TABLE users 
                RENAME COLUMN id TO user_id
            """))
            db.session.commit()
            print("Successfully renamed 'id' column to 'user_id'")
        else:
            print("Column 'id' not found in users table")

if __name__ == '__main__':
    rename_id_column() 