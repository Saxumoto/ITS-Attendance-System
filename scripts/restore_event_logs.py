import sqlite3
from datetime import datetime

DB_PATH = 'C:/DESKTOP FILES/ITS-Attendance-System/StudentDatabase.db'

def seed_jumpstart_day2():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    today_date = "2026-08-12"
    event = "Jumpstart Day 2"
    
    print(f"Generating full session activity logs for Event: '{event}' and Date: '{today_date}'...")
    
    # 1. Clear any existing event_logs for this event
    c.execute("DELETE FROM event_logs WHERE event_name=?", (event,))
    conn.commit()
    
    # 2. Fetch up to 20 existing student IDs
    c.execute("SELECT studentID FROM studentData LIMIT 20")
    rows = c.fetchall()
    existing_ids = [r[0] for r in rows]
    
    # Add a transferee & walk-in
    c.execute("""
        INSERT OR REPLACE INTO studentData (studentID, firstName, lastName, yearLevel, regType)
        VALUES ('99990201', 'Juan', 'Cruz', '1st Year', 'NEW')
    """)
    c.execute("""
        INSERT OR REPLACE INTO studentData (studentID, firstName, lastName, yearLevel, regType)
        VALUES ('99990202', 'Alex', 'Ramos', '3rd Year', 'TRANSFEREE')
    """)
    conn.commit()
    
    all_participants = existing_ids + ['99990201', '99990202']
    
    total_logs_created = 0
    
    # 1. MORNING TIME IN (20 students)
    for idx, s_id in enumerate(all_participants):
        ts = f"{today_date} 07:35:{idx:02d}"
        c.execute("""
            INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date)
            VALUES (?, 'Morning Time IN', ?, ?, ?)
        """, (s_id, ts, event, today_date))
        total_logs_created += 1
        
    # 2. MORNING TIME OUT (18 students)
    for idx, s_id in enumerate(all_participants[:18]):
        ts = f"{today_date} 12:01:{idx:02d}"
        c.execute("""
            INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date)
            VALUES (?, 'Morning Time OUT', ?, ?, ?)
        """, (s_id, ts, event, today_date))
        total_logs_created += 1

    # 3. AFTERNOON TIME IN (18 students)
    for idx, s_id in enumerate(all_participants[:18]):
        ts = f"{today_date} 13:05:{idx:02d}"
        c.execute("""
            INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date)
            VALUES (?, 'Afternoon Time IN', ?, ?, ?)
        """, (s_id, ts, event, today_date))
        total_logs_created += 1

    # 4. AFTERNOON TIME OUT (18 students)
    for idx, s_id in enumerate(all_participants[:18]):
        ts = f"{today_date} 16:45:{idx:02d}"
        c.execute("""
            INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date)
            VALUES (?, 'Afternoon Time OUT', ?, ?, ?)
        """, (s_id, ts, event, today_date))
        total_logs_created += 1

    conn.commit()
    conn.close()
    
    print(f"\n[SUCCESS] Generated {total_logs_created} full event attendance logs for '{event}'!")

if __name__ == "__main__":
    seed_jumpstart_day2()
