# Desktop Client Installation Guide

The File Protector Desktop Client is required to monitor your local file system and upload backups to the cloud. The web interface cannot directly access your file system for security reasons.

## Prerequisites

- Python 3.8 or higher
- Internet connection
- Windows, macOS, or Linux

## Installation Steps

### Step 1: Download the Client

1. Download the `desktop_client` folder from the repository
2. Extract it to a location of your choice (e.g., `C:\FileProtector\` or `~/FileProtector/`)

### Step 2: Install Python Dependencies

Open a terminal/command prompt in the `desktop_client` folder and run:

**Windows:**
```bash
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
pip3 install -r requirements.txt
```

### Step 3: Configure the Client

1. Open `client.py` in a text editor
2. Update the `API_BASE_URL` variable with your deployed website URL:
   ```python
   API_BASE_URL = "https://your-vercel-app.vercel.app"
   ```
3. (Optional) If you have custom MongoDB settings, update `MONGO_URI` and `DB_NAME`

### Step 4: Run the Client

**Windows:**
```bash
python client.py
```

**macOS/Linux:**
```bash
python3 client.py
```

The client will:
- Start a local API server on `http://localhost:5001`
- Send heartbeats to the web backend every 30 seconds
- Monitor your configured folders when enabled
- Upload backups to cloud every 30 minutes

### Step 5: Verify Connection

1. Open your deployed website
2. Go to the Dashboard
3. Check the "Client" status - it should show "🟢 Connected"
4. The "Start Monitoring" and "Upload to Cloud" buttons should now be enabled

## Running as a Service (Optional)

### Windows - Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: "When I log on"
4. Action: Start a program
5. Program: `python`
6. Arguments: `C:\path\to\desktop_client\client.py`
7. Start in: `C:\path\to\desktop_client\`

### macOS/Linux - systemd Service

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

## Troubleshooting

### Client Not Connecting

1. Check if the client is running: Look for "Client started" message
2. Verify API_BASE_URL is correct in `client.py`
3. Check firewall settings - port 5001 should be accessible locally
4. Verify internet connection

### Buttons Still Disabled

1. Make sure the client is running
2. Refresh the web page
3. Check browser console for errors
4. Verify the client can reach the API_BASE_URL

### Monitoring Not Starting

1. Configure monitor folders in the Settings tab
2. Configure backup folder in the Settings tab
3. Check that folders exist and are accessible
4. Look at client console output for errors

## Configuration File

The client saves its configuration to:
- **Windows:** `C:\Users\YourName\.file_protector_client.json`
- **macOS/Linux:** `~/.file_protector_client.json`

You can edit this file directly or use the web interface Settings tab.

## Uninstallation

1. Stop the client (Ctrl+C or stop the service)
2. Delete the `desktop_client` folder
3. (Optional) Delete `~/.file_protector_client.json`

