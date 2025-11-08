# Upload Desktop Client to MongoDB

This guide explains how to upload the desktop client ZIP files to MongoDB so users can download them from your website.

## Step-by-Step Instructions

### Step 1: Package the Client

First, create the ZIP files for each platform:

**Windows:**
```bash
package_client.bat
```

**macOS/Linux:**
```bash
chmod +x package_client.sh
./package_client.sh
```

This creates ZIP files in the `dist/` folder:
- `file-protector-client-windows.zip`
- `file-protector-client-macos.zip`
- `file-protector-client-linux.zip`

### Step 2: Upload to MongoDB

Run the upload script:

**Windows:**
```bash
cd backend
python upload_client.py
```

**macOS/Linux:**
```bash
cd backend
python3 upload_client.py
```

The script will:
1. Check for ZIP files in the `dist/` folder
2. Upload each file to MongoDB GridFS
3. Store them with metadata (platform, upload date, etc.)

### Step 3: Verify Upload

The files are now stored in MongoDB and accessible via:
- `GET /api/client/download/windows`
- `GET /api/client/download/macos`
- `GET /api/client/download/linux`

### Step 4: Test Download

1. Open your deployed website
2. Go to the "📥 Download Client" tab
3. Click any download button
4. The file should download from MongoDB

## Updating Client Files

When you update the client:

1. Make changes to `desktop_client/`
2. Run the packaging script again
3. Run `upload_client.py` again
4. The old files in MongoDB will be replaced automatically

## Troubleshooting

### "Client file not found" Error

This means the files haven't been uploaded to MongoDB yet. Run `upload_client.py` first.

### Upload Script Fails

- Check MongoDB connection string in environment variables
- Verify `dist/` folder exists and contains ZIP files
- Check MongoDB permissions (read/write access)

### Download Doesn't Work

- Verify the backend API is deployed and accessible
- Check browser console for errors
- Ensure CORS is enabled on the backend

## Files Stored in MongoDB

The files are stored in GridFS with:
- **Filename**: `file-protector-client-{platform}.zip`
- **Metadata**: 
  - `platform`: windows, macos, or linux
  - `upload_date`: When uploaded
  - `content_type`: application/zip

## API Endpoint

The download endpoint is:
```
GET /api/client/download/{platform}
```

Where `{platform}` is one of: `windows`, `macos`, or `linux`

Response:
- **200 OK**: File content (binary ZIP)
- **404 Not Found**: File not uploaded yet
- **400 Bad Request**: Invalid platform
- **500 Server Error**: MongoDB connection issue

## Notes

- Files are stored in the same MongoDB database as backups
- Old versions are automatically deleted when uploading new ones
- File size is typically 50-200 KB per platform
- MongoDB GridFS handles large files efficiently

