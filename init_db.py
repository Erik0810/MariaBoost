import os
import sqlite3
from app import app

def init_db():
    """Initialize database if it doesn't exist"""
    db_path = app.config['DATABASE']
    create_db = not os.path.exists(db_path)
    
    if create_db:
        print(f"Creating new database at {db_path}")
        try:
            with sqlite3.connect(db_path) as db:
                with open('schema.sql', 'r') as f:
                    db.executescript(f.read())
                db.commit()
                print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
    
    return create_db

if __name__ == '__main__':
    init_db()