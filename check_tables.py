import sqlite3
import os

def check_tables():
    # Connect to the database
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("Tables in the database:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Look for expertise-related tables
    expertise_tables = [t[0] for t in tables if 'expert' in t[0].lower()]
    if expertise_tables:
        print("\nExpertise-related tables:")
        for table in expertise_tables:
            print(f"- {table}")
            
            # Show table schema
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print("  Columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]}), {'NOT NULL' if col[3] else 'NULL'}")
    
    conn.close()

if __name__ == "__main__":
    check_tables()