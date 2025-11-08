from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import threading
import time
from datetime import datetime
from state import load_state, save_state
from pymongo import MongoClient
import gridfs
import socket

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global variables for monitoring
monitoring_thread = None
monitoring_active = False
logs = []  # Store recent logs
MAX_LOGS = 100

# MongoDB connection - use environment variables
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://nishanthck09072004_db_user:b9hoRGMqNCbGSK98@cluster0.yyhfish.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DB_NAME", "file_backups")

# ====== Helper Functions ======

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

def get_backup_files():
    """Get list of files in backup folder."""
    state = load_state()
    backup_folder = state["backup_folder"]
    
    if not os.path.exists(backup_folder):
        return []
    
    files = []
    for filename in os.listdir(backup_folder):
        file_path = os.path.join(backup_folder, filename)
        if os.path.isfile(file_path):
            stat = os.stat(file_path)
            files.append({
                "name": filename,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    
    return sorted(files, key=lambda x: x["modified"], reverse=True)

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

# ====== API Endpoints ======

@app.route('/api/state', methods=['GET'])
def get_state():
    """Get current state."""
    state = load_state()
    # Ensure backward compatibility - convert old format to new format
    if "monitor_folder" in state and "monitor_folders" not in state:
        state["monitor_folders"] = [state["monitor_folder"]]
    
    return jsonify({
        "success": True,
        "state": state,
        "monitoring_active": monitoring_active
    })

@app.route('/api/state', methods=['POST'])
def update_state():
    """Update state."""
    try:
        data = request.json
        state = load_state()
        
        # Handle adding a new monitor folder
        if "add_monitor_folder" in data:
            if "monitor_folders" not in state or not isinstance(state["monitor_folders"], list):
                state["monitor_folders"] = []
            new_folder = data["add_monitor_folder"]
            if new_folder not in state["monitor_folders"]:
                state["monitor_folders"].append(new_folder)
                add_log(f"Added monitor folder: {new_folder}")
        
        # Handle removing a monitor folder
        if "remove_monitor_folder" in data:
            if "monitor_folders" in state:
                folder_to_remove = data["remove_monitor_folder"]
                if folder_to_remove in state["monitor_folders"]:
                    state["monitor_folders"].remove(folder_to_remove)
                    add_log(f"Removed monitor folder: {folder_to_remove}")
        
        # Legacy support for single monitor folder
        if "monitor_folder" in data:
            state["monitor_folder"] = data["monitor_folder"]
            if "monitor_folders" not in state or not isinstance(state["monitor_folders"], list):
                state["monitor_folders"] = [data["monitor_folder"]]
        
        if "backup_folder" in data:
            state["backup_folder"] = data["backup_folder"]
        if "startMonitoring" in data:
            state["startMonitoring"] = data["startMonitoring"]
        
        save_state(state)
        add_log("State updated successfully")
        
        return jsonify({"success": True, "state": state})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start file monitoring."""
    global monitoring_active, monitoring_thread
    
    if monitoring_active:
        return jsonify({"success": False, "error": "Monitoring already active"})
    
    try:
        state = load_state()
        state["startMonitoring"] = True
        save_state(state)
        
        # Start monitoring in a separate thread
        from file_protector2 import start_monitoring_thread
        monitoring_thread = threading.Thread(target=start_monitoring_thread, daemon=True)
        monitoring_thread.start()
        monitoring_active = True
        
        add_log("Monitoring started", "success")
        return jsonify({"success": True})
    except Exception as e:
        add_log(f"Error starting monitoring: {e}", "error")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Stop file monitoring."""
    global monitoring_active
    
    try:
        state = load_state()
        state["startMonitoring"] = False
        save_state(state)
        monitoring_active = False
        
        add_log("Monitoring stopped", "warning")
        return jsonify({"success": True})
    except Exception as e:
        add_log(f"Error stopping monitoring: {e}", "error")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get recent logs."""
    limit = request.args.get('limit', 50, type=int)
    return jsonify({"success": True, "logs": logs[-limit:]})

@app.route('/api/backups/local', methods=['GET'])
def get_local_backups():
    """Get list of local backup files."""
    try:
        files = get_backup_files()
        return jsonify({"success": True, "files": files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/backups/cloud', methods=['GET'])
def get_cloud_backups():
    """Get list of cloud backup files."""
    try:
        files = get_mongo_backup_files()
        return jsonify({"success": True, "files": files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def manual_upload():
    """Manually trigger upload to MongoDB."""
    try:
        from file_protector2 import upload_to_mongo
        upload_to_mongo()
        add_log("Manual upload completed", "success")
        return jsonify({"success": True})
    except Exception as e:
        add_log(f"Upload failed: {e}", "error")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status."""
    state = load_state()
    
    # Get monitor folders (support both old and new format)
    if "monitor_folders" in state:
        monitor_folders = state["monitor_folders"]
    elif "monitor_folder" in state:
        monitor_folders = [state["monitor_folder"]]
    else:
        monitor_folders = []
    
    # Check which folders exist
    existing_folders = [folder for folder in monitor_folders if os.path.exists(folder)]
    
    status = {
        "monitoring_active": monitoring_active if 'monitoring_active' in globals() else False,
        "internet_connected": is_connected(),
        "monitor_folders_count": len(monitor_folders),
        "existing_folders_count": len(existing_folders),
        "all_folders_exist": len(existing_folders) == len(monitor_folders) if monitor_folders else False,
        "backup_folder_exists": os.path.exists(state.get("backup_folder", "")),
        "local_backup_count": len(get_backup_files()),
        "cloud_backup_count": len(get_mongo_backup_files()) if is_connected() else None
    }
    
    return jsonify({"success": True, "status": status})

@app.route('/api/folders/validate', methods=['POST'])
def validate_folder():
    """Validate if a folder path exists."""
    try:
        data = request.json
        path = data.get("path", "")
        exists = os.path.exists(path) and os.path.isdir(path)
        return jsonify({"success": True, "exists": exists})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/backups/cloud/download', methods=['POST'])
def download_from_cloud():
    """Download file from MongoDB and save to backup folder."""
    try:
        from flask import send_file
        import base64
        
        data = request.json
        filename = data.get("filename")
        
        if not filename:
            return jsonify({"success": False, "error": "Filename required"}), 400
        
        # Connect to MongoDB
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        fs = gridfs.GridFS(db)
        
        # Find the file
        file_doc = db.fs.files.find_one({"filename": filename})
        if not file_doc:
            client.close()
            add_log(f"File not found in cloud: {filename}", "error")
            return jsonify({"success": False, "error": "File not found"}), 404
        
        # Get file data
        file_data = fs.get(file_doc["_id"])
        file_content = file_data.read()
        
        # Save to backup folder
        state = load_state()
        backup_folder = state["backup_folder"]
        os.makedirs(backup_folder, exist_ok=True)
        
        destination = os.path.join(backup_folder, filename)
        with open(destination, "wb") as f:
            f.write(file_content)
        
        client.close()
        add_log(f"Downloaded {filename} from cloud to {destination}", "success")
        return jsonify({"success": True, "message": f"Downloaded {filename} to backup folder"})
        
    except Exception as e:
        add_log(f"Download failed: {e}", "error")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/backups/local/delete', methods=['POST'])
def delete_local_backup():
    """Delete a local backup file."""
    try:
        data = request.json
        filename = data.get("filename")
        
        if not filename:
            return jsonify({"success": False, "error": "Filename required"}), 400
        
        state = load_state()
        backup_folder = state["backup_folder"]
        file_path = os.path.join(backup_folder, filename)
        
        if not os.path.exists(file_path):
            return jsonify({"success": False, "error": "File not found"}), 404
        
        os.remove(file_path)
        add_log(f"Deleted local backup: {filename}", "warning")
        return jsonify({"success": True, "message": f"Deleted {filename} from local backups"})
        
    except Exception as e:
        add_log(f"Delete failed: {e}", "error")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/backups/cloud/delete', methods=['POST'])
def delete_cloud_backup():
    """Delete a file from MongoDB cloud storage."""
    try:
        data = request.json
        filename = data.get("filename")
        
        if not filename:
            return jsonify({"success": False, "error": "Filename required"}), 400
        
        # Connect to MongoDB
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        fs = gridfs.GridFS(db)
        
        # Find the file
        file_doc = db.fs.files.find_one({"filename": filename})
        if not file_doc:
            client.close()
            return jsonify({"success": False, "error": "File not found in cloud"}), 404
        
        # Delete the file from GridFS
        fs.delete(file_doc["_id"])
        client.close()
        
        add_log(f"Deleted cloud backup: {filename}", "warning")
        return jsonify({"success": True, "message": f"Deleted {filename} from cloud storage"})
        
    except Exception as e:
        add_log(f"Delete failed: {e}", "error")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/backups/local/delete-all', methods=['POST'])
def delete_all_local_backups():
    """Delete all local backup files."""
    try:
        state = load_state()
        backup_folder = state["backup_folder"]
        
        if not os.path.exists(backup_folder):
            return jsonify({"success": False, "error": "Backup folder not found"}), 404
        
        files_deleted = 0
        for filename in os.listdir(backup_folder):
            file_path = os.path.join(backup_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                files_deleted += 1
        
        add_log(f"Deleted all local backups ({files_deleted} files)", "warning")
        return jsonify({"success": True, "message": f"Deleted {files_deleted} files from local backups", "count": files_deleted})
        
    except Exception as e:
        add_log(f"Delete all failed: {e}", "error")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/backups/cloud/delete-all', methods=['POST'])
def delete_all_cloud_backups():
    """Delete all files from MongoDB cloud storage."""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        fs = gridfs.GridFS(db)
        
        # Get all files
        files_deleted = 0
        for file_doc in db.fs.files.find():
            fs.delete(file_doc["_id"])
            files_deleted += 1
        
        client.close()
        
        add_log(f"Deleted all cloud backups ({files_deleted} files)", "warning")
        return jsonify({"success": True, "message": f"Deleted {files_deleted} files from cloud storage", "count": files_deleted})
        
    except Exception as e:
        add_log(f"Delete all failed: {e}", "error")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    add_log("API Server starting...", "info")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
