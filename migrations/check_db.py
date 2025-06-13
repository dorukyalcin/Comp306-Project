from sqlalchemy import create_engine, text
import os

# Get database URL from environment or use default
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/casino_db')

def check_db():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Check table structure
    with engine.connect() as connection:
        # Get all columns in users table
        result = connection.execute(text("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        
        print("\nUsers table structure:")
        print("----------------------")
        for row in result:
            print(f"Column: {row[0]}")
            print(f"Type: {row[1]}")
            print(f"Default: {row[2]}")
            print(f"Nullable: {row[3]}")
            print("----------------------")

if __name__ == '__main__':
    check_db() 