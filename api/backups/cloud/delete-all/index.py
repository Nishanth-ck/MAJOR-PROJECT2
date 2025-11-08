import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from helpers import add_log
from pymongo import MongoClient
import gridfs

MONGO_URI = os.environ.get("MONGO_URI", "")
DB_NAME = os.environ.get("DB_NAME", "file_backups")

def handler(request):
    """Handle /api/backups/cloud/delete-all requests."""
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
    
    if request.method == 'POST':
        try:
            if not MONGO_URI:
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({"success": False, "error": "MongoDB URI not configured"})
                }
            
            # Connect to MongoDB
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            db = client[DB_NAME]
            fs = gridfs.GridFS(db)
            
            # Get all files and delete them
            files_deleted = 0
            for file_doc in db.fs.files.find():
                fs.delete(file_doc["_id"])
                files_deleted += 1
            
            client.close()
            
            add_log(f"Deleted all cloud backups ({files_deleted} files)", "warning")
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    "success": True,
                    "message": f"Deleted {files_deleted} files from cloud storage",
                    "count": files_deleted
                })
            }
        except Exception as e:
            add_log(f"Delete all failed: {e}", "error")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({"success": False, "error": str(e)})
            }
    
    return {
        'statusCode': 405,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({"success": False, "error": "Method not allowed"})
    }

