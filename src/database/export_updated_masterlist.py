import os
import sqlite3
import pandas as pd
from src.config import PROJECT_ROOT

ROOT_DB_PATH = os.path.join(PROJECT_ROOT, "StudentDatabase.db")
OUTPUT_MASTERLIST_PATH = os.path.join(PROJECT_ROOT, "BSIT_MASTERLIST_UPDATED_WITH_IDS.xlsx")

def export_updated_masterlist():
    """
    Exports the current database student list to an Excel spreadsheet
    formatted exactly like BSIT_MASTERLIST_REVISED.xlsx, but including
    the StudentID column.
    
    This allows the user to easily copy-paste the new freshmen and matched
    IDs back into their department spreadsheet.
    """
    if not os.path.exists(ROOT_DB_PATH):
        print(f"[ERROR] Database not found at: {ROOT_DB_PATH}")
        return False
        
    print("Connecting to database and fetching student list...")
    conn = sqlite3.connect(ROOT_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Query all students sorted by Last Name
    cursor.execute("SELECT studentID, firstName, lastName, yearLevel, regType FROM studentData ORDER BY lastName ASC, firstName ASC")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("[WARNING] No student records found in database.")
        return False
        
    print(f"Loaded {len(rows)} students. Formatting data...")
    
    formatted_data = []
    for idx, row in enumerate(rows, start=1):
        last_name = str(row['lastName']).strip().upper()
        first_name = str(row['firstName']).strip().upper()
        
        # Format name as: "1  LASTNAME, FIRSTNAME"
        name_formatted = f"{idx}  {last_name}, {first_name}"
        
        # Convert yearLevel string back to integer (e.g. "1st Year" -> 1)
        year_str = str(row['yearLevel']).lower()
        year_val = 1
        if "2nd" in year_str or "2" in year_str:
            year_val = 2
        elif "3rd" in year_str or "3" in year_str:
            year_val = 3
        elif "4th" in year_str or "4" in year_str:
            year_val = 4
            
        formatted_data.append({
            "StudentID": str(row['studentID']).strip(),
            "Name of Student": name_formatted,
            "Course": "BSIT",
            "Year": year_val,
            "Sex": "N/A", # Place-holder for manual input
            "RegType": str(row['regType'] if 'regType' in row.keys() else 'EXISTING').strip()
        })
        
    # Convert to DataFrame
    df = pd.DataFrame(formatted_data)
    
    # Save to Excel
    print(f"Exporting updated master list to: {os.path.basename(OUTPUT_EXCEL_PATH := OUTPUT_MASTERLIST_PATH)}...")
    try:
        df.to_excel(OUTPUT_MASTERLIST_PATH, index=False)
        print("-" * 50)
        print("EXPORT SUCCESSFUL!")
        print(f"   Created File: {os.path.basename(OUTPUT_MASTERLIST_PATH)}")
        print(f"   Total Students Exported: {len(df)}")
        print("   Columns Included: StudentID, Name of Student, Course, Year, Sex")
        print("-" * 50)
        print("You can open this file and merge it directly into your department files.")
    except Exception as e:
        print(f"[ERROR] Failed to save Excel file: {e}")
        return False
        
    return True

if __name__ == "__main__":
    export_updated_masterlist()
