import time
import shutil
import os
import socket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from state import load_state
from datetime import datetime
from pymongo import MongoClient
import gridfs
import zipfile

# ====== MongoDB Atlas Connection ======
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://nishanthck09072004_db_user:b9hoRGMqNCbGSK98@cluster0.yyhfish.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DB_NAME", "file_backups")

# ====== Helper Functions ======

def is_connected():
    """Check internet connection by pinging Google DNS."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def upload_to_mongo():
    """Upload all files from backup folder to MongoDB Atlas."""
    state = load_state()
    backup_folder = state["backup_folder"]

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
        print("[UPLOAD ERROR]", e)

# ====== Watchdog Handler ======

class ProtectHandler(FileSystemEventHandler):
    def __init__(self):
        # Track last known files for deleted file recovery
        self.last_seen_files = {}
        # Prevent duplicate events by tracking recent operations
        self.recent_files = {}  # Track files to avoid duplicate backups

    def on_modified(self, event):
        if not event.is_directory:
            self.backup_file(event.src_path, "modified")
            # Track this file
            self.last_seen_files[event.src_path] = True
        else:
            # Folder modified - log but don't backup (too frequent)
            print(f"[FOLDER_MODIFIED] {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            # Check if this is a temp file or actual deletion
            filename = os.path.basename(event.src_path)
            
            # Skip obvious temp files
            if filename.startswith('~') or filename.startswith('.tmp') or filename.endswith('.tmp'):
                print(f"[SKIP] Ignored temp file delete: {filename}")
                return
            
            # Add small delay to check if file reappears (temp file handling)
            time.sleep(0.1)
            
            # If file doesn't exist after delay, it's likely a real delete
            if not os.path.exists(event.src_path):
                self.backup_file(event.src_path, "deleted")
                if event.src_path in self.last_seen_files:
                    del self.last_seen_files[event.src_path]
        else:
            # Folder deleted - backup the entire folder
            self.backup_folder(event.src_path, "deleted")

    def on_created(self, event):
        if not event.is_directory:
            # Wait a moment to ensure file is fully created
            time.sleep(0.2)
            if os.path.exists(event.src_path):
                self.backup_file(event.src_path, "created")
                # Track new file
                self.last_seen_files[event.src_path] = True
        else:
            # Folder created - just log
            print(f"[FOLDER_CREATED] {event.src_path}")

    def on_moved(self, event):
        """Handle file rename/move operations."""
        if not event.is_directory:
            # File was moved/renamed
            if event.src_path and event.dest_path:
                print(f"[MOVED] {event.src_path} -> {event.dest_path}")
                # Backup the destination file if it exists
                if os.path.exists(event.dest_path):
                    self.backup_file(event.dest_path, "moved")
                    self.last_seen_files[event.dest_path] = True
        else:
            print(f"[FOLDER_MOVED] {event.src_path} -> {event.dest_path}")

    def backup_file(self, file_path, action):
        """Backup a file when it's modified, deleted, created, or moved."""
        try:
            filename = os.path.basename(file_path)
            state = load_state()
            backup_folder = state["backup_folder"]

            if action == "deleted":
                # File is already deleted, check if it reappears soon (save operation)
                time.sleep(0.3)
                
                if os.path.exists(file_path):
                    # File reappeared - it was a save operation, not a delete!
                    print(f"[SAVE_DETECTED] File was saved (not deleted): {filename}")
                    self.backup_file(file_path, "modified")  # Treat as modification
                    return
                
                # File is truly deleted
                backup_name = f"{filename}_deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                dest_path = os.path.join(backup_folder, backup_name)
                
                # Check if we have the last backup to preserve
                last_backup = self.find_last_backup(backup_folder, filename)
                if last_backup:
                    # Copy the last backup as the deleted version
                    shutil.copy2(last_backup, dest_path)
                    print(f"[DELETED] Preserved last backup: {filename} -> {os.path.basename(dest_path)}")
                else:
                    # Create empty marker file
                    with open(dest_path, 'w') as f:
                        f.write(f"File was deleted: {file_path}\n")
                        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    print(f"[DELETED] Created marker: {filename} -> {os.path.basename(dest_path)}")
            elif os.path.exists(file_path):
                # File exists, create backup
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
        
        # Look for any backup of this file
        for backup_name in os.listdir(backup_folder):
            if backup_name.startswith(filename + '_'):
                return os.path.join(backup_folder, backup_name)
        return None

    def backup_folder(self, folder_path, action):
        """Backup folder contents when deleted."""
        if action == "deleted":
            folder_name = os.path.basename(folder_path)
            state = load_state()
            backup_folder = state["backup_folder"]
            
            # Check if parent folder still exists (might be recursive delete)
            parent_dir = os.path.dirname(folder_path)
            if not os.path.exists(parent_dir):
                print(f"[FOLDER_DELETED] Parent folder deleted, skipping: {folder_name}")
                return
            
            # Create a backup of the folder as a ZIP file
            zip_name = f"[FOLDER]_{folder_name}_deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            zip_path = os.path.join(backup_folder, zip_name)
            
            # Try to backup what we can from the folder
            # Since folder is deleted, we can't backup its contents
            # Create a marker instead with details about what was lost
            marker_name = f"[FOLDER]_{folder_name}_deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}_info.txt"
            marker_path = os.path.join(backup_folder, marker_name)
            
            with open(marker_path, 'w') as f:
                f.write(f"Folder was deleted: {folder_path}\n")
                f.write(f"Folder name: {folder_name}\n")
                f.write(f"Full path: {folder_path}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"\nNote: Folder contents could not be backed up as the folder was already deleted.\n")
                f.write(f"To backup folder contents before deletion, stop monitoring before deleting the folder.\n")
            
            print(f"[FOLDER_DELETED] Created marker: {folder_name}")
        else:
            print(f"[FOLDER_{action.upper()}] {folder_path}")

# ====== Main Loop ======

def start_monitoring_thread():
    """Start monitoring in a thread (called from API)."""
    print("Waiting for monitoring to be enabled... (set startMonitoring=True in state.json)")

    observers = []
    last_upload_time = time.time()

    try:
        while True:
            state = load_state()

            if state["startMonitoring"] and len(observers) == 0:
                os.makedirs(state["backup_folder"], exist_ok=True)

                # Support both old format (single folder) and new format (multiple folders)
                monitor_folders = state.get("monitor_folders", [state.get("monitor_folder", "")])

                event_handler = ProtectHandler()
                
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
                    print(f"Backups will be saved to: {state['backup_folder']}")
                else:
                    print("[ERROR] No valid folders to monitor")

            elif not state["startMonitoring"] and len(observers) > 0:
                for observer in observers:
                    observer.stop()
                    observer.join()
                observers.clear()
                print("Monitoring stopped")

            # Every 30 minutes, try upload
            if time.time() - last_upload_time >= 1800:  # 30 min (1800 sec)
                upload_to_mongo()        
                last_upload_time = time.time()

            time.sleep(1)

    except KeyboardInterrupt:
        for observer in observers:
            observer.stop()
        print("Stopping monitor...")

    for observer in observers:
        observer.join()

if __name__ == "__main__":
    start_monitoring_thread()




