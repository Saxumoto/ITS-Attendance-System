# 📱 ITS Attendance System

A modern, desktop-based attendance tracking solution wrapped in a web-tech interface for the **Information Technology Society (ITS)**. This system streamlines event check-ins using barcode scanning, real-time database transactions, and automated side-by-side Excel reporting.

Built with **Python Eel** serving a highly responsive HTML, CSS (Vanilla), and JavaScript frontend for a state-of-the-art dark slate dashboard experience.

---

## 🚀 Key Features

* **⚡ Fast Scanning Portal:** Quick barcode/ID scanning with instant Web Audio API synthesised feedback (✅ Beep / ❌ Buzz). Includes candidate resolution popup for multiple matches during keyboard search.
* **🔒 Period Lock System:** Prevent accidental scans or registry entries by locking the active scan period (e.g. `Morning Time IN` is closed while `Morning Time OUT` remains open). Lock states are persisted crash-proof in SQLite.
* **📈 6-Card Metrics Dashboard:** Real-time statistics tracking total unique attendees, divided into:
  - **Total Attended**
  - **1st Year (Freshmen)**
  - **2nd Year (Sophomores)**
  - **3rd Year (Juniors)**
  - **4th Year (Seniors)**
  - **Not Found (Unrecognized scans)**
* **🔄 Unique Student Tracking:** Metric board logic tracks unique student IDs, avoiding duplicate tallies for students scanning multiple times.
* **🎛️ Minimalist Horizontal Control Bar:** Custom spacing saves over 75% of vertical HUD height, leaving more room to display live student check-in log tables.
* **👥 Transferee & Walk-in Support:** Register unrecognized scans with custom types: `New / Walk-in` or `Transferee`. 
* **📅 Timezone-Safe Date Default:** Calendar defaults securely to local system time instead of UTC to avoid midnight data mismatch.
* **📂 Native Excel Exporter (.xlsx):** Compiles side-by-side session data for active attendees, automatically calculating column widths to fit cell contents perfectly in Microsoft Excel with no text cutoffs.

---

## 📁 Project Structure

The files are neatly organized into folders for clean maintainability:
* `main.py` ➔ Python backend and Eel server entry point.
* `StudentDatabase.db` ➔ Active production SQLite database.
* `web/` ➔ Static UI files (`index.html` markup, styling, JS and `logo.png` logo assets).
* `scripts/` ➔ Backend utility scripts (duplication checkers, Excel importers).
* `rosters_and_archives/` ➔ Archive directory containing raw student directories and spreadsheet database source files.
* `backups/` ➔ Archived deprecated CustomTkinter source files and graphic assets.
* `venv/` ➔ Python virtual environment.

---

## 🛠️ Tech Stack

* **Language Backend:** Python 3.12 (virtualized in venv)
* **Frontend Engine:** Python Eel (serving Chrome/Chromium App-Mode)
* **Design Stack:** HTML5, CSS3 Variables, JavaScript ES6
* **Database:** SQLite3
* **Spreadsheet Generation:** Pandas, Openpyxl (native `.xlsx` formatting)

---

## 📥 Installation & Usage

### Running from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/Saxumoto/ITS-Attendance-System.git
   cd ITS-Attendance-System
   ```
2. Activate virtual environment:
   ```bash
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install eel pandas openpyxl
   ```
4. Run the application:
   ```bash
   python main.py
   ```

---
*Developed for the Information Technology Society.*
