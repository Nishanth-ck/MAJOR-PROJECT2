import os
import json
from urllib.parse import urlparse, parse_qs
from helpers import (
    get_state, save_state, add_log, is_connected, 
    get_mongo_backup_files, get_logs
)
from pymongo import MongoClient
import gridfs

MONGO_URI = os.environ.get("MONGO_URI", "")
DB_NAME = os.environ.get("DB_NAME", "file_backups")

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
    body = request.body
    if isinstance(body, bytes):
        body = body.decode('utf-8')
    return json.loads(body) if body else {}

def parse_query(request):
    """Parse query parameters from request URL."""
    if hasattr(request, 'url'):
        parsed = urlparse(request.url)
        return parse_qs(parsed.query)
    elif hasattr(request, 'query'):
        return request.query
    return {}

def handle_state(request, path_parts):
    """Handle /api/state requests."""
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
    method = getattr(request, 'method', 'GET')
    if method == 'GET':
        state = get_state()
        monitor_folders = state.get("monitor_folders", [])
        if not monitor_folders and "monitor_folder" in state:
            monitor_folders = [state["monitor_folder"]]
        
        status = {
            "monitoring_active": state.get("startMonitoring", False),
            "internet_connected": is_connected(),
            "monitor_folders_count": len(monitor_folders),
            "existing_folders_count": 0,
            "all_folders_exist": False,
            "backup_folder_exists": False,
            "local_backup_count": 0,
            "cloud_backup_count": len(get_mongo_backup_files()) if is_connected() else None
        }
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({"success": True, "status": status})
        }
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handle_logs(request, path_parts):
    """Handle /api/logs requests."""
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
            method = getattr(request, 'method', 'GET')
            if method == 'POST':
                data = parse_body(request)
                filename = data.get("filename")
                if not filename:
                    return {'statusCode': 400, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Filename required"})}
                add_log(f"Download requested for {filename} - not available in serverless", "warning")
                return {'statusCode': 200, 'headers': cors_headers(), 'body': json.dumps({"success": True, "message": "Download feature requires file system access"})}
        
        elif action == 'delete':
            method = getattr(request, 'method', 'GET')
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
            method = getattr(request, 'method', 'GET')
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
    
    method = getattr(request, 'method', 'GET')
    if method == 'GET':
        try:
            files = get_mongo_backup_files()
            return {'statusCode': 200, 'headers': cors_headers(), 'body': json.dumps({"success": True, "files": files})}
        except Exception as e:
            return {'statusCode': 500, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": str(e)})}
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handle_backups_local(request, path_parts):
    """Handle /api/backups/local requests."""
    method = getattr(request, 'method', 'GET')
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
    method = getattr(request, 'method', 'GET')
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
    method = getattr(request, 'method', 'GET')
    if method == 'POST':
        add_log("Manual upload requested - not available in serverless environment", "warning")
        return {'statusCode': 200, 'headers': cors_headers(), 'body': json.dumps({"success": True, "message": "Upload feature requires file system access"})}
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handle_folders_validate(request, path_parts):
    """Handle /api/folders/validate requests."""
    method = getattr(request, 'method', 'GET')
    if method == 'POST':
        try:
            data = parse_body(request)
            path = data.get("path", "")
            return {'statusCode': 200, 'headers': cors_headers(), 'body': json.dumps({"success": True, "exists": False, "note": "File system validation not available in serverless environment"})}
        except Exception as e:
            return {'statusCode': 400, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": str(e)})}
    
    return {'statusCode': 405, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Method not allowed"})}

def handler(request):
    """Main handler that routes all API requests."""
    # Handle CORS preflight
    method = getattr(request, 'method', 'GET')
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
    
    # Parse the path from request
    path = ''
    if hasattr(request, 'path'):
        path = request.path
    elif hasattr(request, 'url'):
        parsed = urlparse(request.url)
        path = parsed.path
    elif hasattr(request, 'headers') and 'x-vercel-path' in request.headers:
        path = request.headers['x-vercel-path']
    
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
    
    return {'statusCode': 404, 'headers': cors_headers(), 'body': json.dumps({"success": False, "error": "Endpoint not found"})}

