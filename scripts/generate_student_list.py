import pandas as pd
import sqlite3
import re
import os

# --- FILE NAMES ---
DB_FILE = 'StudentDatabase.db'
EXCEL_FILE = 'IT-Database.xlsx'  # <--- Now looking for the Excel file
OUTPUT_FILE = 'Final_Student_List.xlsx'

def generate_list():
    print("--- STARTING SMART MERGE (EXCEL MODE) ---")

    # 1. LOAD DATABASE
    print("Loading database...")
    if not os.path.exists(DB_FILE):
        print(f"❌ Error: {DB_FILE} not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    df_db = pd.read_sql_query("SELECT * FROM studentData", conn)
    conn.close()
    
    # Normalize DB names
    df_db['lastName_upper'] = df_db['lastName'].str.strip().str.upper()
    df_db['firstName_upper'] = df_db['firstName'].str.strip().str.upper()

    # 2. LOAD EXCEL FILE
    print(f"Loading Excel: {EXCEL_FILE}...")
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ Error: {EXCEL_FILE} not found. Did you rename it back to .xlsx?")
        return

    try:
        # Read Excel directly
        df_csv = pd.read_excel(EXCEL_FILE)
        print(f"✅ Loaded {len(df_csv)} rows.")
        # print(f"Columns: {df_csv.columns.tolist()}") # Debugging
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return

    # 3. MATCHING LOGIC
    def clean_name(row_val):
        # Cleans "1  ABAD, Manu Gabriel" -> "ABAD", "MANU GABRIEL"
        # Remove leading digits and spaces
        clean_val = re.sub(r'^\d+\s+', '', str(row_val))
        # Split by comma
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
            return "N/A"

    print("Matching students...")
    matched_data = []

    # Smart Column Finder
    # We look for columns containing 'Name' and 'Year'
    name_col = next((col for col in df_csv.columns if 'Name' in str(col)), df_csv.columns[0])
    year_col = next((col for col in df_csv.columns if 'Year' in str(col)), df_csv.columns[2] if len(df_csv.columns) > 2 else None)

    print(f"Using columns -> Name: '{name_col}', Year: '{year_col}'")

    for idx, row in df_csv.iterrows():
        try:
            # Get data from Excel row
            c_last, c_first = clean_name(row[name_col])
            c_year = format_year(row[year_col]) if year_col else "N/A"
            
            if c_last and c_first:
                # Find matching Last Name in DB
                candidates = df_db[df_db['lastName_upper'] == c_last]
                
                for _, db_row in candidates.iterrows():
                    # Check if DB First Name is inside Excel First Name
                    # e.g. if DB has "MANU", it matches "MANU GABRIEL"
                    if db_row['firstName_upper'] in c_first:
                        matched_data.append({
                            'studentID': db_row['studentID'],
                            'firstName': db_row['firstName'],
                            'lastName': db_row['lastName'],
                            'yearLevel': c_year
                        })
                        break 
        except Exception:
            continue

    # 4. EXPORT
    if matched_data:
        df_final = pd.DataFrame(matched_data)
        df_final.to_excel(OUTPUT_FILE, index=False)
        print(f"\n✅ SUCCESS! Matched {len(df_final)} students.")
        print(f"📁 Created file: {OUTPUT_FILE}")
        print("-" * 30)
        print("NEXT STEP: Run 'import_new_db.py' to update your system database.")
    else:
        print("\n❌ No matches found. Check your Excel file structure.")

if __name__ == "__main__":
    generate_list()