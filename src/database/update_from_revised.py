import os
import re
import pandas as pd
from src.config import DB_PATH, PROJECT_ROOT
from src.database.db_manager import get_db_connection

EXCEL_PATH = os.path.join(PROJECT_ROOT, "BSIT_MASTERLIST_REVISED.xlsx")

def clean_name(row_val):
    """
    Cleans "1  ABAD, Manu Gabriel Calibo" -> "ABAD", "MANU GABRIEL CALIBO"
    Handles leading sequence numbers and double spaces.
    """
    # Remove leading number and space, e.g., "1  " or "10 "
    clean_val = re.sub(r'^\d+\s+', '', str(row_val))
    # Replace multiple spaces with a single space
    clean_val = re.sub(r'\s+', ' ', clean_val).strip()
    
    parts = clean_val.split(',')
    if len(parts) >= 2:
        return parts[0].strip().upper(), parts[1].strip().upper()
    return None, None

def format_year(y):
    """Formats year integer to string: 1 -> 1st Year, 2 -> 2nd Year, etc."""
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

def update_from_revised():
    """
    Matches students in BSIT_MASTERLIST_REVISED.xlsx with their IDs in the local DB.
    Updates Year Level and Course details without dropping historical records.
    Logs unmatched students for review.
    """
    if not os.path.exists(EXCEL_PATH):
        print(f"[ERROR] Revised master list not found at: {EXCEL_PATH}")
        return False
        
    print(f"Reading revised master list: {os.path.basename(EXCEL_PATH)}...")
    try:
        df_excel = pd.read_excel(EXCEL_PATH)
    except Exception as e:
        print(f"[ERROR] Failed to read Excel file: {e}")
        return False
        
    # Smart Column Finder
    name_col = next((col for col in df_excel.columns if 'Name' in str(col) or col == 'Unnamed: 0'), df_excel.columns[0])
    year_col = next((col for col in df_excel.columns if 'Year' in str(col)), None)
    course_col = next((col for col in df_excel.columns if 'Course' in str(col)), None)
    
    print(f"Detected Columns -> Name: '{name_col}', Year: '{year_col}', Course: '{course_col}'")
    
    # Load existing students from DB
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, first_name, last_name, year_level, course FROM students")
        db_students = [dict(row) for row in cursor.fetchall()]
        
    print(f"Loaded {len(db_students)} existing students from database for ID matching.")
    
    # Index DB students by uppercase last name for quick candidate lookup
    db_by_lastname = {}
    for student in db_students:
        ln_upper = student['last_name'].strip().upper()
        if ln_upper not in db_by_lastname:
            db_by_lastname[ln_upper] = []
        db_by_lastname[ln_upper].append(student)
        
    matched_count = 0
    updated_count = 0
    unmatched_records = []
    
    updates_to_make = []
    
    for index, row in df_excel.iterrows():
        raw_name = row[name_col]
        if pd.isna(raw_name):
            continue
            
        c_last, c_first = clean_name(raw_name)
        if not c_last or not c_first:
            unmatched_records.append((index + 2, str(raw_name), "Could not parse name format (expected 'Lastname, Firstname')"))
            continue
            
        # Search candidate matches by Last Name
        candidates = db_by_lastname.get(c_last, [])
        matched_student = None
        
        for candidate in candidates:
            cand_fn_upper = candidate['first_name'].strip().upper()
            
            # Fuzzy match first names: check if candidate first name matches/is substring of Excel first name, or vice versa
            # E.g. DB: "MANU GABRIEL" matches Excel: "MANU GABRIEL CALIBO"
            if cand_fn_upper in c_first or c_first in cand_fn_upper:
                matched_student = candidate
                break
                
        if matched_student:
            matched_count += 1
            
            # Determine updated values
            new_year = format_year(row[year_col]) if year_col else matched_student['year_level']
            new_course = str(row[course_col]).strip() if course_col else matched_student['course']
            
            # Queue update if values changed
            if (matched_student['year_level'] != new_year or 
                matched_student['course'] != new_course):
                
                updates_to_make.append((new_year, new_course, matched_student['student_id']))
                updated_count += 1
        else:
            unmatched_records.append((index + 2, f"{c_last}, {c_first}", "No matching student ID found in database"))
            
    # Apply database updates
    if updates_to_make:
        print(f"Applying {len(updates_to_make)} database updates...")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                UPDATE students
                SET year_level = ?, course = ?
                WHERE student_id = ?
            """, updates_to_make)
            
    print("-" * 50)
    print("MATCHING & UPDATE SUMMARY:")
    print(f"   Matched Students: {matched_count} / {len(df_excel)}")
    print(f"   Database Records Updated: {updated_count}")
    print(f"   Unmatched Students (New/Typo): {len(unmatched_records)}")
    print("-" * 50)
    
    if unmatched_records:
        print("\n[WARNING] Top 10 unmatched students (Excel names that don't match database records):")
        for row_num, name, reason in unmatched_records[:10]:
            print(f"   Line {row_num}: {name} -> {reason}")
        if len(unmatched_records) > 10:
            print(f"   ... and {len(unmatched_records) - 10} more.")
            
        # Export to CSV for audit
        unmatched_df = pd.DataFrame(unmatched_records, columns=["Excel Row", "Parsed Name", "Reason"])
        unmatched_path = os.path.join(PROJECT_ROOT, "unmatched_revised_students.csv")
        unmatched_df.to_csv(unmatched_path, index=False)
        print(f"\n[INFO] Complete unmatched list written to: {unmatched_path}")
        
    print("[INFO] Masterlist update execution finished!")
    return True

if __name__ == "__main__":
    update_from_revised()
