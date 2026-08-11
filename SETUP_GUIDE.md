# 🖥️ ITS Attendance System — Setup & Installation Guide

This guide explains how to install and run the **ITS Attendance System** on any Windows laptop.

There are **two ways** to run the system — choose whichever is easier:

---

## 🟢 OPTION A — Run the Standalone App (Recommended, No Installation Needed)

This is the easiest method. Just copy and launch — no Python, no CMD required.

### What you need:
- **Windows 10 or 11** (64-bit)
- **Google Chrome** installed (required for the app window to open)

### Steps:

1. **Copy** the `ITS-Attendance-System` folder to the target laptop  
   (via USB flash drive, Google Drive, or OneDrive)

2. Make sure the folder contains these **two required files**:
   ```
   ITS-Attendance-System/
   ├── ITS Attendance System.exe   ← the app launcher
   ├── StudentDatabase.db          ← the student roster database
   └── web/                        ← UI files (do not delete)
   ```

   > ⚠️ **Both the `.exe` and `StudentDatabase.db` must be in the same folder.**
   > The app will not find the student list without the database file.

3. **Double-click** `ITS Attendance System.exe` to launch the system.

4. Chrome will open automatically in app mode showing the dashboard.

> 💡 **Tip:** You can right-click the `.exe` and choose **"Send to → Desktop (create shortcut)"** for one-click access from the desktop.

---

## 🔵 OPTION B — Run from Source Code (Developers Only)

Use this method only if you need to modify or develop the system.

### Requirements:
- **Python 3.10 or later** installed with **"Add to PATH"** checked during setup
- **Google Chrome** installed

### Steps:

1. **Install Python** from https://www.python.org/downloads/  
   ⚠️ On the installer's first screen, make sure to tick **"Add Python to PATH"** before clicking Install.

2. Copy the full `ITS-Attendance-System` folder to the laptop.

3. Open the project folder, click the **address bar**, type `cmd`, and press **Enter**.

4. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

5. Install dependencies:
   ```
   pip install eel pandas openpyxl
   ```

6. Launch the app:
   ```
   python main.py
   ```

#### Optional — One-Click Launch Batch File:
1. Open **Notepad** and paste:
   ```
   @echo off
   cd /d "%~dp0"
   call venv\Scripts\activate
   python main.py
   ```
2. Save as **`Launch ITS Attendance.bat`** (set file type to **All Files** in Notepad's save dialog)
3. Double-click the `.bat` file to launch anytime.

---

## ❓ Troubleshooting

| Problem | Solution |
|---|---|
| App won't open / nothing happens | Make sure **Google Chrome** is installed |
| "StudentDatabase.db not found" error | Place `StudentDatabase.db` in the same folder as the `.exe` |
| App opens but student list is empty | The `StudentDatabase.db` may be empty — use the seeded one from the original source |
| Blank white screen | Close and reopen the `.exe` |
| `python` not recognized (Option B) | Reinstall Python and tick "Add Python to PATH" |
| `ModuleNotFoundError` (Option B) | Run `pip install eel pandas openpyxl` again inside the venv |

---

## 📁 Files to Always Keep Together

When sharing or copying the system to another laptop, always bring:

| File / Folder | Purpose |
|---|---|
| `ITS Attendance System.exe` | The main app launcher |
| `StudentDatabase.db` | Official student master list + all attendance logs |
| `web/` folder | UI assets (html, logo) — required by the exe |

---

## 📞 Support

For issues, contact the system developer or the ITS Technical Committee.

---
*ITS Attendance System — Internal Use Only*
