const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    getInitialData: (params) => ipcRenderer.invoke('get_initial_data', params),
    getEventHistory: () => ipcRenderer.invoke('get_event_history_py'),
    processScan: (params) => ipcRenderer.invoke('process_scan_py', params),
    checkPeriodLock: (params) => ipcRenderer.invoke('check_period_lock_py', params),
    togglePeriodLock: (params) => ipcRenderer.invoke('toggle_period_lock_py', params),
    registerStudent: (params) => ipcRenderer.invoke('register_student_py', params),
    deleteLog: (params) => ipcRenderer.invoke('delete_log_py', params),
    clearLogs: (params) => ipcRenderer.invoke('clear_logs_py', params),
    exportExcel: (params) => ipcRenderer.invoke('export_logs_csv_py', params)
});
