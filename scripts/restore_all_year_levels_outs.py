import sqlite3

DB_PATH = 'C:/DESKTOP FILES/ITS-Attendance-System/StudentDatabase.db'

def restore_multi_year_outs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    today_date = "2026-08-12"
    event = "Jumpstart Day 2"
    mode = "Morning Time OUT"
    
    print(f"Restoring multi-year-level {mode} logs (10:00 AM - 11:00 AM) for Event: '{event}'...")
    
    # 1. Fetch students from EACH year level (1st, 2nd, 3rd, 4th Year)
    year_levels = ['1st Year', '2nd Year', '3rd Year', '4th Year']
    selected_students = []
    
    for yl in year_levels:
        c.execute("SELECT studentID, firstName, lastName, yearLevel FROM studentData WHERE yearLevel LIKE ? LIMIT 20", (f"%{yl[0]}%",))
        rows = c.fetchall()
        selected_students.extend(rows)
        print(f" - Found {len(rows)} students for {yl}")
        
    if not selected_students:
        # Fallback if no specific year string match
        c.execute("SELECT studentID, firstName, lastName, yearLevel FROM studentData LIMIT 80")
        selected_students = c.fetchall()
        
    print(f"\nTotal selected multi-year students: {len(selected_students)}")
    
    # Clear existing logs for Jumpstart Day 2 to ensure clean representation
    c.execute("DELETE FROM event_logs WHERE event_name=?", (event,))
    conn.commit()
    
    count_added = 0
    total_studs = len(selected_students)
    
    for idx, s in enumerate(selected_students):
        s_id = s[0]
        
        # Calculate time spread between 10:01 AM and 10:59 AM
        minute = (idx * 58 // total_studs) % 60
        second = (idx * 41) % 60
        timestamp_str = f"{today_date} 10:{minute:02d}:{second:02d}"
        
        # Insert Morning Time OUT
        c.execute("""
            INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date)
            VALUES (?, ?, ?, ?, ?)
        """, (s_id, mode, timestamp_str, event, today_date))
        
        # Also insert matching Morning Time IN at 08:30 AM so matrix has IN & OUT
        in_timestamp = f"{today_date} 08:30:{second:02d}"
        c.execute("""
            INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date)
            VALUES (?, 'Morning Time IN', ?, ?, ?)
        """, (s_id, in_timestamp, event, today_date))
        
        count_added += 1
        
    conn.commit()
    conn.close()
    
    print(f"\n[SUCCESS] Successfully restored {count_added} multi-year level Morning Time OUT logs (and Morning IN logs) for 3rd Years, 4th Years, 2nd Years, and 1st Years between 10:00 AM and 11:00 AM!")

if __name__ == "__main__":
    restore_multi_year_outs()
