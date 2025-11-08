"""
Desktop Client for File Protector
Runs locally on user's machine and communicates with deployed backend
"""

import os
import sys
import json
import time
import threading
import requests
import socket
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pymongo import MongoClient
import gridfs
import shutil

# Configuration
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".file_protector_client.json")
API_BASE_URL = os.environ.get("API_BASE_URL", "https://your-vercel-app.vercel.app")
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://nishanthck09072004_db_user:b9hoRGMqNCbGSK98@cluster0.yyhfish.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DB_NAME", "file_backups")

# Client state
client_state = {
    "monitor_folders": [],
    "backup_folder": "",
    "startMonitoring": False
}

observers = []
monitoring_active = False
last_heartbeat = None

def load_config():
    """Load configuration from file."""
    global client_state
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                client_state = json.load(f)
        except:
            pass
    return client_state

def save_config():
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(client_state, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

def is_connected():
    """Check internet connection."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def send_heartbeat():
    """Send heartbeat to backend to indicate client is connected."""
    global last_heartbeat
    try:
        status = get_local_status()
        import socket
        client_id = socket.gethostname()  # Use hostname as client ID
        response = requests.post(
            f"{API_BASE_URL}/api/client/heartbeat",
            json={
                "client_id": client_id,
                "status": status,
                "timestamp": datetime.now().isoformat()
            },
            timeout=5
        )
        if response.status_code == 200:
            last_heartbeat = datetime.now()
            # Update state from server if needed
            data = response.json()
            if data.get("success") and "state" in data:
                update_state_from_server(data["state"])
        return True
    except Exception as e:
        print(f"Heartbeat error: {e}")
        return False

def update_state_from_server(server_state):
    """Update local state from server state."""
    global client_state
    if "monitor_folders" in server_state:
        client_state["monitor_folders"] = server_state["monitor_folders"]
    if "backup_folder" in server_state:
        client_state["backup_folder"] = server_state["backup_folder"]
    if "startMonitoring" in server_state:
        client_state["startMonitoring"] = server_state["startMonitoring"]
    save_config()

def sync_state_to_server():
    """Sync local state to server."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/client/state",
            json=client_state,
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"State sync error: {e}")
        return False

def get_local_status():
    """Get local system status."""
    monitor_folders = client_state.get("monitor_folders", [])
    if not monitor_folders and "monitor_folder" in client_state:
        monitor_folders = [client_state["monitor_folder"]]
    
    existing_folders = [f for f in monitor_folders if os.path.exists(f)]
    backup_folder = client_state.get("backup_folder", "")
    
    local_backup_count = 0
    if os.path.exists(backup_folder):
        local_backup_count = len([f for f in os.listdir(backup_folder) 
                                   if os.path.isfile(os.path.join(backup_folder, f))])
    
    return {
        "monitoring_active": monitoring_active,
        "internet_connected": is_connected(),
        "monitor_folders_count": len(monitor_folders),
        "existing_folders_count": len(existing_folders),
        "all_folders_exist": len(existing_folders) == len(monitor_folders) if monitor_folders else False,
        "backup_folder_exists": os.path.exists(backup_folder),
        "local_backup_count": local_backup_count,
        "client_connected": True,
        "last_heartbeat": last_heartbeat.isoformat() if last_heartbeat else None
    }

def upload_to_mongo():
    """Upload all files from backup folder to MongoDB."""
    backup_folder = client_state.get("backup_folder", "")
    
    if not os.path.exists(backup_folder):
        print("[UPLOAD] Backup folder not found.")
        return
    
    if not is_connected():
        print("[UPLOAD] No internet connection. Skipping upload.")
        return
    
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        fs = gridfs.GridFS(db)
        
        for filename in os.listdir(backup_folder):
            file_path = os.path.join(backup_folder, filename)
            
            if os.path.isfile(file_path):
                with open(file_path, "rb") as f:
                    # Delete old version if exists
                    old_file = db.fs.files.find_one({"filename": filename})
                    if old_file:
                        fs.delete(old_file["_id"])
                    
                    fs.put(
                        f.read(),
                        filename=filename,
                        upload_date=datetime.utcnow()
                    )
                    print(f"[UPLOAD] Sent {filename} to MongoDB")
        
        client.close()
        print("[UPLOAD] Completed successfully at", datetime.now())
    except Exception as e:
        print(f"[UPLOAD ERROR] {e}")

class ProtectHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_seen_files = {}
        self.recent_files = {}
    
    def on_modified(self, event):
        if not event.is_directory:
            self.backup_file(event.src_path, "modified")
            self.last_seen_files[event.src_path] = True
    
    def on_deleted(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            
            if filename.startswith('~') or filename.startswith('.tmp') or filename.endswith('.tmp'):
                print(f"[SKIP] Ignored temp file delete: {filename}")
                return
            
            time.sleep(0.1)
            
            if not os.path.exists(event.src_path):
                self.backup_file(event.src_path, "deleted")
                if event.src_path in self.last_seen_files:
                    del self.last_seen_files[event.src_path]
    
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(0.2)
            if os.path.exists(event.src_path):
                self.backup_file(event.src_path, "created")
                self.last_seen_files[event.src_path] = True
    
    def on_moved(self, event):
        if not event.is_directory:
            if event.src_path and event.dest_path:
                print(f"[MOVED] {event.src_path} -> {event.dest_path}")
                if os.path.exists(event.dest_path):
                    self.backup_file(event.dest_path, "moved")
                    self.last_seen_files[event.dest_path] = True
    
    def backup_file(self, file_path, action):
        """Backup a file when it's modified, deleted, created, or moved."""
        try:
            filename = os.path.basename(file_path)
            backup_folder = client_state.get("backup_folder", "")
            
            if not backup_folder:
                print(f"[WARNING] Backup folder not configured")
                return
            
            if action == "deleted":
                time.sleep(0.3)
                
                if os.path.exists(file_path):
                    print(f"[SAVE_DETECTED] File was saved (not deleted): {filename}")
                    self.backup_file(file_path, "modified")
                    return
                
                backup_name = f"{filename}_deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                dest_path = os.path.join(backup_folder, backup_name)
                
                last_backup = self.find_last_backup(backup_folder, filename)
                if last_backup:
                    shutil.copy2(last_backup, dest_path)
                    print(f"[DELETED] Preserved last backup: {filename} -> {os.path.basename(dest_path)}")
                else:
                    with open(dest_path, 'w') as f:
                        f.write(f"File was deleted: {file_path}\n")
                        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    print(f"[DELETED] Created marker: {filename} -> {os.path.basename(dest_path)}")
            elif os.path.exists(file_path):
                backup_name = f"{filename}_{action}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                dest_path = os.path.join(backup_folder, backup_name)
                shutil.copy2(file_path, dest_path)
                print(f"[{action.upper()}] Backed up: {filename} -> {os.path.basename(dest_path)}")
            else:
                print(f"[WARNING] {file_path} - no file to copy.")
        except Exception as e:
            print(f"Error backing up {file_path}: {e}")
    
    def find_last_backup(self, backup_folder, filename):
        """Find the most recent backup of a file."""
        if not os.path.exists(backup_folder):
            return None
        
        for backup_name in os.listdir(backup_folder):
            if backup_name.startswith(filename + '_'):
                return os.path.join(backup_folder, backup_name)
        return None

def start_monitoring():
    """Start file monitoring."""
    global monitoring_active, observers
    
    if monitoring_active:
        print("Monitoring already active")
        return
    
    backup_folder = client_state.get("backup_folder", "")
    if not backup_folder:
        print("[ERROR] Backup folder not configured")
        return
    
    os.makedirs(backup_folder, exist_ok=True)
    
    monitor_folders = client_state.get("monitor_folders", [])
    if not monitor_folders and "monitor_folder" in client_state:
        monitor_folders = [client_state["monitor_folder"]]
    
    event_handler = ProtectHandler()
    observers = []
    
    for folder in monitor_folders:
        if os.path.exists(folder):
            observer = Observer()
            observer.schedule(event_handler, folder, recursive=True)
            observer.start()
            observers.append(observer)
            print(f"Monitoring folder: {folder}")
        else:
            print(f"[WARNING] Folder does not exist: {folder}")
    
    if observers:
        monitoring_active = True
        print(f"Backups will be saved to: {backup_folder}")
    else:
        print("[ERROR] No valid folders to monitor")

def stop_monitoring():
    """Stop file monitoring."""
    global monitoring_active, observers
    
    for observer in observers:
        observer.stop()
        observer.join()
    observers.clear()
    monitoring_active = False
    print("Monitoring stopped")

def monitoring_loop():
    """Main monitoring loop."""
    global monitoring_active
    last_upload_time = time.time()
    
    while True:
        try:
            if client_state.get("startMonitoring") and not monitoring_active:
                start_monitoring()
            elif not client_state.get("startMonitoring") and monitoring_active:
                stop_monitoring()
            
            # Every 30 minutes, try upload
            if time.time() - last_upload_time >= 1800:
                upload_to_mongo()
                last_upload_time = time.time()
            
            time.sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            time.sleep(5)

def heartbeat_loop():
    """Send periodic heartbeats to server."""
    while True:
        try:
            send_heartbeat()
            time.sleep(30)  # Send heartbeat every 30 seconds
        except Exception as e:
            print(f"Heartbeat error: {e}")
            time.sleep(60)  # Retry after 60 seconds on error

def api_server_loop():
    """Local API server to handle commands from web interface."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse
    
    class ClientAPIHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                if self.path == '/api/status':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    status = get_local_status()
                    response_data = json.dumps({"success": True, "status": status}).encode()
                    self.wfile.write(response_data)
                elif self.path == '/api/state':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response_data = json.dumps({"success": True, "state": client_state}).encode()
                    self.wfile.write(response_data)
                else:
                    self.send_response(404)
                    self.end_headers()
            except (ConnectionAbortedError, BrokenPipeError, OSError) as e:
                # Client disconnected, ignore
                pass
            except Exception as e:
                print(f"Error handling GET request: {e}")
        
        def do_POST(self):
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length == 0:
                    post_data = b'{}'
                else:
                    post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                if self.path == '/api/monitoring/start':
                    client_state["startMonitoring"] = True
                    save_config()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True}).encode())
                elif self.path == '/api/monitoring/stop':
                    client_state["startMonitoring"] = False
                    save_config()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True}).encode())
                elif self.path == '/api/upload':
                    upload_to_mongo()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True}).encode())
                elif self.path == '/api/state':
                    if "add_monitor_folder" in data:
                        if "monitor_folders" not in client_state:
                            client_state["monitor_folders"] = []
                        if data["add_monitor_folder"] not in client_state["monitor_folders"]:
                            client_state["monitor_folders"].append(data["add_monitor_folder"])
                    if "remove_monitor_folder" in data:
                        if "monitor_folders" in client_state:
                            if data["remove_monitor_folder"] in client_state["monitor_folders"]:
                                client_state["monitor_folders"].remove(data["remove_monitor_folder"])
                    if "backup_folder" in data:
                        client_state["backup_folder"] = data["backup_folder"]
                    save_config()
                    sync_state_to_server()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "state": client_state}).encode())
                elif self.path == '/api/folders/validate':
                    path = data.get("path", "")
                    exists = os.path.exists(path) and os.path.isdir(path)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "exists": exists}).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            except (ConnectionAbortedError, BrokenPipeError, OSError) as e:
                # Client disconnected, ignore
                pass
            except Exception as e:
                print(f"Error handling POST request: {e}")
                try:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
                except:
                    pass
        
        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
        
        def log_message(self, format, *args):
            pass  # Suppress log messages
    
    server = HTTPServer(('localhost', 5001), ClientAPIHandler)
    print("Local API server started on http://localhost:5001")
    server.serve_forever()

def main():
    """Main entry point."""
    print("=" * 60)
    print("File Protector Desktop Client")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Config File: {CONFIG_FILE}")
    print()
    
    # Load configuration
    load_config()
    
    # Start threads
    monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
    monitoring_thread.start()
    
    heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
    heartbeat_thread.start()
    
    # Start local API server
    api_thread = threading.Thread(target=api_server_loop, daemon=True)
    api_thread.start()
    
    print("Client started. Press Ctrl+C to stop.")
    print("Monitoring will start automatically when enabled from web interface.")
    print()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        stop_monitoring()
        print("Client stopped.")

if __name__ == "__main__":
    main()

