# 🛡️ File Protector - Complete User Guide

## Table of Contents
1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [User Interface Guide](#user-interface-guide)
4. [Use Cases](#use-cases)
5. [Test Scenarios](#test-scenarios)
6. [Troubleshooting](#troubleshooting)

---

## Overview

**File Protector** is a comprehensive file monitoring and backup system that:
- Monitors multiple folders/drives for file changes
- Creates instant backups when files are modified or deleted
- Uploads backups to MongoDB Atlas cloud storage
- Provides a modern web interface for monitoring and management

### Key Features
- ✅ Real-time file monitoring
- ✅ Multiple folder monitoring
- ✅ Automatic local backups
- ✅ Cloud storage (MongoDB Atlas)
- ✅ File recovery from cloud
- ✅ System logs
- ✅ Dashboard with statistics

---

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- Node.js 14 or higher
- MongoDB Atlas account (free tier available)
- Windows OS (for file monitoring)

### Step 1: Install Backend Dependencies

1. Open terminal/command prompt in the `backend` folder
2. Run:
```bash
pip install -r requirements.txt
```

This installs:
- Flask (web server)
- Flask-CORS (cross-origin support)
- PyMongo (MongoDB driver)
- Watchdog (file monitoring)
- GridFS (file storage)

### Step 2: Install Frontend Dependencies

1. Open terminal in the `frontend` folder
2. Run:
```bash
npm install
```

This installs:
- React
- React DOM
- Axios (API calls)
- Tailwind CSS

### Step 3: Configure MongoDB

1. Go to https://www.mongodb.com/atlas
2. Create a free account
3. Create a cluster (free tier)
4. Get your connection string
5. Update `backend/api.py` and `backend/file_protector2.py`:
   - Replace `MONGO_URI` with your connection string
   - Format: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`

### Step 4: Start the Application

**Option A: Manual Start (Two Terminal Windows)**

**Terminal 1 - Backend:**
```bash
cd backend
python api.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

**Option B: Create Batch Files (Windows)**

Create `start.bat` in project root:
```batch
@echo off
echo Starting Backend...
start "Backend" cmd /k "cd backend && python api.py"
timeout /t 3 /nobreak >nul
echo Starting Frontend...
start "Frontend" cmd /k "cd frontend && npm start"
echo Both servers starting!
pause
```

### Step 5: Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

---

## User Interface Guide

### Dashboard Tab 📊

**Quick Actions (Top Section)**
- **▶️ Start Monitoring**: Start watching folders for changes
- **⏸️ Stop Monitoring**: Stop the monitoring service
- **☁️ Upload to Cloud**: Manually trigger cloud backup
- **🔄 Refresh Status**: Reload system information

**System Status**
- **Monitoring Status**: Shows if monitoring is active
- **Internet Connection**: Connectivity status
- **Monitor Folders**: Number of folders being watched
- **Backup Folder**: Status of backup location

**Backup Statistics**
- **Local Backups**: Count of files in backup folder
- **Cloud Backups**: Count of files in MongoDB

**Current Configuration**
- Lists all monitored folders
- Shows backup folder location

---

### Settings Tab ⚙️

**Monitor Folders Section**

**Adding a Monitor Folder:**
1. Enter folder path (e.g., `C:\Users\YourName\Documents`)
2. Click "➕ Add" button
3. System validates the folder exists
4. Folder appears in "Currently Monitored Folders" list

**Removing a Monitor Folder:**
1. Find the folder in the list
2. Click "🗑️ Remove" button
3. Confirm removal

**⚠️ Root Drive Warning:**
If you try to add C:\ or D:\ root, you'll get a warning about backing up system files.

**Backup Folder Section**
1. Enter or update backup folder path
2. Click "💾 Save" button
3. All backups go to this central location

---

### Backups Tab 💾

**Two Tabs:**
- **💾 Local Backups**: Files stored on your computer
- **☁️ Cloud Backups**: Files in MongoDB Atlas

**Local Backups:**
- Shows all backup files
- Displays file size and modification date
- Files are named with suffixes:
  - `_modified` - File was changed
  - `_deleted` - File was deleted

**Cloud Backups:**
- Shows files uploaded to MongoDB
- Click "⬇️ Download" to retrieve files
- Downloads save to backup folder
- Use for disaster recovery

---

### Logs Tab 📋

**Auto-refresh Toggle:**
- Enable/disable automatic log updates (every 3 seconds)

**Buttons:**
- **🔄 Refresh**: Manually reload logs
- **🗑️ Clear Display**: Clear visible logs (will repopulate on next event)

**Log Types:**
- **ℹ️ INFO**: General information
- **✅ SUCCESS**: Successful operations
- **⚠️ WARNING**: Warning messages
- **❌ ERROR**: Errors requiring attention

**Log Colors:**
- Blue border: Info
- Green border: Success
- Yellow border: Warning
- Red border: Error

---

## Use Cases

### 1. Document Protection
**Scenario**: Protect important documents from accidental deletion
- Add folder: `C:\Users\YourName\Documents`
- System backs up every change
- If file deleted, recovery copy available

### 2. Project Backup
**Scenario**: Automatic backup of code projects
- Add folder: `C:\Projects\YourProject`
- Every code change creates a backup
- Historical versions maintained

### 3. Desktop Monitoring
**Scenario**: Protect files on desktop
- Add folder: `C:\Users\YourName\Desktop`
- All desktop files automatically backed up
- Prevents data loss from accidental deletion

### 4. Multiple Folder Protection
**Scenario**: Protect multiple important locations
- Add: Documents folder
- Add: Desktop folder
- Add: Downloads folder
- Add: Projects folder
- All monitored simultaneously

### 5. Cloud Disaster Recovery
**Scenario**: Recover files if computer fails
- Files backed up locally
- Files uploaded to cloud (MongoDB)
- If computer crashes, download from cloud
- Full file recovery possible

### 6. Entire Drive Monitoring
**Scenario**: Monitor everything on a drive
- Add folder: `D:\`
- All files on D: drive backed up
- Use with caution (creates many backups)

---

## Test Scenarios

### Test 1: Basic File Monitoring

**Steps:**
1. Start the backend server
2. Start the frontend server
3. Open http://localhost:3000
4. Go to Settings tab
5. Add monitor folder: `C:\Users\YourName\Desktop`
6. Set backup folder: `C:\Users\YourName\Backups`
7. Go to Dashboard
8. Click "▶️ Start Monitoring"
9. Create a test file on Desktop: `test.txt`
10. Modify the file
11. Check Backups tab - should see `test.txt_modified`
12. Delete the file
13. Check Backups tab - should see `test.txt_deleted`

**Expected Results:**
- ✅ System status shows "Active"
- ✅ Backup files created
- ✅ Logs show backup events
- ✅ File recovery possible

---

### Test 2: Cloud Upload and Download

**Steps:**
1. Ensure monitoring is started
2. Add several files to monitored folder
3. Wait for them to be backed up
4. On Dashboard, click "☁️ Upload to Cloud"
5. Go to Backups tab
6. Click "☁️ Cloud Backups"
7. Verify files listed
8. Click "⬇️ Download" on a file
9. Check backup folder for downloaded file

**Expected Results:**
- ✅ Files uploaded to cloud
- ✅ Files listed in cloud backups
- ✅ Download retrieves complete file
- ✅ File exists in backup folder

---

### Test 3: Multiple Folder Monitoring

**Steps:**
1. Go to Settings
2. Add folder: `C:\Users\YourName\Documents`
3. Add folder: `C:\Users\YourName\Desktop`
4. Add folder: `C:\Users\YourName\Downloads`
5. Start monitoring
6. Create files in each folder
7. Check Dashboard - shows "3/3 Exists"
8. Modify files in all folders
9. Check Backups tab - files from all folders

**Expected Results:**
- ✅ All folders listed
- ✅ All folders watched
- ✅ Backups from all folders appear
- ✅ Each folder monitored independently

---

### Test 4: Root Drive Warning

**Steps:**
1. Go to Settings
2. Try to add: `C:\`
3. Warning dialog appears
4. Click "OK" to proceed or "Cancel" to stop
5. If proceeding, monitoring starts on entire C: drive

**Expected Results:**
- ✅ Warning dialog shown
- ✅ Explains consequences
- ✅ Can proceed or cancel
- ✅ If proceeding, system watches entire drive

---

### Test 5: Log Monitoring

**Steps:**
1. Start monitoring
2. Go to Logs tab
3. Perform file operations (create, modify, delete)
4. Watch logs update in real-time
5. Toggle "Auto-refresh" on/off
6. Click "🔄 Refresh" manually
7. Click "🗑️ Clear Display"

**Expected Results:**
- ✅ Logs appear automatically
- ✅ Different log types color-coded
- ✅ Timestamps show correctly
- ✅ Auto-refresh works
- ✅ Manual refresh works
- ✅ Clear display works

---

### Test 6: Folder Addition/Removal

**Steps:**
1. Stop monitoring
2. Add a folder: `C:\Test1`
3. Add another: `C:\Test2`
4. Remove `C:\Test2`
5. Start monitoring
6. Verify only `C:\Test1` monitored

**Expected Results:**
- ✅ Can add folders when stopped
- ✅ Can remove folders
- ✅ Only active folders monitored
- ✅ System status updates

---

### Test 7: Network Error Handling

**Steps:**
1. Start monitoring
2. Disconnect internet
3. System continues local backups
4. Uploads will fail (expected)
5. Check logs for error messages
6. Reconnect internet
7. Manually trigger upload

**Expected Results:**
- ✅ Local backups continue
- ✅ Cloud uploads fail gracefully
- ✅ Error logs created
- ✅ Upload works when reconnected

---

### Test 8: Large File Handling

**Steps:**
1. Add folder with large files (>100MB)
2. Start monitoring
3. Modify large file
4. Verify backup created
5. Upload to cloud
6. Download from cloud
7. Verify file integrity

**Expected Results:**
- ✅ Large files backed up
- ✅ Uploads large files
- ✅ Downloads complete files
- ✅ File integrity maintained

---

## Troubleshooting

### Problem: Frontend doesn't load
**Solution:**
- Check if backend server is running on port 5000
- Verify `npm install` completed successfully
- Check for port conflicts (another app using port 3000)

### Problem: Monitoring not starting
**Solution:**
- Check if folders exist
- Verify backup folder permissions
- Check logs for error messages
- Ensure `startMonitoring` is True in state.json

### Problem: Files not backing up
**Solution:**
- Verify monitoring is Active (green status)
- Check monitored folder exists
- Check logs for errors
- Verify file system permissions
- Ensure watchdog library installed correctly

### Problem: Cloud upload fails
**Solution:**
- Check internet connection
- Verify MongoDB connection string
- Check MongoDB Atlas IP whitelist (add your IP)
- Verify free tier limits not exceeded
- Check logs for specific error

### Problem: Can't download from cloud
**Solution:**
- Verify file exists in cloud backups
- Check internet connection
- Verify backup folder exists and writable
- Check logs for specific error
- Restart backend server

### Problem: Too many backup files
**Solution:**
- Remove monitoring from root drives (C:\)
- Monitor specific folders instead
- Periodically clean old backups
- Use more targeted monitoring

### Problem: State.json errors
**Solution:**
- Ensure valid JSON format
- Check file permissions
- Verify all required fields present:
  - `monitor_folders` (array)
  - `backup_folder` (string)
  - `startMonitoring` (boolean)

### Problem: Port already in use
**Solution:**
- Backend (port 5000): Stop other Flask apps
- Frontend (port 3000): Close other React apps
- Or change ports in code

---

## Advanced Configuration

### Changing Upload Interval

Edit `backend/file_protector2.py` line 136:
```python
# Change from 1800 (30 min) to 300 (5 min)
if time.time() - last_upload_time >= 300:
```

### Changing Max Logs

Edit `backend/api.py` line 19:
```python
# Change from 100 to 500
MAX_LOGS = 500
```

### Running Backend as Service (Windows)

Create `start_service.bat`:
```batch
@echo off
cd /d "%~dp0backend"
python api.py
pause
```

Run as Windows Task Scheduler for auto-start.

---

## Best Practices

1. **Monitor Specific Folders**
   - Avoid monitoring C:\ root
   - Target important folders (Documents, Desktop, Projects)
   - Use multiple specific folders

2. **Organize Backups**
   - Use descriptive backup folder
   - Periodically clean old backups
   - Keep backups separate from source files

3. **Internet Connection**
   - Keep internet active for cloud backups
   - Local backups work offline
   - Manually trigger uploads when needed

4. **Security**
   - Don't share MongoDB connection string
   - Use strong MongoDB credentials
   - Keep backup folder secure

5. **Performance**
   - Monitor reasonable number of folders
   - Avoid system directories
   - Clean logs periodically

---

## System Requirements

**Minimum:**
- Windows 10/11
- Python 3.7+
- Node.js 14+
- 100MB disk space for backups
- Internet connection (for cloud features)

**Recommended:**
- Windows 10/11
- Python 3.9+
- Node.js 16+
- 1GB disk space for backups
- Stable internet connection
- 4GB RAM

---

## Support

For issues or questions:
1. Check this guide
2. Review system logs
3. Check error messages
4. Verify configuration

**File Locations:**
- Backend logs: Check terminal output
- State file: `backend/state.json`
- Backups: Configured backup folder
- Cloud backups: MongoDB Atlas cluster

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**License**: MIT

