from sqlalchemy import create_engine, text
import os
import sys

# Get database URL from environment or use default
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/casino_db')

def migrate():
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Check if column exists
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'profile_picture'
            """))
            
            if not result.fetchone():
                print("Adding profile_picture column...")
                connection.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN profile_picture VARCHAR(255) DEFAULT 'default_profile.png'
                """))
                connection.commit()
                print("Column added successfully!")
            else:
                print("Column already exists!")
                
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    migrate() 