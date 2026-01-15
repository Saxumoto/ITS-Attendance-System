# 📱 ITS Attendance System (Command Center)

A modern, desktop-based attendance tracking solution designed for the **Information Technology Society (ITS)**. This system streamlines event check-ins using barcode scanning, real-time database updates, and automated reporting.

Built with **Python** and **CustomTkinter** for a sleek, responsive user interface.

## 🚀 Key Features

* **⚡ Fast Scanning:** Quick barcode/ID scanning with instant audio feedback (✅ Beep / ❌ Buzz).
* **📊 Live Dashboard:** Real-time statistics of total attendees broken down by year level.
* **🌗 Modern UI:** Professional Light/Dark mode with a responsive layout.
* **📅 Event Management:** Custom date picker and event naming for organized record-keeping.
* **📂 Data Power:**
    * **Import:** Easily load student lists from Excel.
    * **Export:** One-click export of attendance logs to CSV for reporting.
* **💾 Local Database:** Powered by SQLite for reliable, offline data storage.
* **📦 Portable:** Compiled into a standalone `.exe` for easy deployment on Windows computers.

## 🛠️ Tech Stack

* **Language:** Python 3.12
* **GUI Framework:** CustomTkinter
* **Database:** SQLite3
* **Data Handling:** Pandas, CSV
* **Utilities:** Winsound (Audio), Pillow (Images), TkCalendar (Date Picker)
* **Build Tool:** PyInstaller

## 📥 Installation & Usage

### Option A: Run the App (Windows)
1.  Download the latest release (or locate the `dist/` folder).
2.  Ensure `StudentDatabase.db` is in the same folder as `main.exe`.
3.  Double-click **`main.exe`** to launch the Command Center.

### Option B: Run from Source
1.  Clone the repository:
    ```bash
    git clone [https://github.com/Saxumoto/ITS-Attendance-System.git](https://github.com/Saxumoto/ITS-Attendance-System.git)
    cd ITS-Attendance-System
    ```
2.  Install dependencies:
    ```bash
    pip install customtkinter pandas pillow tkcalendar
    ```
3.  Run the application:
    ```bash
    python main.py
    ```

## 📸 How to Use
1.  **Select Date & Event:** Choose the active date and name your event.
2.  **Set Mode:** Choose between "Time IN" or "Time OUT".
3.  **Scan:** Click the scanner box and start scanning student IDs.
4.  **Export:** Click "Export Excel" to save the session data.

---
*Developed for the Information Technology Society.*
