import os
import json
from datetime import datetime
from pymongo import MongoClient
import gridfs
import socket

# MongoDB connection - Use environment variable in production
# Set MONGO_URI in Vercel dashboard under Settings > Environment Variables
MONGO_URI = os.environ.get("MONGO_URI", "")
DB_NAME = os.environ.get("DB_NAME", "file_backups")

# In-memory state for serverless (Vercel doesn't have persistent file system)
# In production, you might want to use a database or external storage
STATE_STORAGE = {
    "monitor_folders": [],
    "backup_folder": "",
    "startMonitoring": False
}

logs = []
MAX_LOGS = 100

def add_log(message, log_type="info"):
    """Add a log entry with timestamp."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "type": log_type
    }
    logs.append(log_entry)
    if len(logs) > MAX_LOGS:
        logs.pop(0)
    print(f"[{log_type.upper()}] {message}")

def is_connected():
    """Check internet connection."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def get_state():
    """Get current state."""
    return STATE_STORAGE.copy()

def save_state(state):
    """Save state (in-memory for serverless)."""
    STATE_STORAGE.update(state)

def get_mongo_backup_files():
    """Get list of files from MongoDB."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        files = []
        
        for file_doc in db.fs.files.find():
            files.append({
                "name": file_doc["filename"],
                "size": file_doc["length"],
                "uploaded": file_doc["uploadDate"].isoformat()
            })
        
        client.close()
        return sorted(files, key=lambda x: x["uploaded"], reverse=True)
    except Exception as e:
        add_log(f"Error fetching MongoDB files: {e}", "error")
        return []

def get_logs(limit=50):
    """Get recent logs."""
    return logs[-limit:] if len(logs) > limit else logs

