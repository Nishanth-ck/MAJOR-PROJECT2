import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from helpers import get_mongo_backup_files, add_log
from pymongo import MongoClient
import gridfs

MONGO_URI = os.environ.get("MONGO_URI", "")
DB_NAME = os.environ.get("DB_NAME", "file_backups")

def handler(request):
    """Handle /api/backups/cloud/delete requests."""
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
            body = request.body
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            data = json.loads(body) if body else {}
            filename = data.get("filename")
            
            if not filename:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({"success": False, "error": "Filename required"})
                }
            
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
            
            # Find the file
            file_doc = db.fs.files.find_one({"filename": filename})
            if not file_doc:
                client.close()
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({"success": False, "error": "File not found in cloud"})
                }
            
            # Delete the file from GridFS
            fs.delete(file_doc["_id"])
            client.close()
            
            add_log(f"Deleted cloud backup: {filename}", "warning")
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({"success": True, "message": f"Deleted {filename} from cloud storage"})
            }
        except Exception as e:
            add_log(f"Delete failed: {e}", "error")
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

