# 🚀 Getting Started with File Protector

## Quick Installation (5 Minutes)

### Step 1: Run Setup
Double-click `SETUP.bat` in the project folder.

This will:
- ✅ Check Python installation
- ✅ Check Node.js installation
- ✅ Install backend dependencies
- ✅ Install frontend dependencies

### Step 2: Configure MongoDB
1. Go to https://www.mongodb.com/atlas
2. Sign up (free account)
3. Create a cluster (Free tier M0)
4. Get connection string
5. Edit `backend/api.py` - update `MONGO_URI`
6. Edit `backend/file_protector2.py` - update `MONGO_URI`

### Step 3: Start the Application
Double-click `START.bat`

This opens:
- Backend server (Terminal 1)
- Frontend server (Terminal 2)
- Browser at http://localhost:3000

---

## What's Included?

### 📄 Documentation Files

1. **USER_GUIDE.md** (15+ pages)
   - Complete installation guide
   - UI walkthrough
   - 8 test scenarios
   - Troubleshooting guide
   - Use cases
   - Advanced configuration

2. **README.md** (Main project file)
   - Project overview
   - Quick start
   - Architecture
   - Features
   - Links to documentation

3. **GETTING_STARTED.md** (This file)
   - Quick setup instructions
   - First steps

### 🔧 Scripts

1. **SETUP.bat**
   - Automated installation
   - Checks prerequisites
   - Installs dependencies

2. **START.bat**
   - Launches both servers
   - Opens browser automatically
   - Easy one-click start

---

## First Time Usage

### 1. Configure Folders
1. Open http://localhost:3000
2. Click Settings tab
3. Add monitor folder (e.g., `C:\Users\YourName\Documents`)
4. Set backup folder (e.g., `C:\Users\YourName\Backups`)
5. Click "💾 Save"

### 2. Start Monitoring
1. Click Dashboard tab
2. Click "▶️ Start Monitoring"
3. Status shows "Active"

### 3. Test It
1. Create a test file in monitored folder
2. Modify the file
3. Go to Backups tab
4. See `test.txt_modified` created
5. Delete the file
6. See `test.txt_deleted` created

### 4. View Logs
1. Click Logs tab
2. See real-time activity
3. Enable auto-refresh

### 5. Upload to Cloud
1. Click Dashboard tab
2. Click "☁️ Upload to Cloud"
3. Wait for upload
4. Click Backups tab
5. Click "☁️ Cloud Backups"
6. See your files in cloud

### 6. Download from Cloud
1. In Cloud Backups tab
2. Click "⬇️ Download" on any file
3. File restored to backup folder

---

## Example Use Cases

### Protect Your Documents
```
Monitor: C:\Users\YourName\Documents
Backup: C:\Users\YourName\Backups
```

### Protect Your Desktop
```
Monitor: C:\Users\YourName\Desktop
Backup: C:\Users\YourName\Backups
```

### Protect Your Project
```
Monitor: C:\Projects\MyProject
Backup: C:\Projects\Backups
```

### Monitor Multiple Locations
```
Monitor: C:\Users\YourName\Documents
Monitor: C:\Users\YourName\Desktop
Monitor: C:\Users\YourName\Downloads
Backup: C:\Users\YourName\Backups
```

---

## Important Notes

### ⚠️ Don't Monitor Root Drive
Avoid monitoring `C:\` directly unless you want to backup:
- Windows system files
- Program files
- Temp files
- Everything!

Instead, monitor specific folders like:
- `C:\Users\YourName\Documents`
- `C:\Users\YourName\Desktop`

### ✅ Recommended Setup
```
Monitor Folders:
  ✓ C:\Users\YourName\Documents
  ✓ C:\Users\YourName\Desktop
  ✓ C:\Users\YourName\Downloads

Backup Folder:
  ✓ C:\Users\YourName\Backups
```

---

## Troubleshooting

### "Can't start monitoring"
- Check if folders exist
- Check backup folder permissions
- See System Status in Dashboard

### "Cloud upload failed"
- Check internet connection
- Verify MongoDB connection string
- Check MongoDB IP whitelist
- See Logs tab for details

### "Download button not working"
- Restart backend server
- Check internet connection
- See Logs tab for errors

For more help, see **USER_GUIDE.md** → Troubleshooting section.

---

## Next Steps

1. ✅ Install dependencies (SETUP.bat)
2. ✅ Configure MongoDB
3. ✅ Start application (START.bat)
4. ✅ Add monitor folders
5. ✅ Start monitoring
6. ✅ Test file backup
7. ✅ Upload to cloud
8. ✅ Read USER_GUIDE.md for advanced features

---

## File Locations

**Configuration:**
- `backend/state.json` - Current settings

**Backups:**
- Local: Your configured backup folder
- Cloud: MongoDB Atlas cluster

**Logs:**
- View in UI (Logs tab)
- Also in terminal output

---

## Need Help?

1. Read **USER_GUIDE.md** (comprehensive guide)
2. Check **README.md** (project overview)
3. Review Logs tab in UI
4. Verify configuration files
5. Check test scenarios in USER_GUIDE.md

---

## Quick Reference

**Start Application:**
```bash
Double-click START.bat
```

**Stop Application:**
- Close the terminal windows
- Or press Ctrl+C in each terminal

**Check Status:**
- Open http://localhost:3000
- Click Dashboard tab

**View Logs:**
- Click Logs tab
- Enable auto-refresh

**Add Folders:**
- Click Settings tab
- Enter path, click Add

**Start Monitoring:**
- Click Dashboard tab
- Click Start Monitoring

**Backup to Cloud:**
- Click Dashboard tab
- Click Upload to Cloud

**Download from Cloud:**
- Click Backups tab
- Click Cloud Backups
- Click Download button

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Status:** Ready to Use ✅

