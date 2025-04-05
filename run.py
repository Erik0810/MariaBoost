import os
from app import app
import sqlite3

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()

def init_db():
    """Initialize database if it doesn't exist"""
    if not os.path.exists(app.config['DATABASE']):
        print("Initializing database...")
        db = sqlite3.connect(app.config['DATABASE'])
        try:
            with open('schema.sql', 'r') as f:
                db.executescript(f.read())
            db.commit()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    else:
        print("Using existing database")

application = app

if __name__ == '__main__':
    print("Starting application...")
    
    # Initialize database if needed
    with app.app_context():
        init_db()
    
    print("Application ready")
    # Run the app in production mode
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

