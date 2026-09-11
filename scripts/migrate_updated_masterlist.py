import sqlite3
import pypdf
import os
import re

DB_PATH = 'StudentDatabase.db'
PDF_DIR = 'UPDATED MASTERLIST'

def parse_pdf_line(line):
    # Matches patterns like M2BSITABAD, Manu Gabriel Calibo1 or F1BSITABECIA, Jhey Kristelle Mae T ortor1
    m = re.match(r'^([MF])([1-4])BSIT(.+?),\s*(.+?)(\d+)$', line)
    if m:
        sex, year, last_name, first_name, idx = m.groups()
        first_name = re.sub(r'\s+', ' ', first_name).strip()
        last_name = re.sub(r'\s+', ' ', last_name).strip()
        year_map = {'1': '1st Year', '2': '2nd Year', '3': '3rd Year', '4': '4th Year'}
        return {
            'sex': sex,
            'yearLevel': year_map[year],
            'lastName': last_name,
            'firstName': first_name,
            'rawIndex': idx
        }
    return None

def migrate_masterlist():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Step 1: Cache existing student ID mappings by (lastName, firstName) or lastName
    cursor.execute("SELECT studentID, firstName, lastName, yearLevel, regType FROM studentData")
    existing_records = cursor.fetchall()
    
    id_map_exact = {}
    id_map_lastname = {}

    for sid, fname, lname, ylevel, rtype in existing_records:
        if sid and not str(sid).startswith('TEMP'):
            key_exact = (lname.strip().lower(), fname.strip().lower())
            id_map_exact[key_exact] = sid
            
            key_last = lname.strip().lower()
            if key_last not in id_map_lastname:
                id_map_lastname[key_last] = []
            id_map_lastname[key_last].append((fname.strip().lower(), sid))

    print(f"Loaded {len(existing_records)} existing DB records.")
    print(f"Loaded {len(id_map_exact)} verified barcode IDs.")

    # Step 2: Parse PDF masterlist
    masterlist = []
    for fname in sorted(os.listdir(PDF_DIR)):
        if fname.endswith('.pdf'):
            path = os.path.join(PDF_DIR, fname)
            reader = pypdf.PdfReader(path)
            for page in reader.pages:
                text = page.extract_text()
                for line in text.split('\n'):
                    item = parse_pdf_line(line.strip())
                    if item:
                        masterlist.append(item)

    print(f"Parsed {len(masterlist)} official students from UPDATED MASTERLIST PDFs.")

    # Step 3: Match IDs & Re-build studentData table
    temp_id_counter = 1001
    matched_existing_ids = 0
    assigned_pending_ids = 0

    new_student_rows = []

    for item in masterlist:
        lname = item['lastName']
        fname = item['firstName']
        ylevel = item['yearLevel']

        key_exact = (lname.lower(), fname.lower())
        assigned_id = None
        reg_type = 'EXISTING'

        if key_exact in id_map_exact:
            assigned_id = id_map_exact[key_exact]
            matched_existing_ids += 1
        else:
            # Try fuzzy match on last name + first name prefix
            key_last = lname.lower()
            if key_last in id_map_lastname:
                for existing_fname, existing_id in id_map_lastname[key_last]:
                    if existing_fname in fname.lower() or fname.lower() in existing_fname:
                        assigned_id = existing_id
                        matched_existing_ids += 1
                        break

        if not assigned_id:
            assigned_id = f"TEMP-2026-{temp_id_counter}"
            temp_id_counter += 1
            assigned_pending_ids += 1
            reg_type = 'PENDING_ID'

        new_student_rows.append((assigned_id, fname, lname, ylevel, reg_type))

    # Step 4: Atomic Table Refresh
    cursor.execute("DELETE FROM studentData")
    cursor.executemany("INSERT INTO studentData (studentID, firstName, lastName, yearLevel, regType) VALUES (?, ?, ?, ?, ?)", new_student_rows)

    conn.commit()
    conn.close()

    print("\n=================================================")
    print("      DATABASE MASTERLIST MIGRATION SUCCESS       ")
    print("=================================================")
    print(f"Total Official Enrolled Students Inserted: {len(new_student_rows)}")
    print(f"  - Preserved Existing Barcode IDs:         {matched_existing_ids}")
    print(f"  - Assigned PENDING_ID (TEMP IDs):         {assigned_pending_ids}")
    print("=================================================\n")

if __name__ == '__main__':
    migrate_masterlist()
