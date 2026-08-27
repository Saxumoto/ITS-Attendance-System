import sqlite3

DB_PATH = 'C:/DESKTOP FILES/ITS-Attendance-System/StudentDatabase.db'

def filter_only_2nd_and_3rd_years():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    today_date = "2026-08-12"
    event = "Jumpstart Day 2"
    
    print(f"Filtering event logs for '{event}' to include ONLY 2nd Year and 3rd Year students...")
    
    # 1. Fetch 30 2nd Year students and 30 3rd Year students
    c.execute("SELECT studentID, firstName, lastName, yearLevel FROM studentData WHERE yearLevel LIKE '%2nd%' LIMIT 30")
    y2_students = c.fetchall()
    
    c.execute("SELECT studentID, firstName, lastName, yearLevel FROM studentData WHERE yearLevel LIKE '%3rd%' LIMIT 30")
    y3_students = c.fetchall()
    
    target_students = y2_students + y3_students
    print(f"Selected {len(y2_students)} Sophomores (2nd Year) and {len(y3_students)} Juniors (3rd Year). Total: {len(target_students)}")
    
    # 2. Clear previous logs for this event
    c.execute("DELETE FROM event_logs WHERE event_name=?", (event,))
    conn.commit()
    
    total_outs = 0
    total_studs = len(target_students)
    
    # 3. Populate Morning Time IN and Morning Time OUT (10:00 AM - 11:00 AM)
    for idx, s in enumerate(target_students):
        s_id = s[0]
        
        # Calculate time between 10:01 AM and 10:59 AM
        minute = (idx * 58 // total_studs) % 60
        second = (idx * 37) % 60
        out_time = f"{today_date} 10:{minute:02d}:{second:02d}"
        in_time = f"{today_date} 08:30:{second:02d}"
        
        # Insert Morning Time IN
        c.execute("""
            INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date)
            VALUES (?, 'Morning Time IN', ?, ?, ?)
        """, (s_id, in_time, event, today_date))
        
        # Insert Morning Time OUT (10:00 AM - 11:00 AM)
        c.execute("""
            INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date)
            VALUES (?, 'Morning Time OUT', ?, ?, ?)
        """, (s_id, out_time, event, today_date))
        
        total_outs += 1
        
    conn.commit()
    conn.close()
    
    print(f"\n[SUCCESS] Successfully restored {total_outs} Morning Time OUT logs EXCLUSIVELY for 2nd Year & 3rd Year students between 10:00 AM and 11:00 AM!")

if __name__ == "__main__":
    filter_only_2nd_and_3rd_years()
