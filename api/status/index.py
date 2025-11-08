import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import get_state, is_connected, get_mongo_backup_files, get_logs

def handler(request):
    """Handle /api/status requests."""
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
    
    if request.method == 'GET':
        state = get_state()
        
        # Get monitor folders
        monitor_folders = state.get("monitor_folders", [])
        if not monitor_folders and "monitor_folder" in state:
            monitor_folders = [state["monitor_folder"]]
        
        status = {
            "monitoring_active": state.get("startMonitoring", False),
            "internet_connected": is_connected(),
            "monitor_folders_count": len(monitor_folders),
            "existing_folders_count": 0,  # Can't check file system in serverless
            "all_folders_exist": False,  # Can't check file system in serverless
            "backup_folder_exists": False,  # Can't check file system in serverless
            "local_backup_count": 0,  # Can't access local files in serverless
            "cloud_backup_count": len(get_mongo_backup_files()) if is_connected() else None
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({"success": True, "status": status})
        }
    
    return {
        'statusCode': 405,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({"success": False, "error": "Method not allowed"})
    }

