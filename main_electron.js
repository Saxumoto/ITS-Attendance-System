const { app, BrowserWindow, ipcMain, dialog, screen } = require('electron');
const path = require('path');
const { initDb, api } = require('./server_api');

let mainWindow = null;

function createWindow() {
    initDb();

    // Dynamically calculate optimal window dimensions based on display work area resolution
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;

    const windowWidth = Math.min(1360, Math.floor(screenWidth * 0.92));
    const windowHeight = Math.min(880, Math.floor(screenHeight * 0.92));

    mainWindow = new BrowserWindow({
        width: windowWidth,
        height: windowHeight,
        minWidth: 1024,
        minHeight: 680,
        center: true,
        title: "ITS Attendance System",
        icon: path.join(__dirname, 'web', 'logo.ico'),
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false
        }
    });

    mainWindow.removeMenu();
    mainWindow.loadFile(path.join(__dirname, 'web', 'index.html'));
}

ipcMain.handle('get_initial_data', async (event, params) => api.getInitialData(params));
ipcMain.handle('get_event_history_py', async (event) => api.getEventHistory());
ipcMain.handle('process_scan_py', async (event, params) => api.processScan(params));
ipcMain.handle('check_period_lock_py', async (event, params) => api.checkPeriodLock(params));
ipcMain.handle('toggle_period_lock_py', async (event, params) => api.togglePeriodLock(params));
ipcMain.handle('register_student_py', async (event, params) => api.registerStudent(params));
ipcMain.handle('delete_log_py', async (event, params) => api.deleteLog(params));
ipcMain.handle('clear_logs_py', async (event, params) => api.clearLogs(params));

ipcMain.handle('export_logs_csv_py', async (event, params) => {
    try {
        const tempRes = await api.exportExcel({ event: params.event, date: params.date, savePath: null });
        const defaultName = tempRes.default_filename || 'Attendance_Report.xlsx';

        const { canceled, filePath } = await dialog.showSaveDialog(mainWindow, {
            title: "Save Attendance Excel Report",
            defaultPath: path.join(require('os').homedir(), 'Desktop', defaultName),
            filters: [
                { name: 'Excel Workbook (*.xlsx)', extensions: ['xlsx'] }
            ]
        });

        if (canceled || !filePath) {
            return { status: "cancelled" };
        }

        const res = await api.exportExcel({ event: params.event, date: params.date, savePath: filePath });
        return { status: "success", message: `Export saved successfully!\nSaved to: ${filePath}`, file_path: filePath };
    } catch (err) {
        return { status: "error", message: `Export failed: ${err.message}` };
    }
});

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});
