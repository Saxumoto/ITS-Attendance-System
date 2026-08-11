-- Enable foreign key support in SQLite
PRAGMA foreign_keys = ON;

-- Students table containing student details
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    year_level TEXT NOT NULL,
    course TEXT NOT NULL DEFAULT 'BSIT',
    status TEXT NOT NULL DEFAULT 'ACTIVE'
);

-- Events table containing registered events
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    event_date TEXT NOT NULL, -- YYYY-MM-DD
    description TEXT,
    UNIQUE(name, event_date)
);

-- Attendance logs table
CREATE TABLE IF NOT EXISTS attendance_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    event_id INTEGER NOT NULL,
    scan_mode TEXT NOT NULL, -- TIME_IN, TIME_OUT, LATE
    timestamp TEXT NOT NULL, -- YYYY-MM-DD HH:MM:SS
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE
);

-- Indices for optimal scanning performance
CREATE INDEX IF NOT EXISTS idx_students_id ON students(student_id);
CREATE INDEX IF NOT EXISTS idx_logs_student_event ON attendance_logs(student_id, event_id);
