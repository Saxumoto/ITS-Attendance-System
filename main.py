import customtkinter as ctk
import sqlite3
from datetime import datetime
import os
import sys
import csv
import winsound
from tkinter import filedialog, messagebox, ttk
from tkcalendar import DateEntry
from PIL import Image

# --- CONFIGURATION ---
ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue") 
THEME_COLOR = "#E0A638" 

class AttendanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("ITS Command Center")
        self.geometry("1280x800")
        self.minsize(1000, 650)
        
        # --- PATH SETUP ---
        if getattr(sys, 'frozen', False):
            self.app_dir = os.path.dirname(sys.executable)
        else:
            self.app_dir = os.path.dirname(os.path.abspath(__file__))

        self.db_name = os.path.join(self.app_dir, 'StudentDatabase.db')
        icon_path = os.path.join(self.app_dir, 'logo.ico')

        try:
            self.iconbitmap(icon_path)
        except:
            pass

        self.setup_database()

        # --- LAYOUT GRID ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= LEFT SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, 
                                    fg_color=("#F0F0F0", "#212121")) 
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(12, weight=1) # Pushes content up

        # HEADER
        self.header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="ew")
        
        try:
            base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else self.app_dir
            logo_path = os.path.join(base_path, "logo.png")
            logo_img = ctk.CTkImage(light_image=Image.open(logo_path),
                                    dark_image=Image.open(logo_path),
                                    size=(35, 35)) 
            self.logo_label = ctk.CTkLabel(self.header_frame, text="  ITS ATTENDANCE", image=logo_img, 
                                         compound="left", font=("Arial Black", 16), text_color=THEME_COLOR)
            self.logo_label.pack(side="left")
        except:
            self.logo_label = ctk.CTkLabel(self.header_frame, text="ITS ATTENDANCE", 
                                         font=("Arial Black", 18), text_color=THEME_COLOR)
            self.logo_label.pack(side="left")

        # Toggle Button
        self.btn_mode = ctk.CTkButton(self.header_frame, text="☾", width=30, height=30, 
                                      fg_color="transparent", text_color=("#333", "#EEE"),
                                      hover_color=("#DDD", "#444"), font=("Arial", 18),
                                      command=self.toggle_mode)
        self.btn_mode.pack(side="right")

        # CONTROLS
        self.add_sidebar_label("ACTIVE DATE", row=1)
        self.cal_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.cal_frame.grid(row=2, column=0, padx=25, sticky="ew")
        
        # Auto-Refresh on Date Change
        self.date_picker = DateEntry(self.cal_frame, width=12, background=THEME_COLOR,
                                     foreground='white', borderwidth=0, date_pattern='y-mm-dd',
                                     font=("Arial", 12))
        self.date_picker.pack(fill="x", ipady=3)
        self.date_picker.bind("<<DateEntrySelected>>", lambda e: self.refresh_table())

        # Load Button
        self.btn_load = ctk.CTkButton(self.sidebar, text="↻ Refresh Data", command=self.refresh_table, 
                                      height=28, fg_color=("#E0E0E0", "#444"), text_color=("black", "white"), hover_color=("#D0D0D0", "#555"))
        self.btn_load.grid(row=3, column=0, padx=25, pady=(10, 10), sticky="ew")

        self.add_sidebar_label("EVENT NAME", row=4)
        self.entry_event = ctk.CTkEntry(self.sidebar, height=28, fg_color=("white", "#333"), text_color=("black", "white"), border_color=("#CCC", "#555"))
        self.entry_event.grid(row=5, column=0, padx=25, sticky="ew")
        self.entry_event.insert(0, "General Event")
        self.entry_event.bind("<Return>", lambda e: self.refresh_table())

        self.add_sidebar_label("CUT-OFF TIME", row=6)
        self.time_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.time_frame.grid(row=7, column=0, padx=25, sticky="ew")
        self.entry_time_limit = ctk.CTkEntry(self.time_frame, height=28, width=100, placeholder_text="10:30", 
                                             fg_color=("white", "#333"), text_color=("black", "white"), border_color=("#CCC", "#555"))
        self.entry_time_limit.pack(side="left", fill="x", expand=True)
        self.chk_use_limit = ctk.CTkCheckBox(self.time_frame, text="On", width=50, fg_color=THEME_COLOR, text_color=("black", "white"))
        self.chk_use_limit.pack(side="left", padx=(10, 0))

        self.add_sidebar_label("SCAN MODE", row=8)
        self.mode_selector = ctk.CTkComboBox(self.sidebar, height=28, values=["Time IN", "Time OUT", "Late", "Custom"], 
                                             fg_color=("white", "#333"), text_color=("black", "white"), 
                                             border_color=("#CCC", "#555"), button_color=("#CCC", "#555"))
        self.mode_selector.grid(row=9, column=0, padx=25, sticky="ew")

        self.btn_export = ctk.CTkButton(self.sidebar, text="⬇ Export Excel", command=self.export_data, 
                                        fg_color=THEME_COLOR, text_color="white", hover_color="#C08B28", font=("Arial", 13, "bold"))
        self.btn_export.grid(row=10, column=0, padx=25, pady=(20, 10), sticky="ew")

        # --- NEW RESET BUTTON ---
        self.btn_reset = ctk.CTkButton(self.sidebar, text="✖ Clear Log", command=self.reset_log, 
                                       height=28, fg_color="#C0392B", hover_color="#E74C3C", text_color="white")
        self.btn_reset.grid(row=11, column=0, padx=25, pady=(0, 20), sticky="ew")

        # 3. LIVE STATS CARD
        self.stats_frame = ctk.CTkFrame(self.sidebar, fg_color=("white", "#1a1a1a"), 
                                        corner_radius=10, border_color=("#DDD", "#333"), border_width=1)
        self.stats_frame.grid(row=13, column=0, padx=20, pady=(0, 20), sticky="ew") 
        
        ctk.CTkLabel(self.stats_frame, text="TOTAL SCANNED", font=("Arial", 9, "bold"), text_color="#888").pack(pady=(12,0))
        self.lbl_total = ctk.CTkLabel(self.stats_frame, text="0", font=("Arial", 30, "bold"), text_color=("#333", "white"))
        self.lbl_total.pack(pady=0)
        self.lbl_breakdown = ctk.CTkLabel(self.stats_frame, text="Waiting...", justify="center", font=("Arial", 11), text_color="#666")
        self.lbl_breakdown.pack(pady=(5, 12), padx=10)


        # ================= RIGHT SIDE =================
        self.right_frame = ctk.CTkFrame(self, fg_color=("white", "#111")) 
        self.right_frame.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1) 
        self.right_frame.grid_rowconfigure(1, weight=1)    

        # 1. SCANNER AREA
        self.scan_area = ctk.CTkFrame(self.right_frame, height=100, fg_color=("#F9F9F9", "#1e1e1e"), 
                                      corner_radius=15, border_color=("#EEE", "#333"), border_width=1)
        self.scan_area.grid(row=0, column=0, sticky="ew", padx=30, pady=25)
        self.scan_area.pack_propagate(False) 

        self.lbl_status = ctk.CTkLabel(self.scan_area, text="Ready...", font=("Arial", 12, "bold"), text_color="#888")
        self.lbl_status.pack(pady=(10, 2)) 
        
        self.entry_scan = ctk.CTkEntry(self.scan_area, height=35, width=250,           
                                       font=("Arial", 18), placeholder_text="Scan ID", justify="center",
                                       fg_color=("white", "#2b2b2b"), text_color=("black", "white"),
                                       border_color=THEME_COLOR, border_width=2)
        self.entry_scan.pack(pady=5) 
        self.entry_scan.bind('<Return>', self.process_scan)
        self.entry_scan.focus()

        # 2. TABLE
        self.table_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical")
        columns = ("timestamp", "id", "name", "year", "mode")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=15, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.pack(side="left", fill="both", expand=True) 
        scrollbar.pack(side="right", fill="y")
        
        self.tree.heading("timestamp", text="TIME")
        self.tree.heading("id", text="STUDENT ID")
        self.tree.heading("name", text="FULL NAME")
        self.tree.heading("year", text="YEAR LEVEL")
        self.tree.heading("mode", text="STATUS")

        self.tree.column("timestamp", width=100, anchor="center")
        self.tree.column("id", width=120, anchor="center")
        self.tree.column("name", width=300, anchor="w")
        self.tree.column("year", width=100, anchor="center")
        self.tree.column("mode", width=120, anchor="center")

        self.update_treeview_style()
        self.refresh_table()

    def add_sidebar_label(self, text, row):
        lbl = ctk.CTkLabel(self.sidebar, text=text, font=("Arial", 11, "bold"), text_color="#888")
        lbl.grid(row=row, column=0, padx=30, pady=(15, 2), sticky="w")

    def toggle_mode(self):
        if ctk.get_appearance_mode() == "Light":
            ctk.set_appearance_mode("Dark")
            self.btn_mode.configure(text="☀") 
        else:
            ctk.set_appearance_mode("Light")
            self.btn_mode.configure(text="☾")
        self.update_treeview_style()

    def update_treeview_style(self):
        mode = ctk.get_appearance_mode()
        style = ttk.Style()
        style.theme_use("default")

        if mode == "Dark":
            bg_color = "#2b2b2b"
            fg_color = "white"
            header_bg = "#111111"
            header_fg = "white"
        else:
            bg_color = "white"
            fg_color = "black"
            header_bg = "#F0F0F0"
            header_fg = "#333333"

        style.configure("Treeview", background=bg_color, foreground=fg_color, 
                        fieldbackground=bg_color, rowheight=40, font=("Arial", 11))
        
        style.configure("Treeview.Heading", background=header_bg, foreground=header_fg, 
                        relief="flat", font=('Arial', 10, 'bold'))
        
        style.map('Treeview', background=[('selected', THEME_COLOR)], foreground=[('selected', 'white')])

    # --- AUDIO FEEDBACK ---
    def play_sound(self, success=True):
        try:
            if success:
                winsound.Beep(1000, 200) 
            else:
                winsound.Beep(400, 500)  
        except:
            pass

    # --- LOGIC ---
    def setup_database(self):
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS event_logs 
                        (id INTEGER PRIMARY KEY, student_id TEXT, mode TEXT, 
                         timestamp TEXT, event_name TEXT, manual_date TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS studentData 
                        (id INTEGER PRIMARY KEY, studentID TEXT UNIQUE, 
                         firstName TEXT, lastName TEXT, yearLevel TEXT)''')
        try: self.c.execute("ALTER TABLE event_logs ADD COLUMN manual_date TEXT")
        except: pass 
        self.conn.commit()

    def check_time_limit(self):
        if self.chk_use_limit.get() == 1:
            limit_str = self.entry_time_limit.get().strip()
            if not limit_str: return True
            try:
                now = datetime.now().time()
                limit_time = datetime.strptime(limit_str, "%H:%M").time()
                if now > limit_time: return False
            except: return True
        return True

    def refresh_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        active_date = self.date_picker.get_date().strftime("%Y-%m-%d")
        event_name = self.entry_event.get().strip()
        
        self.c.execute("SELECT student_id, mode, timestamp FROM event_logs WHERE manual_date=? AND event_name=? ORDER BY timestamp DESC", (active_date, event_name))
        logs = self.c.fetchall()
        
        stats = {}
        total = 0
        for log in logs:
            s_id, mode, ts = log
            fname, year = "Unknown ID", "N/A"
            try:
                self.c.execute("SELECT firstName, lastName, yearLevel FROM studentData WHERE studentID=?", (s_id,))
                r = self.c.fetchone()
                if r: fname, year = f"{r[0]} {r[1]}", str(r[2])
            except: pass
            
            total += 1
            stats[year] = stats.get(year, 0) + 1
            self.tree.insert("", "end", values=(ts.split(' ')[1] if ' ' in ts else ts, s_id, fname, year, mode))
        
        self.lbl_total.configure(text=str(total))
        bd = "\n".join([f"{k}: {v}" for k, v in sorted(stats.items())])
        self.lbl_breakdown.configure(text=bd if bd else "No Data")

    def reset_log(self):
        # --- 3. RESET LOGIC ---
        active_date = self.date_picker.get_date().strftime("%Y-%m-%d")
        event_name = self.entry_event.get().strip()
        
        confirm = messagebox.askyesno("Confirm Reset", 
                                      f"Are you sure you want to DELETE ALL logs for:\n\nDate: {active_date}\nEvent: {event_name}?\n\nThis cannot be undone.")
        if confirm:
            try:
                self.c.execute("DELETE FROM event_logs WHERE manual_date=? AND event_name=?", (active_date, event_name))
                self.conn.commit()
                self.refresh_table()
                self.play_sound(False) # A little sound to indicate "Cleared"
                messagebox.showinfo("Success", "Attendance Log Cleared.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def process_scan(self, event=None):
        sid = self.entry_scan.get().strip()
        mode = self.mode_selector.get()
        evt = self.entry_event.get().strip()
        date = self.date_picker.get_date().strftime("%Y-%m-%d")
        if not sid: return
        
        if not self.check_time_limit():
            self.lbl_status.configure(text="⛔ TIME LIMIT REACHED", text_color="#FF4C4C")
            self.play_sound(False)
            self.entry_scan.delete(0, "end")
            return
        
        self.c.execute("SELECT id FROM studentData WHERE studentID=?", (sid,))
        if self.c.fetchone():
            self.c.execute("SELECT id FROM event_logs WHERE student_id=? AND mode=? AND manual_date=? AND event_name=?", (sid, mode, date, evt))
            if self.c.fetchone(): 
                self.lbl_status.configure(text="⚠ ALREADY SCANNED", text_color="orange")
                self.play_sound(False)
            else:
                self.c.execute("INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date) VALUES (?,?,?,?,?)", 
                               (sid, mode, f"{date} {datetime.now().strftime('%H:%M:%S')}", evt, date))
                self.conn.commit()
                self.lbl_status.configure(text=f"✅ SUCCESS: {sid}", text_color="#27AE60")
                self.play_sound(True)
                self.refresh_table()
        else: 
            self.lbl_status.configure(text="❌ ID NOT FOUND", text_color="#FF4C4C")
            self.play_sound(False)
        self.entry_scan.delete(0, "end")

    def export_data(self):
        # --- NEW SMART EXPORT ---
        date = self.date_picker.get_date().strftime("%Y-%m-%d")
        evt = self.entry_event.get().strip()
        mode = self.mode_selector.get() # Get current mode (Time IN, Time OUT, etc.)

        # Create filename: "Event_Date_Mode.csv"
        clean_evt = "".join([c if c.isalnum() else "_" for c in evt])
        default_name = f"{clean_evt}_{date}_{mode.replace(' ', '')}.csv"

        fn = filedialog.asksaveasfilename(initialfile=default_name, defaultextension=".csv")
        if fn:
            # Filter specifically by Mode, Event, and Date
            self.c.execute("SELECT student_id, mode, timestamp FROM event_logs WHERE manual_date=? AND event_name=? AND mode=? ORDER BY timestamp DESC", (date, evt, mode))
            logs = self.c.fetchall()

            # Prepare CSV with Headers matching the Dashboard
            # ["Time", "Student ID", "Full Name", "Year Level", "Status"]
            export_list = [["Time", "Student ID", "Full Name", "Year Level", "Status"]]

            for log in logs:
                s_id, log_mode, ts = log
                display_time = ts.split(' ')[1] if ' ' in ts else ts
                
                # Fetch Name & Year for the export
                fname, year = "Unknown ID", "N/A"
                try:
                    self.c.execute("SELECT firstName, lastName, yearLevel FROM studentData WHERE studentID=?", (s_id,))
                    r = self.c.fetchone()
                    if r: fname, year = f"{r[0]} {r[1]}", str(r[2])
                except: pass
                
                export_list.append([display_time, s_id, fname, year, log_mode])
            
            # Write to File
            try:
                with open(fn, 'w', newline='') as f: 
                    csv.writer(f).writerows(export_list)
                messagebox.showinfo("Success", f"Export Complete!\nSaved {len(logs)} records for '{mode}'.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")

if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()