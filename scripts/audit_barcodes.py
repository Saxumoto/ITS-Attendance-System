import sqlite3

db = r'C:\DESKTOP FILES\ITS-Attendance-System\release\ITS Attendance System\StudentDatabase.db'
conn = sqlite3.connect(db)
c = conn.cursor()

null_empty = c.execute("SELECT COUNT(*) FROM studentData WHERE studentID IS NULL OR studentID = ''").fetchone()[0]
temp_count = c.execute("SELECT COUNT(*) FROM studentData WHERE studentID LIKE 'TEMP-%'").fetchone()[0]
real_count = c.execute("SELECT COUNT(*) FROM studentData WHERE studentID NOT LIKE 'TEMP-%' AND studentID != '' AND studentID IS NOT NULL").fetchone()[0]
total = c.execute("SELECT COUNT(*) FROM studentData").fetchone()[0]

print(f"Total Students: {total}")
print(f"Null or Empty: {null_empty}")
print(f"TEMP- Placeholder IDs: {temp_count}")
print(f"Official Barcodes: {real_count}")

print("\n--- Breakdown of Students with Placeholder (TEMP-) IDs by Year ---")
for row in c.execute("SELECT yearLevel, COUNT(*) FROM studentData WHERE studentID LIKE 'TEMP-%' GROUP BY yearLevel"):
    print(f"  {row[0]}: {row[1]} students")

print("\n--- Breakdown of Students with Real Barcodes by Year ---")
for row in c.execute("SELECT yearLevel, COUNT(*) FROM studentData WHERE studentID NOT LIKE 'TEMP-%' GROUP BY yearLevel"):
    print(f"  {row[0]}: {row[1]} students")

print("\n--- Sample of Remaining 100 TEMP- Students ---")
for s in c.execute("SELECT studentID, lastName, firstName, yearLevel FROM studentData WHERE studentID LIKE 'TEMP-%' LIMIT 15"):
    print(f"  {s[0]} | {s[1]}, {s[2]} ({s[3]})")

conn.close()
