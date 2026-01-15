import sqlite3
import pandas as pd
import os

# --- FILE NAMES ---
# Make sure these match your actual file names exactly!
OLD_DB_FILE = 'StudentDatabase.db'
NEW_LIST_FILE = 'IT-Database.xlsx - Sheet1.csv'  # Or just 'IT-Database.csv' if you renamed it
OUTPUT_FILE = 'Final_Student_List.xlsx'

def create_merged_excel():
    print("--- STARTING MERGE PROCESS ---")

    # 1. LOAD OLD DATA (From SQLite)
    if not os.path.exists(OLD_DB_FILE):
        print(f"Error: {OLD_DB_FILE} not found.")
        return

    print(f"Reading old database: {OLD_DB_FILE}...")
    conn = sqlite3.connect(OLD_DB_FILE)
    
    # We read the old data into a DataFrame
    try:
        # Adjust table name if needed. Based on your uploads, it was 'studentData'
        df_old = pd.read_sql_query("SELECT studentID, firstName, lastName FROM studentData", conn)
    except Exception as e:
        print(f"Could not read table from DB: {e}")
        return
    conn.close()
    print(f"Found {len(df_old)} students in old database.")


    # 2. LOAD NEW DATA (From CSV/Excel)
    if not os.path.exists(NEW_LIST_FILE):
        print(f"Error: {NEW_LIST_FILE} not found.")
        return

    print(f"Reading new list: {NEW_LIST_FILE}...")
    try:
        # specific logic to read your CSV format
        # header=0 means the first row contains column names
        df_new = pd.read_csv(NEW_LIST_FILE, encoding='utf-8', on_bad_lines='skip')
        
        # CLEANUP: Rename columns to match standard format
        # You might need to adjust these indices [0], [1] based on your specific CSV column order
        # Assuming: Col A=ID, B=LastName, C=FirstName, E=YearLevel (based on typical exports)
        
        # Let's print the columns found so you can verify
        print("Columns found in CSV:", df_new.columns.tolist())
        
        # We rename the columns to match what we want
        # NOTE: Update these names based on the print output above if it fails!
        df_new.rename(columns={
            df_new.columns[0]: 'studentID', 
            df_new.columns[1]: 'lastName',
            df_new.columns[2]: 'firstName',
            df_new.columns[4]: 'yearLevel' # Assumes Year Level is 5th column
        }, inplace=True)
        
        # Keep only the columns we need from the new file (ID + Year Level)
        # We discard address, birthday, etc. here.
        df_new_clean = df_new[['studentID', 'yearLevel']].copy()
        
        # Ensure IDs are strings (to match cleanly)
        df_new_clean['studentID'] = df_new_clean['studentID'].astype(str).str.strip()
        df_old['studentID'] = df_old['studentID'].astype(str).str.strip()

    except Exception as e:
        print(f"Error reading CSV: {e}")
        return


    # 3. MERGE THE DATA
    print("Merging data based on Student ID...")
    
    # We take the OLD database (Names) and add the YEAR LEVEL from the NEW file
    # "how='left'" means: Keep everyone from the old DB, and attach Year Level if found.
    merged_df = pd.merge(df_old, df_new_clean, on='studentID', how='left')

    # Fill missing year levels with "N/A"
    merged_df['yearLevel'] = merged_df['yearLevel'].fillna('N/A')


    # 4. SAVE TO EXCEL
    print(f"Saving to {OUTPUT_FILE}...")
    merged_df.to_excel(OUTPUT_FILE, index=False)
    
    print("--- SUCCESS! ---")
    print(f"Created: {OUTPUT_FILE}")
    print(f"Total Students: {len(merged_df)}")

if __name__ == "__main__":
    create_merged_excel()