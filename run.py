import os
from app import app, get_db
from datetime import datetime, timedelta
import sqlite3

def init_dev_db():
    """Initialize fresh database for development"""
    print("\n=== Database Initialization ===")
    print("Initializing fresh development database...")
    
    # Always delete existing database
    if os.path.exists(app.config['DATABASE']):
        os.remove(app.config['DATABASE'])
        print("✓ Removed existing database")
    
    db = sqlite3.connect(app.config['DATABASE'])
    try:
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()
        print("✓ Created fresh database")
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        db.rollback()
    finally:
        db.close()

def setup_dev_data():
    """Add test data for development"""
    print("\n=== Setting Up Test Data ===")
    
    # Get today and previous days
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)
    
    # Format dates
    test_dates = [
        day_before.strftime('%Y-%m-%d'),
        yesterday.strftime('%Y-%m-%d')
    ]
    
    print(f"Today's date: {today.strftime('%Y-%m-%d')}")
    print(f"Test dates: {test_dates}")
    
    # Get database connection
    db = get_db()
    
    try:
        # First, verify the database is empty or clear existing data
        cur = db.execute('SELECT COUNT(*) FROM workouts')
        count = cur.fetchone()[0]
        print(f"Current workout entries: {count}")
        
        # Clear any existing data for our test dates
        for date in test_dates:
            db.execute('DELETE FROM workouts WHERE date = ?', (date,))
        db.commit()
        print("✓ Cleared existing test data")
        
        # Add completed workouts for previous days
        for date in test_dates:
            print(f"\nAdding workout for {date}:")
            db.execute(
                'INSERT INTO workouts (date, completed, message) VALUES (?, ?, ?)',
                (date, True, f'Test workout for {date}')
            )
            db.commit()
            print("✓ Inserted workout record")
            
            # Verify the insertion
            row = db.execute(
                'SELECT date, completed, message FROM workouts WHERE date = ?', 
                (date,)
            ).fetchone()
            
            if row:
                print(f"✓ Verified: date={row[0]}, completed={bool(row[1])}, message={row[2]}")
            else:
                print(f"✗ Failed to find workout for {date}")
        
        # Show all workouts in database
        print("\n=== Current Database State ===")
        cur = db.execute('SELECT date, completed, message FROM workouts ORDER BY date')
        rows = cur.fetchall()
        for row in rows:
            print(f"Date: {row[0]}, Completed: {bool(row[1])}, Message: {row[2]}")
            
    except Exception as e:
        print(f"✗ Error setting up development data: {e}")
        db.rollback()

if __name__ == '__main__':
    print("\n=== Starting Development Server ===")
    print("Creating fresh database with test data...")
    
    # Initialize fresh database and add test data
    with app.app_context():
        init_dev_db()
        setup_dev_data()
    
    print("\n=== Server Ready ===")
    # Run the app
    app.run(debug=True)