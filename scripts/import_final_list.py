import sqlite3
import pandas as pd
import os

# --- CONFIGURATION ---
EXCEL_FILE = 'Final_Student_List.xlsx'
DB_FILE = 'StudentDatabase.db'

def import_data():
    print("--- IMPORTING CLEAN DATA ---")

    # 1. CHECK FILES
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ Error: {EXCEL_FILE} not found.")
        return
    if not os.path.exists(DB_FILE):
        print(f"❌ Error: {DB_FILE} not found.")
        return

    # 2. READ EXCEL
    print("Reading Excel file...")
    df = pd.read_excel(EXCEL_FILE)
    print(f"Loaded {len(df)} students.")

    # 3. UPDATE DATABASE
    print("Connecting to database...")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # We will recreate the studentData table to ensure it has the 'yearLevel' column
    print("Resetting 'studentData' table...")
    c.execute("DROP TABLE IF EXISTS studentData")
    
    # Create new table structure
    c.execute('''CREATE TABLE studentData (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    studentID TEXT UNIQUE,
                    firstName TEXT,
                    lastName TEXT,
                    yearLevel TEXT
                )''')

    print("Inserting students...")
    success_count = 0
    
    for index, row in df.iterrows():
        try:
            # Insert row
            c.execute("INSERT INTO studentData (studentID, firstName, lastName, yearLevel) VALUES (?, ?, ?, ?)",
                      (str(row['studentID']), row['firstName'], row['lastName'], row['yearLevel']))
            success_count += 1
        except Exception as e:
            print(f"⚠️ Issue with row {index}: {e}")

    conn.commit()
    conn.close()

    print("-" * 30)
    print("IMPORT COMPLETE!")
    print(f"✅ Database updated with {success_count} students.")
    print("-" * 30)
    print("🚀 YOU ARE READY! Run 'python main.py' to start your system.")

if __name__ == "__main__":
    import_data()