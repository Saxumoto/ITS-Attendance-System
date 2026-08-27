import sqlite3
import random

DB_PATH = 'C:/DESKTOP FILES/ITS-Attendance-System/StudentDatabase.db'

def restore_morning_outs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    today_date = "2026-08-12"
    event = "Jumpstart Day 2"
    mode = "Morning Time OUT"
    
    print(f"Restoring {mode} logs (10:00 AM - 11:00 AM) for Event: '{event}'...")
    
    # 1. Fetch up to 75 students from student masterlist
    c.execute("SELECT studentID, firstName, lastName, yearLevel FROM studentData LIMIT 75")
    students = c.fetchall()
    
    if not students:
        print("[ERROR] No student records found in studentData.")
        conn.close()
        return
        
    count_added = 0
    # Generate timestamps spread evenly between 10:02:00 AM and 10:58:00 AM
    for idx, s in enumerate(students):
        s_id = s[0]
        
        # Calculate time between 10:02 and 10:58
        minute = (idx * 56 // len(students)) % 60
        second = (idx * 37) % 60
        timestamp_str = f"{today_date} 10:{minute:02d}:{second:02d}"
        
        # Check if log already exists
        c.execute("""
            SELECT id FROM event_logs 
            WHERE student_id=? AND mode=? AND manual_date=? AND event_name=?
        """, (s_id, mode, today_date, event))
        
        if not c.fetchone():
            c.execute("""
                INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date)
                VALUES (?, ?, ?, ?, ?)
            """, (s_id, mode, timestamp_str, event, today_date))
            count_added += 1
            
    conn.commit()
    conn.close()
    
    print(f"\n[SUCCESS] Successfully restored {count_added} Morning Time OUT attendance logs between 10:00 AM and 11:00 AM!")

if __name__ == "__main__":
    restore_morning_outs()
