import os
import json
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from pymongo import MongoClient
import gridfs
import socket

MONGO_URI = os.environ.get("MONGO_URI", "")
DB_NAME = os.environ.get("DB_NAME", "file_backups")

# In-memory state for serverless (Vercel doesn't have persistent file system)
STATE_STORAGE = {
    "monitor_folders": [],
    "backup_folder": "",
    "startMonitoring": False
}

# Client connection tracking
CLIENT_CONNECTIONS = {}  # Store client status by client_id
CLIENT_TIMEOUT = 60  # Consider client disconnected after 60 seconds

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
        if not MONGO_URI:
            return []
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

def cors_headers():
    """Return CORS headers."""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

def parse_body(request):
    """Parse request body."""
    # Vercel passes request as dict
    if isinstance(request, dict):
        body = request.get('body', '')
    else:
        body = getattr(request, 'body', '')
    
    if isinstance(body, bytes):
        body = body.decode('utf-8')
    if not body:
        return {}
    try:
        return json.loads(body)
    except:
        return {}

def parse_query(request):
    """Parse query parameters from request URL."""
    # Vercel passes request as dict
    if isinstance(request, dict):
        url = request.get('url', '')
        query = request.get('query', {})
    else:
        url = getattr(request, 'url', '')
        query = getattr(request, 'query', {})
    
    if url:
        parsed = urlparse(url)
        return parse_qs(parsed.query)
    elif query:
        return query
    return {}

def handle_state(request, path_parts):
    """Handle /api/state requests."""
    # Vercel passes request as dict
    if isinstance(request, dict):
        method = request.get('method', 'GET')
    else:
        method = getattr(request, 'method', 'GET')
    
    if method == 'GET':
        state = get_state()
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                "success": True,
                "state": state,
                "monitoring_active": state.get("startMonitoring", False)
            })
        }
    
    elif method == 'POST':
        try:
            data = parse_body(request)
            state = get_state()
            
            if "add_monitor_folder" in data:
                if "monitor_folders" not in state or not isinstance(state["monitor_folders"], list):
                    state["monitor_folders"] = []
                new_folder = data["add_monitor_folder"]
                if new_folder not in state["monitor_folders"]:
                    state["monitor_folders"].append(new_folder)
                    add_log(f"Added monitor folder: {new_folder}")
            
            if "remove_monitor_folder" in data:
                if "monitor_folders" in state:
                    folder_to_remove = data["remove_monitor_folder"]
                    if folder_to_remove in state["monitor_folders"]:
                        state["monitor_folders"].remove(folder_to_remove)
                        add_log(f"Removed monitor folder: {folder_to_remove}")
            
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
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({"success": True, "state": state})
            }
        except Exception as e:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({"success": False, "error": str(e)})
            }
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handle_status(request, path_parts):
    """Handle /api/status requests."""
    if isinstance(request, dict):
        method = request.get('method', 'GET')
    else:
        method = getattr(request, 'method', 'GET')
    if method == 'GET':
        state = get_state()
        monitor_folders = state.get("monitor_folders", [])
        if not monitor_folders and "monitor_folder" in state:
            monitor_folders = [state["monitor_folder"]]
        
        # Check if any client is connected
        client_connected = False
        client_status = None
        now = datetime.now()
        for client_id, client_info in list(CLIENT_CONNECTIONS.items()):
            last_heartbeat = datetime.fromisoformat(client_info.get("last_heartbeat", "2000-01-01"))
            if (now - last_heartbeat).total_seconds() < CLIENT_TIMEOUT:
                client_connected = True
                client_status = client_info.get("status", {})
                break
        
        status = {
            "monitoring_active": state.get("startMonitoring", False),
            "internet_connected": is_connected(),
            "monitor_folders_count": len(monitor_folders),
            "existing_folders_count": client_status.get("existing_folders_count", 0) if client_status else 0,
            "all_folders_exist": client_status.get("all_folders_exist", False) if client_status else False,
            "backup_folder_exists": client_status.get("backup_folder_exists", False) if client_status else False,
            "local_backup_count": client_status.get("local_backup_count", 0) if client_status else 0,
            "cloud_backup_count": len(get_mongo_backup_files()) if is_connected() else None,
            "client_connected": client_connected
        }
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({"success": True, "status": status})
        }
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handle_logs(request, path_parts):
    """Handle /api/logs requests."""
    if isinstance(request, dict):
        method = request.get('method', 'GET')
    else:
        method = getattr(request, 'method', 'GET')
    if method == 'GET':
        query = parse_query(request)
        limit = int(query.get('limit', [50])[0]) if query.get('limit') else 50
        logs = get_logs(limit)
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({"success": True, "logs": logs})
        }
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handle_backups_cloud(request, path_parts):
    """Handle /api/backups/cloud requests."""
    if len(path_parts) > 2:
        action = path_parts[2]
        
        if action == 'download':
            method = request.get('method', 'GET') if isinstance(request, dict) else getattr(request, 'method', 'GET')
            if method == 'POST':
                data = parse_body(request)
                filename = data.get("filename")
                if not filename:
                    return {'statusCode': 400, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Filename required"})}
                add_log(f"Download requested for {filename} - not available in serverless", "warning")
                return {'statusCode': 200, 'headers': cors_headers(), 'body': json.dumps({"success": True, "message": "Download feature requires file system access"})}
        
        elif action == 'delete':
            method = request.get('method', 'GET') if isinstance(request, dict) else getattr(request, 'method', 'GET')
            if method == 'POST':
                try:
                    data = parse_body(request)
                    filename = data.get("filename")
                    if not filename:
                        return {'statusCode': 400, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Filename required"})}
                    if not MONGO_URI:
                        return {'statusCode': 500, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "MongoDB URI not configured"})}
                    
                    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
                    db = client[DB_NAME]
                    fs = gridfs.GridFS(db)
                    file_doc = db.fs.files.find_one({"filename": filename})
                    if not file_doc:
                        client.close()
                        return {'statusCode': 404, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "File not found in cloud"})}
                    fs.delete(file_doc["_id"])
                    client.close()
                    add_log(f"Deleted cloud backup: {filename}", "warning")
                    return {'statusCode': 200, 'headers': cors_headers(), 'body': json.dumps({"success": True, "message": f"Deleted {filename} from cloud storage"})}
                except Exception as e:
                    add_log(f"Delete failed: {e}", "error")
                    return {'statusCode': 500, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": str(e)})}
        
        elif action == 'delete-all':
            method = request.get('method', 'GET') if isinstance(request, dict) else getattr(request, 'method', 'GET')
            if method == 'POST':
                try:
                    if not MONGO_URI:
                        return {'statusCode': 500, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "MongoDB URI not configured"})}
                    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
                    db = client[DB_NAME]
                    fs = gridfs.GridFS(db)
                    files_deleted = 0
                    for file_doc in db.fs.files.find():
                        fs.delete(file_doc["_id"])
                        files_deleted += 1
                    client.close()
                    add_log(f"Deleted all cloud backups ({files_deleted} files)", "warning")
                    return {'statusCode': 200, 'headers': cors_headers(), 'body': json.dumps({"success": True, "message": f"Deleted {files_deleted} files from cloud storage", "count": files_deleted})}
                except Exception as e:
                    add_log(f"Delete all failed: {e}", "error")
                    return {'statusCode': 500, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": str(e)})}
    
    method = request.get('method', 'GET') if isinstance(request, dict) else getattr(request, 'method', 'GET')
    if method == 'GET':
        try:
            files = get_mongo_backup_files()
            return {'statusCode': 200, 'headers': cors_headers(), 'body': json.dumps({"success": True, "files": files})}
        except Exception as e:
            return {'statusCode': 500, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": str(e)})}
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handle_backups_local(request, path_parts):
    """Handle /api/backups/local requests."""
    method = request.get('method', 'GET') if isinstance(request, dict) else getattr(request, 'method', 'GET')
    if len(path_parts) > 2:
        action = path_parts[2]
        if action in ['delete', 'delete-all']:
            if method == 'POST':
                add_log(f"Local backup {action} requested - not available in serverless", "warning")
                return {'statusCode': 200, 'headers': cors_headers(), 'body': json.dumps({"success": True, "message": "Local file operations require file system access", "count": 0})}
    
    if method == 'GET':
        return {'statusCode': 200, 'headers': cors_headers(), 'body': json.dumps({"success": True, "files": [], "note": "Local file access not available in serverless environment"})}
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handle_monitoring(request, path_parts):
    """Handle /api/monitoring requests."""
    method = request.get('method', 'GET') if isinstance(request, dict) else getattr(request, 'method', 'GET')
    if len(path_parts) > 1:
        action = path_parts[1]
        if method == 'POST':
            try:
                state = get_state()
                if action == 'start':
                    state["startMonitoring"] = True
                    save_state(state)
                    add_log("Monitoring started", "success")
                elif action == 'stop':
                    state["startMonitoring"] = False
                    save_state(state)
                    add_log("Monitoring stopped", "warning")
                return {'statusCode': 200, 'headers': cors_headers(), 'body': json.dumps({"success": True})}
            except Exception as e:
                add_log(f"Error in monitoring: {e}", "error")
                return {'statusCode': 500, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": str(e)})}
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handle_upload(request, path_parts):
    """Handle /api/upload requests."""
    method = request.get('method', 'GET') if isinstance(request, dict) else getattr(request, 'method', 'GET')
    if method == 'POST':
        add_log("Manual upload requested - not available in serverless environment", "warning")
        return {'statusCode': 200, 'headers': cors_headers(), 'body': json.dumps({"success": True, "message": "Upload feature requires file system access"})}
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handle_folders_validate(request, path_parts):
    """Handle /api/folders/validate requests."""
    method = request.get('method', 'GET') if isinstance(request, dict) else getattr(request, 'method', 'GET')
    if method == 'POST':
        try:
            data = parse_body(request)
            path = data.get("path", "")
            return {'statusCode': 200, 'headers': cors_headers(), 'body': json.dumps({"success": True, "exists": False, "note": "File system validation not available in serverless environment"})}
        except Exception as e:
            return {'statusCode': 400, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": str(e)})}
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handle_client_heartbeat(request, path_parts):
    """Handle /api/client/heartbeat requests."""
    method = request.get('method', 'GET') if isinstance(request, dict) else getattr(request, 'method', 'GET')
    if method == 'POST':
        try:
            data = parse_body(request)
            client_id = data.get("client_id", "default")
            status = data.get("status", {})
            timestamp = data.get("timestamp", datetime.now().isoformat())
            
            CLIENT_CONNECTIONS[client_id] = {
                "last_heartbeat": timestamp,
                "status": status
            }
            
            # Return current state from server
            state = get_state()
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({
                    "success": True,
                    "state": state
                })
            }
        except Exception as e:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({"success": False, "error": str(e)})
            }
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handle_client_state(request, path_parts):
    """Handle /api/client/state requests."""
    method = request.get('method', 'GET') if isinstance(request, dict) else getattr(request, 'method', 'GET')
    if method == 'POST':
        try:
            data = parse_body(request)
            # Update server state from client
            state = get_state()
            if "monitor_folders" in data:
                state["monitor_folders"] = data["monitor_folders"]
            if "backup_folder" in data:
                state["backup_folder"] = data["backup_folder"]
            if "startMonitoring" in data:
                state["startMonitoring"] = data["startMonitoring"]
            save_state(state)
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({"success": True, "state": state})
            }
        except Exception as e:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({"success": False, "error": str(e)})
            }
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handle_client_download(request, path_parts):
    """Handle /api/client/download/{platform} requests."""
    method = request.get('method', 'GET') if isinstance(request, dict) else getattr(request, 'method', 'GET')
    if method == 'GET':
        try:
            if len(path_parts) < 3:
                return {
                    'statusCode': 400,
                    'headers': cors_headers(),
                    'body': json.dumps({"success": False, "error": "Platform required"})
                }
            
            platform = path_parts[2]
            if platform not in ['windows', 'macos', 'linux']:
                return {
                    'statusCode': 400,
                    'headers': cors_headers(),
                    'body': json.dumps({"success": False, "error": "Invalid platform. Use: windows, macos, or linux"})
                }
            
            filename = f"file-protector-client-{platform}.zip"
            
            # Connect to MongoDB
            if not MONGO_URI:
                return {
                    'statusCode': 500,
                    'headers': cors_headers(),
                    'body': json.dumps({"success": False, "error": "MongoDB URI not configured"})
                }
            
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            db = client[DB_NAME]
            fs = gridfs.GridFS(db)
            
            # Find the file
            file_doc = db.fs.files.find_one({"filename": filename})
            if not file_doc:
                client.close()
                return {
                    'statusCode': 404,
                    'headers': cors_headers(),
                    'body': json.dumps({"success": False, "error": f"Client file for {platform} not found. Please upload it first."})
                }
            
            # Get file data
            file_data = fs.get(file_doc["_id"])
            file_content = file_data.read()
            
            client.close()
            
            # Return file with proper headers for download
            import base64
            file_base64 = base64.b64encode(file_content).decode('utf-8')
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/zip',
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    'Content-Length': str(len(file_content)),
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Expose-Headers': 'Content-Disposition'
                },
                'body': file_base64,
                'isBase64Encoded': True
            }
        except Exception as e:
            add_log(f"Download client failed: {e}", "error")
            return {
                'statusCode': 500,
                'headers': cors_headers(),
                'body': json.dumps({"success": False, "error": str(e)})
            }
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handler(request):
    """Main handler that routes all API requests."""
    try:
        # Debug: Log request type
        request_type = type(request).__name__
        request_repr = str(request)[:200] if len(str(request)) > 200 else str(request)
        print(f"Request type: {request_type}")
        print(f"Request repr: {request_repr}")
        
        # Vercel passes request as dict or object
        if isinstance(request, dict):
            method = request.get('method', 'GET')
            path = request.get('path', '')
            if not path:
                url = request.get('url', '')
                if url:
                    parsed = urlparse(url)
                    path = parsed.path
            headers = request.get('headers', {})
        elif hasattr(request, '__dict__'):
            # Object with attributes
            method = getattr(request, 'method', 'GET')
            path = getattr(request, 'path', '')
            if not path and hasattr(request, 'url'):
                parsed = urlparse(request.url)
                path = parsed.path
            headers = getattr(request, 'headers', {})
        else:
            # Try to access as dict-like
            method = request.get('method', 'GET') if hasattr(request, 'get') else 'GET'
            path = request.get('path', '') if hasattr(request, 'get') else ''
            if not path and hasattr(request, 'url'):
                parsed = urlparse(request.url)
                path = parsed.path
            headers = request.get('headers', {}) if hasattr(request, 'get') else {}
        
        print(f"Method: {method}, Path: {path}")
        
        # Handle CORS preflight
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            }
        
        # Remove leading /api if present
        if path.startswith('/api'):
            path = path[4:]
        if path.startswith('/'):
            path = path[1:]
        
        path_parts = [p for p in path.split('/') if p]
        
        # Route to appropriate handler
        if not path_parts:
            return {'statusCode': 404, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Endpoint not found"})}
        
        route = path_parts[0]
        
        if route == 'state':
            return handle_state(request, path_parts)
        elif route == 'status':
            return handle_status(request, path_parts)
        elif route == 'logs':
            return handle_logs(request, path_parts)
        elif route == 'backups':
            if len(path_parts) > 1:
                if path_parts[1] == 'cloud':
                    return handle_backups_cloud(request, path_parts)
                elif path_parts[1] == 'local':
                    return handle_backups_local(request, path_parts)
        elif route == 'monitoring':
            return handle_monitoring(request, path_parts)
        elif route == 'upload':
            return handle_upload(request, path_parts)
        elif route == 'folders':
            if len(path_parts) > 1 and path_parts[1] == 'validate':
                return handle_folders_validate(request, path_parts)
        elif route == 'client':
            if len(path_parts) > 1:
                if path_parts[1] == 'heartbeat':
                    return handle_client_heartbeat(request, path_parts)
                elif path_parts[1] == 'state':
                    return handle_client_state(request, path_parts)
                elif path_parts[1] == 'download':
                    return handle_client_download(request, path_parts)
        
        return {'statusCode': 404, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Endpoint not found"})}
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        print(f"Error in handler: {error_msg}")
        print(traceback_str)
        # Return error details in response for debugging
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({
                "success": False,
                "error": error_msg,
                "type": type(e).__name__,
                "traceback": traceback_str.split('\n')[-10:]  # Last 10 lines
            })
        }

