# Desktop Client User Guide

## Overview

The File Protector Desktop Client is a local application that runs on your computer to enable file monitoring and cloud backup features. Since web browsers cannot directly access your file system, the desktop client acts as a bridge between your computer and the web application.

## Why You Need the Desktop Client

When you access the File Protector website, you may notice that the "Start Monitoring" and "Upload Backup to Cloud" buttons are disabled. This is because:

1. **Security Restrictions:** Web browsers cannot access your local file system for security reasons
2. **Serverless Backend:** The deployed backend runs on Vercel (serverless) and doesn't have access to your computer's files
3. **Local Monitoring Required:** File monitoring must run locally on your machine

The desktop client solves this by:
- Running locally on your computer
- Monitoring your folders for changes
- Creating backups when files are modified or deleted
- Uploading backups to cloud storage
- Communicating with the web interface

## Installation

### Step 1: Download the Client

1. Download or clone the `desktop_client` folder from the repository
2. Extract it to a convenient location (e.g., `C:\FileProtector\` on Windows or `~/FileProtector/` on Mac/Linux)

### Step 2: Install Python Dependencies

**Windows:**
1. Open Command Prompt in the `desktop_client` folder
2. Run: `install.bat`
   - Or manually: `pip install -r requirements.txt`

**macOS/Linux:**
1. Open Terminal in the `desktop_client` folder
2. Run: `chmod +x install.sh && ./install.sh`
   - Or manually: `pip3 install -r requirements.txt`

### Step 3: Configure the Client

1. Open `client.py` in a text editor
2. Find the line: `API_BASE_URL = os.environ.get("API_BASE_URL", "https://your-vercel-app.vercel.app")`
3. Replace `"https://your-vercel-app.vercel.app"` with your actual deployed website URL
   - Example: `API_BASE_URL = "https://file-protector.vercel.app"`

### Step 4: Run the Client

**Windows:**
```bash
python client.py
```

**macOS/Linux:**
```bash
python3 client.py
```

You should see:
```
============================================================
File Protector Desktop Client
============================================================
API Base URL: https://your-website.vercel.app
Config File: C:\Users\YourName\.file_protector_client.json

Local API server started on http://localhost:5001
Client started. Press Ctrl+C to stop.
Monitoring will start automatically when enabled from web interface.
```

### Step 5: Verify Connection

1. Open your deployed File Protector website
2. Go to the **Dashboard** tab
3. Look for the **"Client"** status indicator
4. It should show: **"🟢 Connected"**
5. The **"Start Monitoring"** and **"Upload to Cloud"** buttons should now be enabled

## Using the Desktop Client

### Starting Monitoring

1. Make sure the desktop client is running
2. Open the web interface
3. Go to **Settings** tab
4. Add monitor folders (folders you want to protect)
5. Set backup folder (where backups will be stored)
6. Go to **Dashboard** tab
7. Click **"▶️ Start Monitoring"**

The client will now watch your folders and create backups automatically.

### Stopping Monitoring

1. Go to **Dashboard** tab
2. Click **"⏸️ Stop Monitoring"**

### Manual Cloud Upload

1. Go to **Dashboard** tab
2. Click **"☁️ Upload to Cloud"**
3. Wait for the upload to complete

### Automatic Features

- **File Monitoring:** Automatically detects file changes, creations, and deletions
- **Backup Creation:** Automatically creates backups when files change
- **Cloud Upload:** Automatically uploads backups every 30 minutes (if internet is available)

## Running in the Background

### Windows - Task Scheduler

1. Open **Task Scheduler**
2. Click **Create Basic Task**
3. Name: "File Protector Client"
4. Trigger: **When I log on**
5. Action: **Start a program**
   - Program: `python`
   - Arguments: `C:\path\to\desktop_client\client.py`
   - Start in: `C:\path\to\desktop_client\`
6. Click **Finish**

### macOS - Launch Agent

Create `~/Library/LaunchAgents/com.fileprotector.client.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.fileprotector.client</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/desktop_client/client.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.fileprotector.client.plist
```

### Linux - systemd Service

Create `/etc/systemd/system/file-protector-client.service`:

```ini
[Unit]
Description=File Protector Desktop Client
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/desktop_client
ExecStart=/usr/bin/python3 /path/to/desktop_client/client.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable file-protector-client
sudo systemctl start file-protector-client
```

## Configuration

The client configuration is stored in:
- **Windows:** `C:\Users\YourName\.file_protector_client.json`
- **macOS/Linux:** `~/.file_protector_client.json`

You can configure:
- **Monitor Folders:** Folders to watch for changes
- **Backup Folder:** Where backups are stored locally
- **Monitoring Status:** Whether monitoring is active

Configuration can be done via:
1. **Web Interface:** Settings tab (recommended)
2. **Direct Edit:** Edit the JSON file directly

## Troubleshooting

### Client Status Shows "Not Connected"

**Possible Causes:**
1. Client is not running
2. Wrong API_BASE_URL in client.py
3. Firewall blocking port 5001
4. Internet connection issues

**Solutions:**
1. Check if client is running (look for console window)
2. Verify API_BASE_URL matches your deployed website
3. Check Windows Firewall or antivirus settings
4. Test internet connection

### Buttons Still Disabled

**Possible Causes:**
1. Client not connected
2. Folders not configured
3. Backup folder not set

**Solutions:**
1. Verify client shows "🟢 Connected" in Dashboard
2. Go to Settings and add monitor folders
3. Set backup folder in Settings
4. Refresh the page

### Monitoring Not Working

**Possible Causes:**
1. Monitoring not started
2. Folders don't exist
3. Permission issues
4. Client crashed

**Solutions:**
1. Click "Start Monitoring" in Dashboard
2. Verify folders exist and paths are correct
3. Check folder permissions
4. Check client console for errors

### Upload to Cloud Fails

**Possible Causes:**
1. No internet connection
2. MongoDB connection issues
3. No local backups to upload

**Solutions:**
1. Check internet connection
2. Verify MongoDB URI in client.py (if custom)
3. Check if local backups exist (Backups tab)

## Architecture Overview

```
┌─────────────────┐
│  Web Browser    │  ← You interact here
│  (Frontend)     │
└────────┬────────┘
         │
         │ HTTP Requests
         │
┌────────▼────────┐         ┌──────────────┐
│  Desktop Client │────────▶│  Web Backend │
│  (localhost:5001)│         │  (Vercel)    │
└────────┬────────┘         └──────┬───────┘
         │                          │
         │ File System              │ Cloud Storage
         │                          │
┌────────▼────────┐         ┌──────▼───────┐
│  Your Computer   │         │   MongoDB     │
│  (Folders/Files) │         │   (Cloud)     │
└──────────────────┘         └───────────────┘
```

## Security Notes

- The desktop client runs locally and only communicates with:
  - Your local file system (for monitoring)
  - The web backend (for status sync)
  - MongoDB (for cloud uploads)
- No data is sent to third parties
- All file operations happen locally
- Cloud uploads are encrypted in transit (HTTPS)

## Uninstallation

1. Stop the client (Ctrl+C or stop the service)
2. Delete the `desktop_client` folder
3. (Optional) Delete the config file:
   - Windows: `C:\Users\YourName\.file_protector_client.json`
   - macOS/Linux: `~/.file_protector_client.json`

## Support

For additional help:
- Check the main project README
- Review INSTALL.md in desktop_client folder
- Check the Logs tab in the web interface
- Review client console output for errors

