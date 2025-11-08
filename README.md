# 🛡️ File Protector - Automated Backup System

A powerful, user-friendly file monitoring and backup system that protects your important files with real-time monitoring, local backups, and cloud storage.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://www.mongodb.com/atlas)

---

## 📋 Table of Contents

- [Features](#-features]
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Documentation](#-documentation)
- [Screenshots](#-screenshots)

---

## ✨ Features

### Core Functionality
- ✅ **Real-time Monitoring** - Watch multiple folders simultaneously
- ✅ **Instant Backups** - Automatic backup on file changes/deletions
- ✅ **Cloud Storage** - Secure backups in MongoDB Atlas
- ✅ **File Recovery** - Download and restore files from cloud
- ✅ **Modern UI** - Beautiful Tailwind CSS interface
- ✅ **System Logs** - Real-time activity tracking

### Advanced Capabilities
- 📁 **Multiple Folder Monitoring** - Protect entire drives or specific folders
- 🌐 **Automatic Cloud Sync** - Uploads every 30 minutes
- 📊 **Dashboard Analytics** - Real-time statistics and status
- 🔄 **Manual Controls** - Start/stop monitoring, manual uploads
- ⚠️ **Smart Warnings** - Prevents accidental root drive monitoring
- 💾 **Complete File Recovery** - Restore any backed-up file

---

## 🚀 Quick Start

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Configure MongoDB

1. Sign up at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free cluster
3. Get your connection string
4. Update in `backend/api.py` and `backend/file_protector2.py`:
   ```python
   MONGO_URI = "your-connection-string-here"
   ```

### 3. Run the Application

**Option A: Separate Terminals**
```bash
# Terminal 1 - Backend
cd backend
python api.py

# Terminal 2 - Frontend
cd frontend
npm start
```

**Option B: Batch File (Windows)**
```batch
# Create start.bat in project root
@echo off
start "Backend" cmd /k "cd backend && python api.py"
timeout /t 3
start "Frontend" cmd /k "cd frontend && npm start"
```

### 4. Access the Application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:5000

---

## 📐 Architecture

```
File Protector/
├── backend/              # Python Flask Backend
│   ├── api.py           # REST API endpoints
│   ├── file_protector2.py  # File monitoring logic
│   ├── state.py         # State management
│   ├── controller.py    # Control scripts
│   └── requirements.txt # Python dependencies
│
├── frontend/             # React Frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   │   ├── Dashboard.js
│   │   │   ├── Settings.js
│   │   │   ├── Backups.js
│   │   │   └── Logs.js
│   │   ├── App.js       # Main app component
│   │   └── index.js     # Entry point
│   └── package.json     # Node dependencies
│
├── USER_GUIDE.md        # Complete user documentation
└── README.md            # This file
```

**Tech Stack:**
- **Backend**: Flask (Python), Watchdog (file monitoring), PyMongo, GridFS
- **Frontend**: React, Tailwind CSS, Axios
- **Database**: MongoDB Atlas (cloud storage)
- **File Storage**: GridFS for large files

---

## 📚 Documentation

### Complete User Guide

See **[USER_GUIDE.md](./USER_GUIDE.md)** for comprehensive documentation including:

- 📖 Complete installation guide
- 🎯 Step-by-step UI walkthrough
- 💡 Real-world use cases
- 🧪 8 detailed test scenarios
- 🔧 Troubleshooting guide
- ⚙️ Advanced configuration

### API Endpoints

**State Management:**
- `GET /api/state` - Get current configuration
- `POST /api/state` - Update configuration
- `POST /api/state` with `add_monitor_folder` - Add folder
- `POST /api/state` with `remove_monitor_folder` - Remove folder

**Monitoring:**
- `POST /api/monitoring/start` - Start monitoring
- `POST /api/monitoring/stop` - Stop monitoring
- `GET /api/status` - Get system status

**Backups:**
- `GET /api/backups/local` - List local backups
- `GET /api/backups/cloud` - List cloud backups
- `POST /api/backups/cloud/download` - Download from cloud
- `POST /api/upload` - Manual cloud upload

**Logs:**
- `GET /api/logs` - Get system logs

---

## 🎮 Use Cases

### 1. Document Protection
Monitor and backup important documents automatically.

### 2. Code Projects
Track every change in your development projects.

### 3. Desktop Files
Protect files on your desktop from accidental deletion.

### 4. Disaster Recovery
Cloud storage ensures file recovery after system failure.

### 5. Multiple Locations
Protect Documents, Desktop, Downloads simultaneously.

### 6. Enterprise Use
Monitor entire network drives or shared folders.

---

## 🖼️ Screenshots

### Dashboard
- Real-time system status
- Quick action buttons
- Backup statistics
- Current configuration

### Settings
- Add/remove monitor folders
- Configure backup location
- Manage multiple folders
- Smart warnings

### Backups
- View local backups
- View cloud backups
- Download from cloud
- File recovery

### Logs
- Real-time activity feed
- Color-coded log types
- Auto-refresh toggle
- Event history

---

## 🧪 Test Scenarios

The **[USER_GUIDE.md](./USER_GUIDE.md)** includes 8 comprehensive test scenarios:

1. **Basic File Monitoring** - Create, modify, delete test
2. **Cloud Upload and Download** - End-to-end cloud workflow
3. **Multiple Folder Monitoring** - Simultaneous folder watching
4. **Root Drive Warning** - Safety for C:\ monitoring
5. **Log Monitoring** - Real-time logging verification
6. **Folder Management** - Add/remove functionality
7. **Network Error Handling** - Offline resilience
8. **Large File Handling** - Performance with big files

---

## ⚙️ Configuration

### Default Settings

**State File:** `backend/state.json`
```json
{
  "monitor_folders": ["C:\\Users\\YourName\\Documents"],
  "backup_folder": "C:\\Users\\YourName\\Backups",
  "startMonitoring": false
}
```

### Environment Variables

- `MONGO_URI` - MongoDB connection string
- `DB_NAME` - Database name (default: file_backups)
- `FLASK_ENV` - Flask environment (development/production)

---

## 🛠️ Troubleshooting

### Common Issues

**Problem:** Backend won't start
- **Solution:** Check Python version (3.7+), install requirements.txt

**Problem:** Frontend won't start
- **Solution:** Run `npm install`, check Node version (14+)

**Problem:** Monitoring not working
- **Solution:** Verify folders exist, check permissions, view logs

**Problem:** Cloud upload fails
- **Solution:** Check internet, verify MongoDB connection string, check IP whitelist

For more troubleshooting, see [USER_GUIDE.md](./USER_GUIDE.md).

---

## 📝 License

MIT License - Feel free to use and modify for your projects.

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support

- 📖 See **USER_GUIDE.md** for detailed help
- 🐛 Check logs for error messages
- 💡 Review test scenarios for examples
- 🔧 Verify configuration files

---

## 🚀 Future Enhancements

- [ ] Scheduled backups
- [ ] Backup retention policies
- [ ] Email notifications
- [ ] File versioning
- [ ] Encryption support
- [ ] Mobile app
- [ ] Network sync
- [ ] Backup compression

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Author:** File Protector Team  
**Status:** Production Ready ✅

