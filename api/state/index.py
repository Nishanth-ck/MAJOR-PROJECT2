import sys
import os
import json

# Add parent directory to path to import helpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import get_state, save_state, add_log

def handler(request):
    """Handle /api/state requests - Vercel Python serverless function."""
    method = request.method
    
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
    
    # Handle GET request
    if method == 'GET':
        state = get_state()
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                "success": True,
                "state": state,
                "monitoring_active": state.get("startMonitoring", False)
            })
        }
    
    # Handle POST request
    if method == 'POST':
        try:
            # Parse request body
            body = request.body
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            data = json.loads(body) if body else {}
            
            state = get_state()
            
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
            
            # Legacy support
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
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({"success": True, "state": state})
            }
        except Exception as e:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({"success": False, "error": str(e)})
            }
    
    # Method not allowed
    return {
        'statusCode': 405,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({"success": False, "error": "Method not allowed"})
    }

