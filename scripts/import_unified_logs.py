import csv
import sqlite3
import os

DB_PATH = r'C:\DESKTOP FILES\ITS-Attendance-System\release\ITS Attendance System\StudentDatabase.db'
UNIFIED_FOLDER = r'C:\DESKTOP FILES\ITS-Attendance-System\UNIFIED_FILES\UNIFIED FILES'
DAY1_CSV = os.path.join(UNIFIED_FOLDER, 'Day_1_Unified_Attendance.csv')
DAY2_CSV = os.path.join(UNIFIED_FOLDER, 'Day_2_Unified_Attendance.csv')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all student IDs currently in studentData
cursor.execute("SELECT studentID FROM studentData")
valid_students = set(r[0] for r in cursor.fetchall())

# Known typo corrections to ensure clean logs
TYPO_CORRECTIONS = {
    '5949428': '59849428',
    '5983434': '59343434',
    '58944461': '59844461',
    '598 9211': '59849211',
    '5984926': '59849726',
    'TEMP-2026-1310': '59835962',
}

MODES = [
    ('Morning Time IN', 'Morning IN'),
    ('Morning Time OUT', 'Morning OUT'),
    ('Afternoon Time IN', 'Afternoon IN'),
    ('Afternoon Time OUT', 'Afternoon OUT')
]

def import_day(csv_path, event_name, manual_date):
    print(f"\n--- Importing {event_name} ({manual_date}) ---")
    inserted = 0
    skipped_existing = 0
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_id = row['Student ID'].strip()
            sid = TYPO_CORRECTIONS.get(raw_id, raw_id)
            if sid not in valid_students:
                continue
            
            for db_mode, col_name in MODES:
                time_val = row.get(col_name, '').strip()
                if time_val and time_val != '-':
                    timestamp = f"{manual_date} {time_val}"
                    # Check if already in event_logs
                    cursor.execute("""
                        SELECT id FROM event_logs 
                        WHERE student_id=? AND mode=? AND manual_date=? AND event_name=?
                    """, (sid, db_mode, manual_date, event_name))
                    if cursor.fetchone():
                        skipped_existing += 1
                    else:
                        cursor.execute("""
                            INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date)
                            VALUES (?, ?, ?, ?, ?)
                        """, (sid, db_mode, timestamp, event_name, manual_date))
                        inserted += 1
    print(f"Inserted: {inserted}, Skipped already logged: {skipped_existing}")

# Also check existing BSIT ORIENTATION logs:
# The 68 logs already in DB were event_name='BSIT ORIENTATION', date='2026-09-12'
# We will use event_name='BSIT ORIENTATION DAY 1' for Day 1 and 'BSIT ORIENTATION DAY 2' for Day 2
# Or we can update the existing 68 logs to 'BSIT ORIENTATION DAY 1' so they unify cleanly.
cursor.execute("UPDATE event_logs SET event_name='BSIT ORIENTATION DAY 1' WHERE event_name='BSIT ORIENTATION'")

import_day(DAY1_CSV, 'BSIT ORIENTATION DAY 1', '2026-09-12')
import_day(DAY2_CSV, 'BSIT ORIENTATION DAY 2', '2026-09-13')

conn.commit()

cursor.execute("SELECT event_name, manual_date, COUNT(*) FROM event_logs GROUP BY event_name, manual_date")
print("\n=== UPDATED EVENT LOGS SUMMARY ===")
for r in cursor.fetchall():
    print(r)

conn.close()
