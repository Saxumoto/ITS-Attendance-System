import csv
import sqlite3
import os
import re

DB_PATH = r'C:\DESKTOP FILES\ITS-Attendance-System\release\ITS Attendance System\StudentDatabase.db'
BACKUP_PATH = r'C:\DESKTOP FILES\ITS-Attendance-System\backups\StudentDatabase_Backup_Before_Unified_Update_2026-10-23.db'
UNIFIED_FOLDER = r'C:\DESKTOP FILES\ITS-Attendance-System\UNIFIED_FILES\UNIFIED FILES'
MASTER_CSV = os.path.join(UNIFIED_FOLDER, 'Master_Unified_Attendance.csv')
DAY1_CSV = os.path.join(UNIFIED_FOLDER, 'Day_1_Unified_Attendance.csv')
DAY2_CSV = os.path.join(UNIFIED_FOLDER, 'Day_2_Unified_Attendance.csv')

def clean_name(name):
    """Normalize names and fix OCR / split-letter artifacts like 'T ortor', 'T ormis', 'T adashi'"""
    # Fix single letter followed by space at start of word like 'T ortor' -> 'Tortor'
    name = re.sub(r'\b([A-Za-z])\s+([a-z]{2,})\b', r'\1\2', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def parse_full_name(name_str):
    """Return (lastName, firstName) cleanly"""
    name_str = clean_name(name_str)
    if ',' in name_str:
        parts = name_str.split(',', 1)
        last = parts[0].strip().upper()
        first = parts[1].strip()
    else:
        parts = name_str.split()
        if len(parts) > 1:
            last = parts[0].strip().upper()
            first = " ".join(parts[1:]).strip()
        else:
            last = name_str.strip().upper()
            first = ""
    return last, first

def main():
    print("==========================================================")
    print("   ITS ATTENDANCE SYSTEM - UNIFIED DATABASE SYNC & UPDATE")
    print("==========================================================")
    
    # 1. Backup DB
    if not os.path.exists(os.path.dirname(BACKUP_PATH)):
        os.makedirs(os.path.dirname(BACKUP_PATH), exist_ok=True)
    import shutil
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"[1] Database backed up to:\n    {BACKUP_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Load all current DB students
    cursor.execute("SELECT studentID, firstName, lastName, yearLevel, regType FROM studentData")
    current_students = cursor.fetchall()
    print(f"[2] Loaded {len(current_students)} current student records from database.")

    db_by_id = {str(r[0]).strip(): dict(studentID=str(r[0]).strip(), firstName=r[1], lastName=r[2], yearLevel=r[3], regType=r[4]) for r in current_students}
    
    # Also index by normalized (lastName, firstName_prefix) and last name
    db_by_name = {}
    db_by_last = {}
    for sid, s in db_by_id.items():
        clean_last = clean_name(s['lastName']).upper()
        clean_first = clean_name(s['firstName']).upper()
        db_by_name[(clean_last, clean_first)] = s
        db_by_last.setdefault(clean_last, []).append(s)

    # Known scanner typos / duplicate mappings from live scanning
    TYPO_CORRECTIONS = {
        '5949428': '59849428',     # ANG, Jefferson Vangurdia (missing 8)
        '5983434': '59343434',     # BERNIDO, Bryle Teodz Vasig (7 vs 8 digit)
        '58944461': '59844461',    # CAMPOS, Dan Laurence Alfafara (589 vs 598)
        '598 9211': '59849211',    # SARPAMONES, Nhatalie Jurgs (space in ID)
        '5984926': '59849726',     # LEPARTO, Dustin Mhyvo -> Dustin Mhyco
        'TEMP-2026-1310': '59835962', # DELA CRUZ, Karl Malone (Day 1 temp vs Day 2 real ID)
    }

    # Name aliases for walk-ins where name was entered reversed or with alternate spelling
    NAME_ALIASES = {
        'CARLOS LUIGI ANTHONY, JANOLINO': ('JANOLINO', 'Carlos Luigi Anthony'),
        'DEE JAY, GENTICA': ('GENTICA', 'Dee Jay'),
        'JAYPEE, VILLFUERTE': ('VILLAFUERTE', 'Jaypee Oberes'),
        'JOVERLYN, SUMANGA': ('SUMANGA', 'Joverlyn'),
        'RUTARCH, MABOLOC': ('MABOLOC', 'Rutarch Donga'),
        'ORENCE, AL KIRBY': ('RINGCONADA', 'Al Kirby Orence'),
        'CEDEO, JOHN ANGELO': ('CEDEÑO', 'John Angelo'),
        'VEEGAS, RENIEL ESCOTE': ('VEÑEGAS', 'Reniel Escote'),
        'TRESFUENTES, JASON CANDELASA': ('TRESFUENTES', 'Jason Candelasa'),
        'TORMIS, MARIO JR.': ('TORMIS', 'Mario Jr. Odjaman'),
        'TORREON, VINCENT PAUL': ('TORREON', 'Vincent Paul Pardillo'),
        'YAMAGAMI, TADASHI': ('YAMAGAMI', 'Tadashi Sarandona')
    }

    # Read Master Unified File
    with open(MASTER_CSV, 'r', encoding='utf-8', errors='ignore') as f:
        master_rows = list(csv.DictReader(f))

    print(f"[3] Processing {len(master_rows)} records from Master_Unified_Attendance.csv...")

    updated_ids_count = 0
    new_students_count = 0
    already_matched_count = 0

    students_to_insert = []
    id_updates = [] # list of (new_id, old_id, new_last, new_first, year, reg_type)

    processed_csv_ids = set()

    for row in master_rows:
        raw_id = row['Student ID'].strip()
        raw_name = row['Full Name'].strip()
        year = row['Year Level'].strip()
        reg_type = row['Reg Type'].strip() or 'EXISTING'

        # Apply typo correction if ID is a known scanner error
        corrected_id = TYPO_CORRECTIONS.get(raw_id, raw_id)
        if corrected_id in processed_csv_ids:
            continue
        processed_csv_ids.add(corrected_id)

        last_name, first_name = parse_full_name(raw_name)
        lookup_key = f"{last_name}, {first_name}".upper()

        if lookup_key in NAME_ALIASES:
            last_name, first_name = NAME_ALIASES[lookup_key]

        # Check 1: Is corrected_id already in DB?
        if corrected_id in db_by_id:
            already_matched_count += 1
            # Check if regType was updated or name has OCR artifact
            current = db_by_id[corrected_id]
            clean_db_last = clean_name(current['lastName'])
            clean_db_first = clean_name(current['firstName'])
            if clean_db_last != current['lastName'] or clean_db_first != current['firstName']:
                cursor.execute("UPDATE studentData SET lastName=?, firstName=? WHERE studentID=?", (clean_db_last, clean_db_first, corrected_id))
            continue

        # Check 2: Match by Name (to link TEMP-2026-XXXX ID to this real barcode ID)
        matched_db_student = None
        key_exact = (last_name.upper(), first_name.upper())
        if key_exact in db_by_name:
            matched_db_student = db_by_name[key_exact]
        elif last_name.upper() in db_by_last:
            candidates = db_by_last[last_name.upper()]
            for cand in candidates:
                cand_first = clean_name(cand['firstName']).upper()
                # Match if first name matches or starts with candidate first name
                first_clean = first_name.upper()
                if cand_first in first_clean or first_clean in cand_first or cand_first.split()[0] == first_clean.split()[0]:
                    matched_db_student = cand
                    break

        if matched_db_student:
            old_id = matched_db_student['studentID']
            if old_id != corrected_id:
                id_updates.append((corrected_id, old_id, last_name, first_name, year, 'EXISTING'))
                # update our in-memory map
                db_by_id[corrected_id] = matched_db_student
                updated_ids_count += 1
        else:
            # Check 3: Truly new student (walk-in, transferee, new enrollee)
            students_to_insert.append((corrected_id, first_name, last_name, year, reg_type if reg_type != 'PENDING_ID' else 'NEW'))
            new_students_count += 1

    print("\n[4] Execution Summary:")
    print(f"  • Existing Verified Students: {already_matched_count}")
    print(f"  • Students Linked from TEMP -> Real Barcode ID: {updated_ids_count}")
    print(f"  • Brand New Students to Insert: {new_students_count}")

    # Perform ID Updates in DB
    for new_id, old_id, lname, fname, ylevel, rtype in id_updates:
        # Update studentData
        cursor.execute("""
            UPDATE studentData 
            SET studentID=?, lastName=?, firstName=?, yearLevel=?, regType=?
            WHERE studentID=?
        """, (new_id, lname, fname, ylevel, rtype, old_id))

        # Cascade update event_logs
        cursor.execute("UPDATE event_logs SET student_id=? WHERE student_id=?", (new_id, old_id))

    # Perform Inserts for Brand New Students
    for sid, fname, lname, ylevel, rtype in students_to_insert:
        cursor.execute("""
            INSERT OR REPLACE INTO studentData (studentID, firstName, lastName, yearLevel, regType)
            VALUES (?, ?, ?, ?, ?)
        """, (sid, fname, lname, ylevel, rtype))

    # Also clean up any lingering OCR spaces like 'T ortor' in studentData
    cursor.execute("SELECT studentID, lastName, firstName FROM studentData WHERE lastName LIKE '% %' OR firstName LIKE '% %'")
    for sid, lname, fname in cursor.fetchall():
        clean_l = clean_name(lname)
        clean_f = clean_name(fname)
        if clean_l != lname or clean_f != fname:
            cursor.execute("UPDATE studentData SET lastName=?, firstName=? WHERE studentID=?", (clean_l, clean_f, sid))

    conn.commit()

    # Final DB counts
    cursor.execute("SELECT COUNT(*) FROM studentData")
    total_after = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM studentData WHERE studentID LIKE 'TEMP%' OR regType='PENDING_ID'")
    pending_after = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM studentData WHERE regType='NEW'")
    new_after = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM studentData WHERE regType='EXISTING'")
    existing_after = cursor.fetchone()[0]

    print("\n==========================================================")
    print("              FINAL DATABASE STATUS (SUCCESS)             ")
    print("==========================================================")
    print(f"Total Registered Students in Database: {total_after}")
    print(f"  - Verified Barcode IDs (EXISTING):    {existing_after}")
    print(f"  - New Registrations (NEW):            {new_after}")
    print(f"  - Unlinked Remaining (PENDING_ID):    {pending_after}")
    print("==========================================================")

    conn.close()

if __name__ == '__main__':
    main()
