import os
import pandas as pd
from src.config import DB_PATH, PROJECT_ROOT
from src.database.db_manager import get_db_connection, initialize_database

DEFAULT_EXCEL_PATH = os.path.join(PROJECT_ROOT, "Final_Student_List.xlsx")

def seed_students(excel_path=DEFAULT_EXCEL_PATH):
    """
    Reads students from the Excel file and updates the SQLite database.
    Uses 'ON CONFLICT DO UPDATE' to preserve historical attendance logs
    while allowing student info (names, year levels) to be updated.
    """
    print("--- [SEED] STARTING STUDENT SEEDING ---")
    
    # 1. Verify files and initialize database
    if not os.path.exists(excel_path):
        print(f"[ERROR] Excel master list not found at: {excel_path}")
        return False
        
    initialize_database()
    
    # 2. Read Excel
    print(f"Reading Excel: {os.path.basename(excel_path)}...")
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"[ERROR] Error reading Excel file: {e}")
        return False
        
    # Check for required columns
    required_cols = ['studentID', 'firstName', 'lastName', 'yearLevel']
    for col in required_cols:
        if col not in df.columns:
            print(f"[ERROR] Missing required column '{col}' in Excel sheet.")
            return False
            
    # Clean data (remove rows with missing studentID)
    df = df.dropna(subset=['studentID'])
    
    # 3. Seed to database
    inserted_count = 0
    updated_count = 0
    error_count = 0
    
    print("Connecting to database and seeding student list...")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        for index, row in df.iterrows():
            student_id = str(row['studentID']).strip()
            first_name = str(row['firstName']).strip()
            last_name = str(row['lastName']).strip()
            year_level = str(row['yearLevel']).strip()
            
            # Default course to 'BSIT' if not provided
            course = str(row.get('course', 'BSIT')).strip()
            status = 'ACTIVE'
            
            try:
                # Check if student exists
                cursor.execute("SELECT first_name, last_name, year_level, course FROM students WHERE student_id = ?", (student_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update if anything changed
                    if (existing['first_name'] != first_name or 
                        existing['last_name'] != last_name or 
                        existing['year_level'] != year_level or 
                        existing['course'] != course):
                        
                        cursor.execute("""
                            UPDATE students 
                            SET first_name = ?, last_name = ?, year_level = ?, course = ?
                            WHERE student_id = ?
                        """, (first_name, last_name, year_level, course, student_id))
                        updated_count += 1
                else:
                    # Insert new student
                    cursor.execute("""
                        INSERT INTO students (student_id, first_name, last_name, year_level, course, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (student_id, first_name, last_name, year_level, course, status))
                    inserted_count += 1
                    
            except Exception as ex:
                print(f"[WARNING] Error seeding row {index + 2} (ID: {student_id}): {ex}")
                error_count += 1
                
    print("-" * 40)
    print("SEEDING SUMMARY:")
    print(f"   New Students Inserted: {inserted_count}")
    print(f"   Student Details Updated: {updated_count}")
    print(f"   Errors: {error_count}")
    print(f"   Total processed: {len(df)}")
    print("-" * 40)
    print("Seeding finished successfully!")
    return True

if __name__ == "__main__":
    seed_students()
