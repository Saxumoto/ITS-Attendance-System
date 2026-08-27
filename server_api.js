const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');
const { app, shell } = require('electron');
const ExcelJS = require('exceljs');

const DB_NAME = 'StudentDatabase.db';

function getDbPath() {
    if (process.execPath) {
        const exeDir = path.dirname(process.execPath);
        const exeDb = path.join(exeDir, DB_NAME);
        if (fs.existsSync(exeDb)) return exeDb;
    }
    const rootPath = path.join('C:\\DESKTOP FILES\\ITS-Attendance-System', DB_NAME);
    if (fs.existsSync(rootPath)) return rootPath;
    return path.join(__dirname, DB_NAME);
}

let persistentDb = null;

function getDbConnection() {
    if (!persistentDb) {
        const dbPath = getDbPath();
        persistentDb = new sqlite3.Database(dbPath);
        persistentDb.configure("busyTimeout", 5000);
        persistentDb.run("PRAGMA journal_mode=WAL;");
        persistentDb.run("PRAGMA synchronous=NORMAL;");
        persistentDb.run("PRAGMA foreign_keys=ON;");
    }
    return persistentDb;
}

function initDb() {
    const db = getDbConnection();
    db.serialize(() => {
        db.run(`CREATE TABLE IF NOT EXISTS studentData 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 studentID TEXT UNIQUE NOT NULL, 
                 firstName TEXT NOT NULL, 
                 lastName TEXT NOT NULL, 
                 yearLevel TEXT NOT NULL, 
                 regType TEXT DEFAULT 'EXISTING')`);

        db.run(`CREATE TABLE IF NOT EXISTS event_logs 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 student_id TEXT NOT NULL, 
                 mode TEXT NOT NULL, 
                 timestamp TEXT NOT NULL, 
                 event_name TEXT NOT NULL, 
                 manual_date TEXT NOT NULL,
                 FOREIGN KEY (student_id) REFERENCES studentData(studentID) ON DELETE CASCADE ON UPDATE CASCADE)`);

        db.run(`CREATE TABLE IF NOT EXISTS closed_periods 
                (event_name TEXT NOT NULL, 
                 manual_date TEXT NOT NULL, 
                 mode TEXT NOT NULL, 
                 PRIMARY KEY (event_name, manual_date, mode))`);

        db.run(`CREATE TABLE IF NOT EXISTS app_settings 
                (key TEXT PRIMARY KEY, value TEXT)`);

        db.run("CREATE INDEX IF NOT EXISTS idx_student_id ON studentData(studentID);");
        db.run("CREATE INDEX IF NOT EXISTS idx_student_name ON studentData(lastName, firstName);");
        db.run("CREATE INDEX IF NOT EXISTS idx_logs_student ON event_logs(student_id);");
        db.run("CREATE INDEX IF NOT EXISTS idx_logs_event_date ON event_logs(event_name, manual_date);");
    });
}

function queryDb(sql, params = []) {
    return new Promise((resolve, reject) => {
        const db = getDbConnection();
        db.all(sql, params, (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
}

function runDb(sql, params = []) {
    return new Promise((resolve, reject) => {
        const db = getDbConnection();
        db.run(sql, params, function (err) {
            if (err) reject(err);
            else resolve(this);
        });
    });
}

const api = {
    async getInitialData(params) {
        const event = params.event || 'JUMPSTART DAY 2';
        const date = params.date || new Date().toISOString().split('T')[0];

        const students = await queryDb("SELECT studentID, firstName, lastName, yearLevel, regType FROM studentData");

        const rawLogs = await queryDb(`
            SELECT el.id, el.student_id, sd.firstName, sd.lastName, sd.yearLevel, el.mode, el.timestamp
            FROM event_logs el
            JOIN studentData sd ON el.student_id = sd.studentID
            WHERE el.manual_date=? AND el.event_name=?
            ORDER BY el.id DESC
        `, [date, event]);

        const logs = rawLogs.map(l => ({
            id: l.id,
            studentID: l.student_id,
            firstName: l.firstName,
            lastName: l.lastName,
            yearLevel: l.yearLevel,
            mode: l.mode,
            timestamp: l.timestamp
        }));

        const closedRows = await queryDb("SELECT mode FROM closed_periods WHERE event_name=? AND manual_date=?", [event, date]);
        const closedModes = closedRows.map(r => r.mode);

        return {
            status: "success",
            activeEvent: event,
            activeDate: date,
            event_name: event,
            manual_date: date,
            students: students,
            logs: logs,
            closed_modes: closedModes
        };
    },

    async getEventHistory() {
        const history = await queryDb(`
            SELECT event_name, manual_date, COUNT(DISTINCT student_id) as total_scans, COUNT(*) as total_logs 
            FROM event_logs 
            GROUP BY event_name, manual_date 
            ORDER BY manual_date DESC, id DESC
        `);
        return { status: "success", history: history };
    },

    async processScan(params) {
        const { query, date, event, mode } = params;
        if (!query) return { status: "error", message: "Empty query" };

        const now = new Date();
        const timeStr = `${date} ${now.toTimeString().split(' ')[0]}`;

        const exactMatch = await queryDb("SELECT studentID, firstName, lastName, yearLevel FROM studentData WHERE studentID=?", [query]);

        if (exactMatch.length > 0) {
            const student = exactMatch[0];
            const existing = await queryDb("SELECT id FROM event_logs WHERE student_id=? AND mode=? AND manual_date=? AND event_name=?", [student.studentID, mode, date, event]);

            if (existing.length > 0) {
                return { status: "already_logged", student: { studentID: student.studentID, firstName: student.firstName, lastName: student.lastName, yearLevel: student.yearLevel } };
            } else {
                await runDb("INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date) VALUES (?,?,?,?,?)", [student.studentID, mode, timeStr, event, date]);
                return { status: "success", student: { studentID: student.studentID, firstName: student.firstName, lastName: student.lastName, yearLevel: student.yearLevel } };
            }
        } else {
            const queryStr = `%${query}%`;
            const candidates = await queryDb("SELECT studentID, firstName, lastName, yearLevel FROM studentData WHERE lastName LIKE ? OR firstName LIKE ?", [queryStr, queryStr]);

            if (candidates.length === 1) {
                const cand = candidates[0];
                const existing = await queryDb("SELECT id FROM event_logs WHERE student_id=? AND mode=? AND manual_date=? AND event_name=?", [cand.studentID, mode, date, event]);

                if (existing.length > 0) {
                    return { status: "already_logged", student: { studentID: cand.studentID, firstName: cand.firstName, lastName: cand.lastName, yearLevel: cand.yearLevel } };
                } else {
                    await runDb("INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date) VALUES (?,?,?,?,?)", [cand.studentID, mode, timeStr, event, date]);
                    return { status: "success", student: { studentID: cand.studentID, firstName: cand.firstName, lastName: cand.lastName, yearLevel: cand.yearLevel } };
                }
            } else if (candidates.length > 1) {
                return { status: "multiple_matches", candidates: candidates, query: query };
            } else {
                const isNumeric = /^\d+$/.test(query);
                if (isNumeric) {
                    return { status: "id_not_found", query: query };
                } else {
                    return { status: "not_found", query: query };
                }
            }
        }
    },

    async checkPeriodLock(params) {
        const { date, event, mode } = params;
        const rows = await queryDb("SELECT 1 FROM closed_periods WHERE event_name=? AND manual_date=? AND mode=?", [event, date, mode]);
        return { status: "success", locked: rows.length > 0 };
    },

    async togglePeriodLock(params) {
        const { date, event, mode } = params;
        const existing = await queryDb("SELECT 1 FROM closed_periods WHERE event_name=? AND manual_date=? AND mode=?", [event, date, mode]);
        let lockStatus = "";
        if (existing.length > 0) {
            await runDb("DELETE FROM closed_periods WHERE event_name=? AND manual_date=? AND mode=?", [event, date, mode]);
            lockStatus = "unlocked";
        } else {
            await runDb("INSERT INTO closed_periods (event_name, manual_date, mode) VALUES (?,?,?)", [event, date, mode]);
            lockStatus = "locked";
        }
        return { status: "success", lock_status: lockStatus };
    },

    async registerStudent(params) {
        const { student_id, first_name, last_name, year_level, reg_type, mode, date, event } = params;
        const now = new Date();
        const timeStr = `${date} ${now.toTimeString().split(' ')[0]}`;

        await runDb("INSERT INTO studentData (studentID, firstName, lastName, yearLevel, regType) VALUES (?,?,?,?,?)",
            [student_id, first_name, last_name, year_level, reg_type || 'TRANSFEREE']);

        await runDb("INSERT INTO event_logs (student_id, mode, timestamp, event_name, manual_date) VALUES (?,?,?,?,?)",
            [student_id, mode, timeStr, event, date]);

        return { status: "success", student_name: `${first_name} ${last_name}` };
    },

    async deleteLog(params) {
        let count = 0;
        if (Array.isArray(params.logs)) {
            for (const log of params.logs) {
                await runDb("DELETE FROM event_logs WHERE student_id=? AND mode=? AND timestamp=?", [log.student_id, log.mode, log.timestamp]);
                count++;
            }
        } else if (params.log_id) {
            await runDb("DELETE FROM event_logs WHERE id=?", [params.log_id]);
            count = 1;
        } else if (params.student_id) {
            await runDb("DELETE FROM event_logs WHERE student_id=? AND mode=? AND manual_date=?", [params.student_id, params.mode, params.date]);
            count = 1;
        }
        return { status: "success", count: count };
    },

    async clearLogs(params) {
        const evt = params.event || params.event_name;
        const dt = params.date || params.manual_date;
        await runDb("DELETE FROM event_logs WHERE event_name=? AND manual_date=?", [evt, dt]);
        return { status: "success" };
    },

    async exportExcel(params) {
        const { event, date, savePath } = params;
        const students = await queryDb("SELECT studentID, firstName, lastName, yearLevel, regType FROM studentData ORDER BY lastName ASC");

        // Calculate Smart Period Tag
        const loggedModesRows = await queryDb("SELECT DISTINCT mode FROM event_logs WHERE event_name=? AND manual_date=?", [event, date]);
        const activeModes = new Set(loggedModesRows.map(r => r.mode));

        let periodTag = "Complete";
        const hasMorningIn = activeModes.has("Morning Time IN");
        const hasMorningOut = activeModes.has("Morning Time OUT");
        const hasAfternoonIn = activeModes.has("Afternoon Time IN");
        const hasAfternoonOut = activeModes.has("Afternoon Time OUT");

        const hasMorning = hasMorningIn || hasMorningOut;
        const hasAfternoon = hasAfternoonIn || hasAfternoonOut;

        if (hasMorning && hasAfternoon) {
            periodTag = "Complete";
        } else if (hasMorningIn && hasMorningOut) {
            periodTag = "Morning_IN_and_OUT";
        } else if (hasAfternoonIn && hasAfternoonOut) {
            periodTag = "Afternoon_IN_and_OUT";
        } else if (hasMorningIn) {
            periodTag = "Morning_Time_IN";
        } else if (hasMorningOut) {
            periodTag = "Morning_Time_OUT";
        } else if (hasAfternoonIn) {
            periodTag = "Afternoon_Time_IN";
        } else if (hasAfternoonOut) {
            periodTag = "Afternoon_Time_OUT";
        } else {
            periodTag = "Complete";
        }

        const cleanEvt = (event || 'Event').replace(/[^a-zA-Z0-9]/g, '_');
        const defaultFileName = `${cleanEvt}_${periodTag}_${date}.xlsx`;

        let fn = savePath;
        if (!fn) {
            const desktopPath = path.join(require('os').homedir(), 'Desktop', 'ITS_Attendance_Exports');
            fs.mkdirSync(desktopPath, { recursive: true });
            fn = path.join(desktopPath, defaultFileName);
        }

        const workbook = new ExcelJS.Workbook();

        // Sheet 1: Consolidated Attendance
        const sheet1 = workbook.addWorksheet('Consolidated Attendance');
        sheet1.addRow(["Student ID", "Full Name", "Year Level", "Reg Type", "Morning IN", "Morning OUT", "Afternoon IN", "Afternoon OUT"]);

        const modes = ["Morning Time IN", "Morning Time OUT", "Afternoon Time IN", "Afternoon Time OUT"];
        const yearStats = { "1st Year": { total: 0, present: 0 }, "2nd Year": { total: 0, present: 0 }, "3rd Year": { total: 0, present: 0 }, "4th Year": { total: 0, present: 0 } };
        const absentees = [["Student ID", "Full Name", "Year Level", "Reg Type"]];

        for (const s of students) {
            const fname = `${s.lastName.toUpperCase()}, ${s.firstName}`;
            if (yearStats[s.yearLevel]) yearStats[s.yearLevel].total++;

            let hasScan = false;
            const timestamps = [];

            for (const m of modes) {
                const logs = await queryDb("SELECT timestamp FROM event_logs WHERE CAST(student_id AS TEXT) = CAST(? AS TEXT) AND TRIM(manual_date) = TRIM(?) AND TRIM(event_name) = TRIM(?) AND mode=?", [s.studentID, date, event, m]);
                if (logs.length > 0) {
                    hasScan = true;
                    const ts = logs[0].timestamp;
                    timestamps.push(ts.includes(' ') ? ts.split(' ')[1] : ts);
                } else {
                    timestamps.push("-");
                }
            }

            if (hasScan) {
                if (yearStats[s.yearLevel]) yearStats[s.yearLevel].present++;
                sheet1.addRow([s.studentID, fname, s.yearLevel, s.regType || "EXISTING", ...timestamps]);
            }
        }

        // Sheet 2: Summary Stats
        const sheet2 = workbook.addWorksheet('Year Level Summary');
        sheet2.addRow(["Year Level", "Total Enrolled", "Total Attended", "Attendance Rate (%)"]);
        for (const [yLevel, stat] of Object.entries(yearStats)) {
            const rate = stat.total > 0 ? ((stat.present / stat.total) * 100).toFixed(1) + '%' : '0.0%';
            sheet2.addRow([yLevel, stat.total, stat.present, rate]);
        }

        // Auto column width formatting
        [sheet1, sheet2].forEach(ws => {
            ws.columns.forEach(col => {
                let maxLen = 14;
                col.eachCell({ includeEmpty: true }, cell => {
                    const len = (cell.value || '').toString().length;
                    if (len > maxLen) maxLen = len;
                });
                col.width = maxLen + 4;
            });
        });

        await workbook.xlsx.writeFile(fn);

        try {
            shell.showItemInFolder(fn);
        } catch (e) {}

        return { status: "success", file_path: fn, default_filename: defaultFileName, period_tag: periodTag };
    }
};

module.exports = { initDb, api };
