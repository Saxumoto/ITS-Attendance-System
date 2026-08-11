import os
import re
import pandas as pd
from src.config import PROJECT_ROOT
from src.database.db_manager import get_db_connection

EXCEL_PATH = os.path.join(PROJECT_ROOT, "BSIT_MASTERLIST_REVISED.xlsx")
OUTPUT_EXCEL_PATH = os.path.join(PROJECT_ROOT, "BSIT_MASTERLIST_REVISED_WITH_IDS.xlsx")

def clean_name(row_val):
    """Clean '1  LASTNAME, FIRSTNAME MIDDLE' -> 'LASTNAME', 'FIRSTNAME MIDDLE'"""
    clean_val = re.sub(r'^\d+\s+', '', str(row_val))
    clean_val = re.sub(r'\s+', ' ', clean_val).strip()
    parts = clean_val.split(',')
    if len(parts) >= 2:
        return parts[0].strip().upper(), parts[1].strip().upper()
    return None, None

def export_revised_with_ids():
    if not os.path.exists(EXCEL_PATH):
        print(f"[ERROR] Revised Excel list not found at: {EXCEL_PATH}")
        return False
        
    print(f"Reading master list: {os.path.basename(EXCEL_PATH)}...")
    try:
        df_excel = pd.read_excel(EXCEL_PATH)
    except Exception as e:
        print(f"[ERROR] Failed to read Excel file: {e}")
        return False
        
    # Find name column
    name_col = next((col for col in df_excel.columns if 'Name' in str(col) or col == 'Unnamed: 0'), df_excel.columns[0])
    
    # Load all student IDs and names from the DB
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, first_name, last_name FROM students")
        db_students = [dict(row) for row in cursor.fetchall()]
        
    # Index DB students by last name
    db_by_lastname = {}
    for student in db_students:
        ln_upper = student['last_name'].strip().upper()
        if ln_upper not in db_by_lastname:
            db_by_lastname[ln_upper] = []
        db_by_lastname[ln_upper].append(student)
        
    student_ids = []
    match_count = 0
    missing_count = 0
    
    # Match and collect IDs
    for index, row in df_excel.iterrows():
        raw_name = row[name_col]
        if pd.isna(raw_name):
            student_ids.append("")
            continue
            
        c_last, c_first = clean_name(raw_name)
        if not c_last or not c_first:
            student_ids.append("")
            missing_count += 1
            continue
            
        candidates = db_by_lastname.get(c_last, [])
        matched_id = None
        for cand in candidates:
            cand_fn_upper = cand['first_name'].strip().upper()
            if cand_fn_upper in c_first or c_first in cand_fn_upper:
                matched_id = cand['student_id']
                break
                
        if matched_id:
            student_ids.append(matched_id)
            match_count += 1
        else:
            # Leave empty for manual input
            student_ids.append("PENDING_ID")
            missing_count += 1
            
    # Insert StudentID column at the beginning of the DataFrame
    df_excel.insert(0, 'StudentID', student_ids)
    
    # Save the updated sheet
    print(f"Saving merged master list with ID numbers to: {os.path.basename(OUTPUT_EXCEL_PATH)}...")
    try:
        df_excel.to_excel(OUTPUT_EXCEL_PATH, index=False)
        print(f"[INFO] Export complete!")
        print(f"       Total Rows: {len(df_excel)}")
        print(f"       Matched & Integrated IDs: {match_count}")
        print(f"       Pending IDs (unmatched): {missing_count}")
    except Exception as e:
        print(f"[ERROR] Failed to save Excel file: {e}")
        return False
        
    return True

if __name__ == "__main__":
    export_revised_with_ids()
