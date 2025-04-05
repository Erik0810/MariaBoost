import os
from app import app
import sqlite3


if __name__ == '__main__':
    print("Starting application...")
    
    
    print("Application ready")
    # Run the app in production mode
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()