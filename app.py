import sqlite3
import os
from flask import Flask, render_template, jsonify, request, g
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(app.root_path, 'workouts.db')

def init_db():
    print("Initializing database...")
    with app.app_context():
        if os.path.exists(app.config['DATABASE']):
            os.remove(app.config['DATABASE'])
        
        db = sqlite3.connect(app.config['DATABASE'])
        try:
            with open('schema.sql', 'r') as f:
                db.executescript(f.read())
            db.commit()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            db.close()

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

def get_week_dates(week_str):
    year, week = map(int, week_str.split('-'))
    first_day = datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w')
    return [first_day + timedelta(days=i) for i in range(7)]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/workouts')
def get_workouts():
    week = request.args.get('week')
    if not week:
        return jsonify({'error': 'Week parameter is required'}), 400

    dates = get_week_dates(week)
    db = get_db()
    workouts = {}
    
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        cur = db.execute(
            'SELECT completed, message FROM workouts WHERE date = ?',
            (date_str,)
        )
        row = cur.fetchone()
        if row:
            workouts[date_str] = {
                'completed': bool(row['completed']),
                'message': row['message']
            }
        else:
            workouts[date_str] = {
                'completed': False,
                'message': None
            }

    return jsonify({
        'dates': [d.strftime('%Y-%m-%d') for d in dates],
        'workouts': workouts
    })

@app.route('/toggle_workout', methods=['POST'])
def toggle_workout():
    data = request.json
    date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    message = data.get('message', '')  # Get message if provided
    
    db = get_db()
    cur = db.execute(
        'SELECT completed FROM workouts WHERE date = ?',
        (date.strftime('%Y-%m-%d'),)
    )
    row = cur.fetchone()
    
    if row is None:
        db.execute(
            'INSERT INTO workouts (date, completed, message) VALUES (?, ?, ?)',
            (date.strftime('%Y-%m-%d'), True, message)
        )
    else:
        new_status = not bool(row['completed'])
        db.execute(
            'UPDATE workouts SET completed = ?, message = ? WHERE date = ?',
            (new_status, message, date.strftime('%Y-%m-%d'))
        )
    
    db.commit()
    return jsonify({'success': True})

@app.route('/save_message', methods=['POST'])
def save_message():
    data = request.json
    date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    message = data['message']
    
    db = get_db()
    cur = db.execute(
        'SELECT id FROM workouts WHERE date = ?',
        (date.strftime('%Y-%m-%d'),)
    )
    row = cur.fetchone()
    
    if row is None:
        db.execute(
            'INSERT INTO workouts (date, message) VALUES (?, ?)',
            (date.strftime('%Y-%m-%d'), message)
        )
    else:
        db.execute(
            'UPDATE workouts SET message = ? WHERE date = ?',
            (message, date.strftime('%Y-%m-%d'))
        )
    
    db.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    print("Starting application...")
    init_db()  # Always initialize the database on startup
    app.run(debug=True)