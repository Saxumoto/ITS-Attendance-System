# 🎓 ITS Attendance System

> A modern, high-performance **Native Desktop Application** designed for the **Information Technology Society (ITS)** to streamline event check-ins, manage attendance rosters, and automate multi-period Excel matrix reporting.

---

## 📌 System Overview

The **ITS Attendance System** is an offline-capable, desktop attendance solution engineered to handle high-volume student check-ins during organization events, symposiums, and academic assemblies. 

Built on a native **Electron + Node.js** architecture with an embedded **SQLite3** transactional database, the application processes USB barcode scanner inputs and manual name searches in **<0.5ms**, eliminating queues, manual roster tallies, and human errors.

---

## 🎯 Purpose & Mission

1. **⚡ Fast & Queueless Event Check-ins:** Provide instant visual and Web Audio chime feedback to event officers as students scan their barcodes upon entering or leaving.
2. **📂 Automated Multi-Period Attendance Tracking:** Accurately track attendance across 4 distinct event periods:
   - `Morning Time IN`
   - `Morning Time OUT`
   - `Afternoon Time IN`
   - `Afternoon Time OUT`
3. **📊 Dynamic Matrix Excel Reporting:** Generate clean, formatted `.xlsx` matrix reports with smart period filename tagging (`[Event]_[PeriodTag]_[Date].xlsx`) via native Windows `Save As` dialogs.
4. **🛡️ Data Integrity & Operational Reliability:** Prevent duplicate check-ins, resolve unregistered student barcodes, isolate period locks, and safeguard local records with a zero-freeze, WAL-journaled database.

---

## 🛠️ Tech Stack & Architecture

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Desktop Runtime** | **Electron v33.4.11** | Native cross-platform desktop application container running Node.js runtime. |
| **Frontend Framework** | **HTML5, CSS3, ES6+ JS** | Responsive glassmorphism dark/light theme dashboard with CSS Flex/Grid. |
| **Database Engine** | **SQLite3 (WAL Mode)** | Embedded relational database with persistent connection and 5,000ms busy timeout. |
| **Audio Feedback** | **Web Audio API** | Offline synthesized audio chime palette for check-in success, select, delete, warning, and error events. |
| **Excel Generation** | **ExcelJS** | Multi-sheet workbook compilation (`Scanned Attendance Logs`, `Year Level Summary`) with auto column width formatting. |
| **IPC Communication** | **Electron IPC ContextBridge** | Context-isolated, secure Inter-Process Communication bridge between Renderer and Main process. |

---

## 🚀 Key Features

* **⚡ Ultra-Fast Barcode Scanning:** Instant `<0.5ms` response time for barcode scanners and manual ID inputs.
* **🔎 Name Search Selection Modal:** Partial keyboard searches (e.g., `"Abad"`) automatically open an interactive popup modal listing all matching candidate profiles for 1-click selection.
* **📂 Live Dashboard Folder Tabs:** Interactive period tabs (`📂 All Periods`, `☀️ Morning IN`, `🌅 Morning OUT`, `🌤️ Afternoon IN`, `🌙 Afternoon OUT`) allow operators to view period-specific rosters without mixing logs.
* **🔒 Period Lock System:** Per-period lock isolation prevents accidental scans or registry entries for closed sessions while keeping open sessions active.
* **➕ Event Session Management:** 
  - **`+ New Event`**: Start clean event sessions with custom titles and dates.
  - **`Refresh System`**: 1-click reset to default `General Event` on today's date.
  - **`Past Event Logs`**: Interactive history modal listing all past database event sessions with 1-click roster restoration.
* **💾 Windows Native `Save As` Export:** 
  - Opens Windows file dialog pre-filled with smart period tags (`JUMPSTART_DAY_2_Complete_2026-08-28.xlsx`).
  - Exports **only actually scanned students** to keep reports concise and clean.
* **💻 Responsive Display Scaling:** Dynamically adapts layout and padding for all laptop screen sizes (`1366x768`, `1920x1080`, high-DPI scaling) to ensure buttons never overlay.

---

## 📥 Installation & Running Locally

### Prerequisites
* [Node.js](https://nodejs.org/) (v18 or higher)
* npm (Node Package Manager)

### Running from Source
1. Clone the GitHub repository:
   ```bash
   git clone https://github.com/Saxumoto/ITS-Attendance-System.git
   cd ITS-Attendance-System
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Launch the application in Electron development mode:
   ```bash
   npx electron .
   ```

4. Build standalone Windows executable release:
   ```bash
   npx electron-builder --dir
   ```

---

## 📦 Standalone Release (Zero Installation Required)

For non-developer deployment, the pre-packaged standalone release folder is located at:
```text
ITS Attendance System - Final Standalone Release/
```
* **`ITS Attendance System.exe`** — Standalone desktop executable (runs on any Windows PC without setup).
* **`Create Desktop Shortcut.bat`** — 1-click script to place a launch icon directly on your Desktop screen.

---

*Developed for the Information Technology Society (ITS).*
