import pandas as pd

# Load your Excel file
file_name = 'Final_Student_List.xlsx'
df = pd.read_excel(file_name)

print(f"📄 Total Rows in Excel: {len(df)}")

# Check for duplicates
duplicates = df[df.duplicated('studentID', keep=False)]

if not duplicates.empty:
    print(f"⚠️ FOUND {len(duplicates)} DUPLICATE ROWS!")
    print("Here are some of the IDs appearing more than once:")
    print(duplicates['studentID'].value_counts().head(10))
else:
    print("✅ No duplicates found. The issue might be empty rows or formatting.")