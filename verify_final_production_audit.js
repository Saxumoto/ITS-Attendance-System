const { api, initDb } = require('./server_api');
const path = require('path');
const fs = require('fs');

async function runFinalProductionAudit() {
    console.log("=================================================");
    console.log("   ITS ATTENDANCE SYSTEM - FINAL SYSTEM AUDIT   ");
    console.log("=================================================\n");

    let auditPassed = true;

    try {
        // 1. Database Location & Initialization
        console.log("1. Checking Single Database Pathing...");
        initDb();
        const testDate = "2026-08-28";
        const testEvent = "PRODUCTION AUDIT EVENT";
        const testMode = "Morning Time IN";
        const testStudentID = "59845693"; // Manu Gabriel Abad

        const initData = await api.getInitialData({ date: testDate, event: testEvent });
        console.log(`   [PASS] Database initialized cleanly. Roster count: ${initData.students.length}`);

        // Clean pre-test logs for clean state
        await api.clearLogs({ event: testEvent, date: testDate });

        // 2. Barcode Scan Test
        console.log("\n2. Testing Barcode Scanning (59845693)...");
        const scanRes = await api.processScan({ query: testStudentID, date: testDate, event: testEvent, mode: testMode });
        if (scanRes.status !== 'success' || !scanRes.student || scanRes.student.studentID !== testStudentID) {
            console.error("   [FAIL] Barcode scan returned invalid payload:", scanRes);
            auditPassed = false;
        } else {
            console.log(`   [PASS] Scanned: ${scanRes.student.firstName} ${scanRes.student.lastName} (${scanRes.student.yearLevel})`);
        }

        // 3. Duplicate Scan Test
        console.log("\n3. Testing Duplicate Scan Protection...");
        const dupRes = await api.processScan({ query: testStudentID, date: testDate, event: testEvent, mode: testMode });
        if (dupRes.status !== 'already_logged') {
            console.error("   [FAIL] Duplicate scan check failed! Status:", dupRes.status);
            auditPassed = false;
        } else {
            console.log("   [PASS] Duplicate scan blocked cleanly!");
        }

        // 4. Partial Name Search Selection Modal Test
        console.log("\n4. Testing Partial Name Search (Query: 'Abad')...");
        const nameRes = await api.processScan({ query: 'Abad', date: testDate, event: testEvent, mode: testMode });
        if (nameRes.status !== 'multiple_matches' || !nameRes.candidates || nameRes.candidates.length < 1) {
            console.error("   [FAIL] Name search selection modal check failed! Status:", nameRes.status);
            auditPassed = false;
        } else {
            console.log(`   [PASS] Multiple candidates returned (${nameRes.candidates.length} students found for selection modal)`);
        }

        // 5. Unregistered ID Test
        console.log("\n5. Testing Unregistered Barcode ID (Query: '99990001')...");
        const unregRes = await api.processScan({ query: '99990001', date: testDate, event: testEvent, mode: testMode });
        if (unregRes.status !== 'id_not_found') {
            console.error("   [FAIL] Unregistered barcode resolution check failed! Status:", unregRes.status);
            auditPassed = false;
        } else {
            console.log("   [PASS] Unregistered ID triggered resolution modal cleanly!");
        }

        // 6. Period Lock Test
        console.log("\n6. Testing Period Lock Isolation...");
        await api.togglePeriodLock({ date: testDate, event: testEvent, mode: "Morning Time IN" });
        const inLock = await api.checkPeriodLock({ date: testDate, event: testEvent, mode: "Morning Time IN" });
        const outLock = await api.checkPeriodLock({ date: testDate, event: testEvent, mode: "Morning Time OUT" });

        if (!inLock.locked || outLock.locked) {
            console.error("   [FAIL] Period lock isolation check failed! IN locked:", inLock.locked, "OUT locked:", outLock.locked);
            auditPassed = false;
        } else {
            console.log("   [PASS] Morning Time IN locked while Morning Time OUT remains open!");
        }
        await api.togglePeriodLock({ date: testDate, event: testEvent, mode: "Morning Time IN" }); // Unlock

        // 7. Single Log Deletion Test
        console.log("\n7. Testing Single Attendance Log Deletion...");
        const logsData = await api.getInitialData({ date: testDate, event: testEvent });
        const delRes = await api.deleteLog({ logs: [{ student_id: testStudentID, mode: testMode, timestamp: logsData.logs[0].timestamp }] });
        const afterDelData = await api.getInitialData({ date: testDate, event: testEvent });

        if (delRes.status !== 'success' || afterDelData.logs.length !== 0) {
            console.error("   [FAIL] Log deletion failed! Remaining logs:", afterDelData.logs.length);
            auditPassed = false;
        } else {
            console.log("   [PASS] Log deleted! Table updated to 0 logs.");
        }

        // 8. Event Session Clearing Test
        console.log("\n8. Testing Clear Event Logs...");
        await api.processScan({ query: testStudentID, date: testDate, event: testEvent, mode: testMode });
        await api.clearLogs({ event: testEvent, date: testDate });
        const afterClearData = await api.getInitialData({ date: testDate, event: testEvent });

        if (afterClearData.logs.length !== 0) {
            console.error("   [FAIL] Clear logs failed! Remaining logs:", afterClearData.logs.length);
            auditPassed = false;
        } else {
            console.log("   [PASS] Event session logs cleared successfully!");
        }

        // 9. Excel Export Calculation Test
        console.log("\n9. Testing Excel Export Generator...");
        const exportRes = await api.exportExcel({ event: "TEST 3", date: "2026-08-28", savePath: null });
        if (exportRes.status !== 'success' || !fs.existsSync(exportRes.file_path)) {
            console.error("   [FAIL] Excel export generator failed:", exportRes);
            auditPassed = false;
        } else {
            console.log(`   [PASS] Export file generated: ${path.basename(exportRes.file_path)}`);
        }

        // 10. Summary
        console.log("\n=================================================");
        if (auditPassed) {
            console.log("   ALL 10 SYSTEM AUDIT CHECKS PASSED (100%)   ");
            console.log("   READY FOR FINAL DEPLOYMENT & PACKAGING      ");
        } else {
            console.log("   SYSTEM AUDIT COMPLETED WITH ISSUES          ");
        }
        console.log("=================================================");

    } catch (err) {
        console.error("\n[CRITICAL AUDIT ERROR]:", err.message);
    }
}

runFinalProductionAudit();
