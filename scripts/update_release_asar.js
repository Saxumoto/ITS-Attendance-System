const asar = require('@electron/asar');
const fs = require('fs');
const path = require('path');

async function main() {
    const root = 'C:/DESKTOP FILES/ITS-Attendance-System';
    const tempDir = path.join(root, 'temp_asar_extract');

    if (!fs.existsSync(tempDir)) {
        console.log('Extracting asar from release...');
        const srcAsar = 'C:/DESKTOP FILES/ITS-Attendance-System/release/ITS Attendance System/resources/app.asar';
        asar.extractAll(srcAsar, tempDir);
    }

    console.log('Syncing updated web/index.html and server_api.js into extracted asar tree...');
    fs.copyFileSync(path.join(root, 'web/index.html'), path.join(tempDir, 'web/index.html'));
    fs.copyFileSync(path.join(root, 'server_api.js'), path.join(tempDir, 'server_api.js'));

    const targets = [
        'C:/DESKTOP FILES/ITS-Attendance-System/release/ITS Attendance System/resources/app.asar',
        'C:/DESKTOP FILES/ITS Attendance System - Final Standalone Release/resources/app.asar'
    ];

    for (const target of targets) {
        console.log(`Packing into ${target}...`);
        await asar.createPackageWithOptions(tempDir, target, { unpack: '**/*.node' });
        console.log(`Updated ${target} (${fs.statSync(target).size} bytes)`);
    }

    console.log('Cleaning up temp directory...');
    fs.rmSync(tempDir, { recursive: true, force: true });
    if (fs.existsSync(path.join(root, 'test_app.asar'))) {
        fs.unlinkSync(path.join(root, 'test_app.asar'));
    }
    console.log('Done updating release asar packages!');
}

main().catch(err => {
    console.error('Build error:', err);
    process.exit(1);
});
