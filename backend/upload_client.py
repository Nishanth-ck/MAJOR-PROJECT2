"""
Script to upload desktop client ZIP files to MongoDB GridFS
Run this after packaging the client with package_client.bat or package_client.sh
"""

import os
import sys
from pymongo import MongoClient
import gridfs
from datetime import datetime

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://nishanthck09072004_db_user:b9hoRGMqNCbGSK98@cluster0.yyhfish.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DB_NAME", "file_backups")

def upload_client_file(zip_path, platform):
    """Upload a client ZIP file to MongoDB GridFS."""
    if not os.path.exists(zip_path):
        print(f"❌ File not found: {zip_path}")
        return False
    
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        fs = gridfs.GridFS(db)
        
        # Check if file already exists and delete it
        existing_file = db.fs.files.find_one({"filename": f"file-protector-client-{platform}.zip"})
        if existing_file:
            fs.delete(existing_file["_id"])
            print(f"🗑️  Deleted existing {platform} client file")
        
        # Upload new file
        with open(zip_path, "rb") as f:
            file_id = fs.put(
                f.read(),
                filename=f"file-protector-client-{platform}.zip",
                platform=platform,
                upload_date=datetime.utcnow(),
                content_type="application/zip"
            )
        
        file_size = os.path.getsize(zip_path)
        print(f"✅ Uploaded {platform} client ({file_size:,} bytes) - ID: {file_id}")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ Error uploading {platform} client: {e}")
        return False

def main():
    print("=" * 60)
    print("Upload Desktop Client Files to MongoDB")
    print("=" * 60)
    print()
    
    # Check if dist folder exists
    dist_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")
    if not os.path.exists(dist_folder):
        print(f"❌ dist folder not found: {dist_folder}")
        print("Please run package_client.bat or package_client.sh first!")
        sys.exit(1)
    
    platforms = ["windows", "macos", "linux"]
    uploaded = 0
    
    for platform in platforms:
        zip_file = os.path.join(dist_folder, f"file-protector-client-{platform}.zip")
        if os.path.exists(zip_file):
            if upload_client_file(zip_file, platform):
                uploaded += 1
        else:
            print(f"⚠️  Skipping {platform} - file not found: {zip_file}")
    
    print()
    print("=" * 60)
    if uploaded == len(platforms):
        print(f"✅ Successfully uploaded {uploaded} client files to MongoDB!")
    else:
        print(f"⚠️  Uploaded {uploaded}/{len(platforms)} client files")
    print("=" * 60)
    print()
    print("Files are now available for download via the API endpoint:")
    print("  GET /api/client/download/{platform}")
    print()

if __name__ == "__main__":
    main()
