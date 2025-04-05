import sqlite3
import os
from flask import Flask, render_template, jsonify, request, g
from datetime import datetime, timedelta
from prizes import prize_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE'] = os.path.join(app.root_path, os.getenv('DATABASE', 'workouts.db'))


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.teardown_appcontext
def teardown_db(exception):
    close_db()

def get_week_dates():
    """Get dates for the current week (Monday to Sunday)"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    monday = today - timedelta(days=today.weekday())  # Get Monday of current week
    
    # Return dates as formatted strings
    date_strs = [(monday + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    
    print(f"\n=== Week Dates ===")
    print(f"Today: {today.strftime('%Y-%m-%d')}")
    print(f"Week dates: {date_strs}")
    return date_strs

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/workouts')
def get_workouts():
    print("\n=== Fetching Workouts ===")
    date_strs = get_week_dates()  # Now returns strings directly
    db = get_db()
    workouts = {}
    
    # Format placeholders for SQL query
    placeholders = ','.join(['?' for _ in date_strs])
    
    # Get all workouts for the week at once
    query = f'SELECT date, completed, message FROM workouts WHERE date IN ({placeholders})'
    print(f"\nExecuting query: {query}")
    print(f"With dates: {date_strs}")
    
    cur = db.execute(query, date_strs)
    rows = cur.fetchall()
    
    # Convert to dict for easy lookup
    workout_dict = {}
    for row in rows:
        date_str = str(row['date'])  # Should already be a string from SQLite
        workout_dict[date_str] = {
            'completed': bool(row['completed']),
            'message': row['message']
        }
        print(f"\nStored in dict - Date: {date_str}, Data: {workout_dict[date_str]}")
    
    print(f"\nFound {len(rows)} workout records:")
    for row in rows:
        print(f"Date: {row['date']}, Completed: {bool(row['completed'])}, Message: {row['message']}")
    
    # Build response for each date
    print("\nBuilding response data:")
    for date_str in date_strs:
        if date_str in workout_dict:
            print(f"Date {date_str}: Found workout record (completed={workout_dict[date_str]['completed']})")
            workouts[date_str] = workout_dict[date_str]
        else:
            print(f"Date {date_str}: No workout record found")
            workouts[date_str] = {
                'completed': False,
                'message': None
            }

    completed_count = sum(1 for w in workouts.values() if w['completed'])
    print(f"\nTotal completed workouts: {completed_count}")
    print("\nFinal workouts data:")
    for date, data in workouts.items():
        print(f"Date: {date}, Completed: {data['completed']}, Message: {data['message']}")

    response_data = {
        'dates': date_strs,
        'workouts': workouts,
        'prize': "❓"
    }
    print(f"\nSending response")
    return jsonify(response_data)

@app.route('/toggle_workout', methods=['POST'])
def toggle_workout():
    data = request.json
    date = data['date']  # Already a string in YYYY-MM-DD format
    message = data.get('message', '')
    
    print(f"\n=== Toggling Workout ===")
    print(f"Date: {date}")
    
    db = get_db()
    cur = db.execute('SELECT completed FROM workouts WHERE date = ?', (date,))
    row = cur.fetchone()
    
    if row is None:
        print("No existing workout found, creating new record")
        db.execute(
            'INSERT INTO workouts (date, completed, message) VALUES (?, ?, ?)',
            (date, True, message)
        )
    else:
        new_status = not bool(row['completed'])
        print(f"Updating existing workout, new status: {new_status}")
        db.execute(
            'UPDATE workouts SET completed = ?, message = ? WHERE date = ?',
            (new_status, message, date)
        )
    
    db.commit()
    
    # Verify the change
    cur = db.execute('SELECT completed FROM workouts WHERE date = ?', (date,))
    row = cur.fetchone()
    print(f"Verified status: {bool(row['completed']) if row else 'Not found'}")
    
    return jsonify({'success': True})

@app.route('/save_message', methods=['POST'])
def save_message():
    data = request.json
    date = data['date']  # Already a string in YYYY-MM-DD format
    message = data['message']
    
    db = get_db()
    cur = db.execute('SELECT id FROM workouts WHERE date = ?', (date,))
    row = cur.fetchone()
    
    if row is None:
        db.execute(
            'INSERT INTO workouts (date, message) VALUES (?, ?)',
            (date, message)
        )
    else:
        db.execute(
            'UPDATE workouts SET message = ? WHERE date = ?',
            (message, date)
        )
    
    db.commit()
    return jsonify({'success': True})

@app.route('/prize')
def get_current_prize():
    current_prize = prize_manager.get_prize()
    if current_prize:
        return jsonify({
            'name': current_prize.name,
            'description': current_prize.description,
            'image': current_prize.image
        })
    return jsonify({'error': 'No prize found for current week'}), 404

if __name__ == '__main__':
    app.run(debug=True)