DROP TABLE IF EXISTS workouts;
CREATE TABLE workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT 0,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workouts_date ON workouts(date);