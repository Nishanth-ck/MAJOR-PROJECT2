# File Protector Desktop Client

This is the desktop client application that runs locally on your machine to monitor your file system and communicate with the deployed web application.

## Why Do I Need This?

Web browsers cannot directly access your local file system for security reasons. The desktop client bridges this gap by:

- Running locally on your computer
- Monitoring your configured folders for file changes
- Creating backups when files are modified, created, or deleted
- Uploading backups to the cloud storage
- Communicating with the web interface via a local API

## Quick Start

1. **Install Dependencies:**
   ```bash
   # Windows
   install.bat
   
   # macOS/Linux
   ./install.sh
   ```

2. **Configure:**
   - Open `client.py`
   - Set `API_BASE_URL` to your deployed website URL
   - (Optional) Configure MongoDB settings

3. **Run:**
   ```bash
   # Windows
   python client.py
   
   # macOS/Linux
   python3 client.py
   ```

4. **Verify:**
   - Open your website
   - Check Dashboard → "Client: 🟢 Connected"
   - Buttons should now be enabled

## Features

- **File Monitoring:** Watches configured folders for changes
- **Automatic Backups:** Creates backups when files are modified/deleted
- **Cloud Upload:** Automatically uploads backups every 30 minutes
- **Local API:** Provides API endpoints for the web interface
- **Heartbeat:** Sends status updates to the web backend

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────┐
│  Web Browser    │────────▶│  Deployed Backend │         │   MongoDB    │
│  (Frontend)     │         │  (Vercel API)     │────────▶│   (Cloud)    │
└─────────────────┘         └──────────────────┘         └──────────────┘
       │                              ▲
       │                              │
       │                              │ Heartbeat
       │                              │
       └──────────────────────────────┘
                  │
                  │ Local API (localhost:5001)
                  │
       ┌──────────▼──────────┐
       │  Desktop Client      │
       │  (client.py)         │
       │                      │
       │  - File Monitoring   │
       │  - Local Backups     │
       │  - Cloud Upload      │
       └──────────────────────┘
                  │
                  │ File System Access
                  │
       ┌──────────▼──────────┐
       │  Your Computer      │
       │  (Folders/Files)    │
       └─────────────────────┘
```

## Configuration

The client configuration is stored in:
- **Windows:** `C:\Users\YourName\.file_protector_client.json`
- **macOS/Linux:** `~/.file_protector_client.json`

You can configure:
- Monitor folders (folders to watch)
- Backup folder (where backups are stored)
- Monitoring status (start/stop)

Configuration can be done via:
1. Web interface (Settings tab)
2. Directly editing the JSON file

## Running as a Service

See `INSTALL.md` for instructions on running the client as a background service on Windows, macOS, or Linux.

## Troubleshooting

### Client Won't Start
- Check Python version: `python --version` (should be 3.8+)
- Verify dependencies: `pip list | grep watchdog`
- Check for port conflicts (port 5001)

### Not Connecting to Web
- Verify `API_BASE_URL` is correct
- Check internet connection
- Check firewall settings

### Monitoring Not Working
- Verify folders exist and are accessible
- Check backup folder permissions
- Look at client console output

## Files

- `client.py` - Main client application
- `requirements.txt` - Python dependencies
- `install.bat` - Windows installer
- `install.sh` - macOS/Linux installer
- `INSTALL.md` - Detailed installation guide
- `README.md` - This file

## Support

For issues or questions, please check:
1. The main project README
2. INSTALL.md for detailed setup
3. Web interface Logs tab for error messages

