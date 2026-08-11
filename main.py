import eel
import sqlite3
from datetime import datetime
import os
import sys
import csv
from tkinter import filedialog, Tk
import pandas as pd

# --- CONFIGURATION ---
DB_NAME = 'StudentDatabase.db'

def get_db_path():
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(app_dir, DB_NAME)

def setup_database():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Core Tables Check
    c.execute('''CREATE TABLE IF NOT EXISTS event_logs 
                    (id INTEGER PRIMARY KEY, student_id TEXT, mode TEXT, 
                     timestamp TEXT, event_name TEXT, manual_date TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS closed_periods 
                    (event_name TEXT, manual_date TEXT, mode TEXT, 
                     PRIMARY KEY (event_name, manual_date, mode))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS studentData 
                    (id INTEGER PRIMARY KEY, studentID TEXT UNIQUE, 
                     firstName TEXT, lastName TEXT, yearLevel TEXT, regType TEXT DEFAULT 'EXISTING')''')
                     
    # Ensure column regType exists in studentData (in case table was created with old schema)
    try:
        c.execute("ALTER TABLE studentData ADD COLUMN regType TEXT DEFAULT 'EXISTING'")
    except:
        pass
        
    try:
        c.execute("ALTER TABLE event_logs ADD COLUMN manual_date TEXT")
    except:
        pass
        
    conn.commit()
    conn.close()

# Initialize database schemas
setup_database()

# Set up Eel web directory
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    web_dir = os.path.join(sys._MEIPASS, 'web')
else:
    web_dir = 'web'

eel.init(web_dir)


@eel.expose
def get_initial_data(date, event):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Fetch student master list
    c.execute("SELECT studentID, firstName, lastName, yearLevel, regType FROM studentData")
    students_rows = c.fetchall()
    students_list = []
    for r in students_rows:
        students_list.append({
            "studentID": r[0],
            "firstName": r[1],
            "lastName": r[2],
            "yearLevel": r[3],
            "regType": r[4]
        })
        
    # Fetch event logs matching parameters
    c.execute("""
        SELECT student_id, mode, timestamp FROM event_logs 
        WHERE manual_date=? AND event_name=? 
        ORDER BY timestamp DESC
    """, (date, event))
    logs_rows = c.fetchall()
    logs_list = []
    for r in logs_rows:
        logs_list.append({
            "studentID": r[0],
            "mode": r[1],
            "timestamp": r[2]
        })
        
    conn.close()
    return {"students": students_list, "logs": logs_list}

def log_attendance_helper(c, student_id, first_name, last_name, year_level, mode, date, event):
    # Check if already logged for this mode session
    c.execute("SELECT id FROM event_logs WHERE student_id=? AND mode=? AND manual_date=? AND event_name=?", (student_id, mode, date, event))
    if c.fetchone(): 
        return {
            "status": "already_logged", 
            "student": {
                "studentID": student_id,
                "firstName": first_name,
                "lastName": last_name,
                "yearLevel": year_level
            }
        }
    
    # Save the log
    time_now_str = f"{date} {datetime.now().strftime('%H:%M:%S')}"
    c.execute("INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date) VALUES (?,?,?,?,?)", 
               (student_id, mode, time_now_str, event, date))
    
    return {
        "status": "success", 
        "student": {
            "studentID": student_id,
            "firstName": first_name,
            "lastName": last_name,
            "yearLevel": year_level
        }
    }

@eel.expose
def process_scan_py(query, date, event, mode, use_cutoff, cutoff_time):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Check if period is locked
    c.execute("SELECT 1 FROM closed_periods WHERE event_name=? AND manual_date=? AND mode=?", (event, date, mode))
    if c.fetchone():
        conn.close()
        return {"status": "blocked_locked"}

    # Check time limit cut-off limit
    if use_cutoff and cutoff_time:
        try:
            now = datetime.now().time()
            limit_time = datetime.strptime(cutoff_time, "%H:%M").time()
            if now > limit_time:
                conn.close()
                return {"status": "blocked_cutoff"}
        except Exception as e:
            print("Time cut-off limit error:", e)
    
    # 1. Check exact Student ID
    c.execute("SELECT studentID, firstName, lastName, yearLevel, regType FROM studentData WHERE studentID=?", (query,))
    match = c.fetchone()
    
    if match:
        res = log_attendance_helper(c, match[0], match[1], match[2], match[3], mode, date, event)
        conn.commit()
        conn.close()
        return res
    else:
        # 2. Match by Name Substrings
        query_str = f"%{query}%"
        c.execute("""
            SELECT studentID, firstName, lastName, yearLevel, regType 
            FROM studentData 
            WHERE lastName LIKE ? OR firstName LIKE ?
        """, (query_str, query_str))
        rows = c.fetchall()
        
        candidates = []
        for r in rows:
            candidates.append({
                "studentID": r[0],
                "firstName": r[1],
                "lastName": r[2],
                "yearLevel": r[3],
                "regType": r[4]
            })
            
        conn.close()
        
        if len(candidates) == 1:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            cand = candidates[0]
            res = log_attendance_helper(c, cand['studentID'], cand['firstName'], cand['lastName'], cand['yearLevel'], mode, date, event)
            conn.commit()
            conn.close()
            return res
        elif len(candidates) > 1:
            return {"status": "multiple_matches", "candidates": candidates}
        else:
            # Check if input looks like ID/Barcode
            is_id_like = query.isdigit() or (any(char.isdigit() for char in query) and len(query) >= 5)
            if is_id_like:
                return {"status": "id_not_found", "student_id": query}
            else:
                return {"status": "not_found"}

@eel.expose
def register_student_py(student_id, first_name, last_name, year_level, reg_type, mode, date, event):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check if period is locked
    c.execute("SELECT 1 FROM closed_periods WHERE event_name=? AND manual_date=? AND mode=?", (event, date, mode))
    if c.fetchone():
        conn.close()
        return {"status": "error", "message": f"Cannot register. The period '{mode}' is locked."}
        
    # Check if studentID exists
    c.execute("SELECT id FROM studentData WHERE studentID=?", (student_id,))
    if c.fetchone():
        conn.close()
        return {"status": "error", "message": f"Student ID '{student_id}' is already registered."}
        
    try:
        # Insert student
        c.execute("""
            INSERT INTO studentData (studentID, firstName, lastName, yearLevel, regType) 
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, first_name.title(), last_name.title(), year_level, reg_type))
        
        # Log attendance
        res = log_attendance_helper(c, student_id, first_name, last_name, year_level, mode, date, event)
        conn.commit()
        conn.close()
        return res
    except Exception as e:
        conn.close()
        return {"status": "error", "message": f"Registration failed:\n{e}"}

@eel.expose
def log_unregistered_py(student_id, mode, date, event):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check if period is locked
    c.execute("SELECT 1 FROM closed_periods WHERE event_name=? AND manual_date=? AND mode=?", (event, date, mode))
    if c.fetchone():
        conn.close()
        return {"status": "error", "message": f"Cannot log unregistered scan. The period '{mode}' is locked."}
        
    # Log directly
    time_now_str = f"{date} {datetime.now().strftime('%H:%M:%S')}"
    c.execute("INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date) VALUES (?,?,?,?,?)", 
               (student_id, mode, time_now_str, event, date))
    conn.commit()
    conn.close()
    return {"status": "success"}

@eel.expose
def delete_logs_py(logs_to_delete, date, event):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    deleted_count = 0
    try:
        for item in logs_to_delete:
            s_id = item['student_id']
            mode = item['mode']
            ts = item['timestamp']
            
            c.execute("""
                DELETE FROM event_logs 
                WHERE student_id=? AND manual_date=? AND event_name=? AND mode=? AND timestamp LIKE ?
            """, (s_id, date, event, mode, f"%{ts}%"))
            deleted_count += c.rowcount
            
        conn.commit()
        conn.close()
        return {"status": "success", "count": deleted_count}
    except Exception as e:
        conn.close()
        return {"status": "error", "message": str(e)}

@eel.expose
def clear_all_logs_py(date, event):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute("DELETE FROM event_logs WHERE manual_date=? AND event_name=?", (date, event))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        conn.close()
        return {"status": "error", "message": str(e)}

@eel.expose
def export_logs_csv_py(date, event):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # 1. Fetch only student IDs who logged at least once today for this event
        c.execute("""
            SELECT DISTINCT student_id FROM event_logs 
            WHERE manual_date=? AND event_name=?
        """, (date, event))
        active_student_ids = [row[0] for row in c.fetchall()]
        
        if not active_student_ids:
            conn.close()
            return {"status": "error", "message": "No attendance records found for this event to export."}
            
        # 2. Fetch profile info for each active student
        students_list = []
        for s_id in active_student_ids:
            c.execute("SELECT studentID, firstName, lastName, yearLevel, regType FROM studentData WHERE studentID=?", (s_id,))
            r = c.fetchone()
            if r:
                students_list.append(list(r))
            else:
                # Unregistered barcode scan
                students_list.append([s_id, "BARCODE", "UNREGISTERED", "N/A", "NOT FOUND"])
                
        # Sort by Last Name (the 3rd element: lastName is index 2)
        students_list.sort(key=lambda x: x[2].lower())

        # 3. Consolidate Matrix
        headers = ["Student ID", "Full Name", "Year Level", "Reg Type", "Morning IN", "Morning OUT", "Afternoon IN", "Afternoon OUT"]
        export_list = [headers]
        modes = ["Morning Time IN", "Morning Time OUT", "Afternoon Time IN", "Afternoon Time OUT"]
        
        for s in students_list:
            s_id = s[0]
            fname = f"{s[2].upper()}, {s[1]}"
            year = s[3]
            reg_type = s[4] if len(s) > 4 and s[4] else "EXISTING"
            
            timestamps = []
            for m in modes:
                c.execute("""
                    SELECT timestamp FROM event_logs 
                    WHERE student_id=? AND manual_date=? AND event_name=? AND mode=?
                """, (s_id, date, event, m))
                row = c.fetchone()
                if row:
                    ts = row[0]
                    time_part = ts.split(' ')[1] if ' ' in ts else ts
                    timestamps.append(time_part)
                else:
                    timestamps.append("ABSENT")
                    
            row_data = [s_id, fname, year, reg_type] + timestamps
            export_list.append(row_data)
            
        conn.close()
        
        # 4. Open Windows Save Dialog via hidden Tkinter GUI
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        clean_evt = "".join([char if char.isalnum() else "_" for char in event])
        default_name = f"{clean_evt}_{date}_Consolidated_Attendance.xlsx"
        
        fn = filedialog.asksaveasfilename(initialfile=default_name, defaultextension=".xlsx",
                                           filetypes=[("Excel spreadsheets", "*.xlsx"), ("All files", "*.*")])
        root.destroy()
        
        if fn:
            # Convert to DataFrame
            df = pd.DataFrame(export_list[1:], columns=export_list[0])
            
            # Save using Pandas & openpyxl
            with pd.ExcelWriter(fn, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Attendance Logs')
                
                # Get the worksheet to apply auto-fit
                workbook = writer.book
                worksheet = writer.sheets['Attendance Logs']
                
                # Auto-fit column widths
                for col in worksheet.columns:
                    max_len = 0
                    col_letter = col[0].column_letter # openpyxl column letter (e.g. 'A')
                    for cell in col:
                        val_str = str(cell.value or '')
                        if len(val_str) > max_len:
                            max_len = len(val_str)
                    # Add 4 extra padding spaces for clean reading room
                    worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)
                    
            return {"status": "success", "message": f"Consolidated Export Complete!\nSaved attendance matrix for {len(students_list)} students."}
        else:
            return {"status": "cancelled"}
            
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return {"status": "error", "message": f"Failed to save file:\n{e}"}

@eel.expose
def check_period_lock_py(date, event, mode):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT 1 FROM closed_periods WHERE event_name=? AND manual_date=? AND mode=?", (event, date, mode))
    locked = c.fetchone() is not None
    conn.close()
    return locked

@eel.expose
def toggle_period_lock_py(date, event, mode):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT 1 FROM closed_periods WHERE event_name=? AND manual_date=? AND mode=?", (event, date, mode))
    is_locked = c.fetchone() is not None
    
    if is_locked:
        c.execute("DELETE FROM closed_periods WHERE event_name=? AND manual_date=? AND mode=?", (event, date, mode))
        status = "unlocked"
    else:
        c.execute("INSERT INTO closed_periods (event_name, manual_date, mode) VALUES (?,?,?)", (event, date, mode))
        status = "locked"
        
    conn.commit()
    conn.close()
    return {"status": "success", "lock_status": status}

# Start Eel App
if __name__ == "__main__":
    # eel.start() runs a local web server and launches chromium in app mode.
    eel.start('index.html', size=(1280, 850), port=0)