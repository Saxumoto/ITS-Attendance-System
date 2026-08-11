import os
import re
import sqlite3
import pandas as pd

ROOT_DB_PATH = r"C:\DESKTOP FILES\ITS-Attendance-System\StudentDatabase.db"
EXCEL_PATH = r"C:\DESKTOP FILES\ITS-Attendance-System\BSIT_MASTERLIST_REVISED.xlsx"

def clean_name(row_val):
    clean_val = re.sub(r'^\d+\s+', '', str(row_val))
    clean_val = re.sub(r'\s+', ' ', clean_val).strip()
    parts = clean_val.split(',')
    if len(parts) >= 2:
        return parts[0].strip().upper(), parts[1].strip().upper()
    return None, None

def format_year(y):
    try:
        y_int = int(float(y))
        if y_int == 1: return "1st Year"
        if y_int == 2: return "2nd Year"
        if y_int == 3: return "3rd Year"
        if y_int == 4: return "4th Year"
        return f"{y_int}th Year"
    except:
        y_str = str(y).strip()
        if "year" in y_str.lower():
            return y_str
        return f"{y_str} Year"

def update_root_db():
    """
    Syncs the root StudentDatabase.db (table studentData) directly.
    Promotes matched students to new Year Levels.
    Adds unmatched students with TEMP-XXX ID numbers.
    """
    if not os.path.exists(ROOT_DB_PATH):
        print(f"[ERROR] Root database not found at: {ROOT_DB_PATH}")
        return False
    if not os.path.exists(EXCEL_PATH):
        print(f"[ERROR] Revised Excel not found at: {EXCEL_PATH}")
        return False
        
    print(f"Syncing: {os.path.basename(ROOT_DB_PATH)}...")
    conn = sqlite3.connect(ROOT_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Read Excel
    df_excel = pd.read_excel(EXCEL_PATH)
    name_col = next((col for col in df_excel.columns if 'Name' in str(col) or col == 'Unnamed: 0'), df_excel.columns[0])
    year_col = next((col for col in df_excel.columns if 'Year' in str(col)), None)
    
    # Load all existing students
    cursor.execute("SELECT studentID, firstName, lastName, yearLevel FROM studentData")
    db_students = [dict(row) for row in cursor.fetchall()]
    
    db_by_lastname = {}
    for s in db_students:
        ln = s['lastName'].strip().upper()
        if ln not in db_by_lastname:
            db_by_lastname[ln] = []
        db_by_lastname[ln].append(s)
        
    matched_count = 0
    updated_count = 0
    inserted_count = 0
    
    # Find next temporary ID suffix to avoid duplicates if run multiple times
    cursor.execute("SELECT studentID FROM studentData WHERE studentID LIKE 'TEMP-%'")
    temp_ids = [row[0] for row in cursor.fetchall()]
    temp_suffixes = []
    for tid in temp_ids:
        try:
            temp_suffixes.append(int(tid.split('-')[1]))
        except:
            pass
    next_suffix = max(temp_suffixes) + 1 if temp_suffixes else 1
    
    for index, row in df_excel.iterrows():
        raw_name = row[name_col]
        if pd.isna(raw_name):
            continue
            
        c_last, c_first = clean_name(raw_name)
        if not c_last or not c_first:
            continue
            
        new_year = format_year(row[year_col]) if year_col else "N/A"
        
        candidates = db_by_lastname.get(c_last, [])
        matched_student = None
        for cand in candidates:
            cand_fn = cand['firstName'].strip().upper()
            if cand_fn in c_first or c_first in cand_fn:
                matched_student = cand
                break
                
        if matched_student:
            matched_count += 1
            if matched_student['yearLevel'] != new_year:
                cursor.execute("""
                    UPDATE studentData
                    SET yearLevel = ?
                    WHERE studentID = ?
                """, (new_year, matched_student['studentID']))
                updated_count += 1
        else:
            # Check if already added under TEMP-XXX ID
            cursor.execute("""
                SELECT studentID, yearLevel FROM studentData 
                WHERE lastName = ? AND firstName = ?
            """, (c_last.title(), c_first.title()))
            existing_temp = cursor.fetchone()
            
            if existing_temp:
                if existing_temp['yearLevel'] != new_year:
                    cursor.execute("""
                        UPDATE studentData
                        SET yearLevel = ?
                        WHERE studentID = ?
                    """, (new_year, existing_temp['studentID']))
                    updated_count += 1
            else:
                temp_id = f"TEMP-{next_suffix:03d}"
                next_suffix += 1
                cursor.execute("""
                    INSERT INTO studentData (studentID, firstName, lastName, yearLevel)
                    VALUES (?, ?, ?, ?)
                """, (temp_id, c_first.title(), c_last.title(), new_year))
                inserted_count += 1
                
    conn.commit()
    conn.close()
    
    print("-" * 50)
    print("SYNC SUMMARY FOR ROOT StudentDatabase.db:")
    print(f"   Matched Students: {matched_count}")
    print(f"   Updated Year Levels: {updated_count}")
    print(f"   Inserted (New with TEMP-XXX ID): {inserted_count}")
    print("-" * 50)
    return True

if __name__ == "__main__":
    update_root_db()
