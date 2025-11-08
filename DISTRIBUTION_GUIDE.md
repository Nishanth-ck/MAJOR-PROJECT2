# Desktop Client Distribution Guide

This guide explains how to distribute the desktop client to your users.

## Overview

The desktop client needs to be packaged and made available for download. There are several ways to do this:

1. **GitHub Releases** (Recommended)
2. **Host in Public Folder** (Vercel)
3. **Cloud Storage** (AWS S3, Google Cloud Storage, etc.)

## Option 1: GitHub Releases (Recommended)

### Step 1: Package the Client

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

### Step 2: Create GitHub Release

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag version (e.g., `v1.0.0`)
4. Upload the three ZIP files
5. Add release notes
6. Publish the release

### Step 3: Update Download Component

Edit `frontend/src/components/Download.js` and update the `handleDownload` function:

```javascript
const handleDownload = (platform) => {
  const version = 'v1.0.0'; // Update this with your release version
  const repoUrl = 'https://github.com/YOUR_USERNAME/YOUR_REPO';
  const downloadUrl = `${repoUrl}/releases/download/${version}/file-protector-client-${platform}.zip`;
  window.open(downloadUrl, '_blank');
};
```

## Option 2: Host in Public Folder (Vercel)

### Step 1: Package the Client

Run the packaging script as described above.

### Step 2: Add to Public Folder

1. Create `frontend/public/downloads/` folder
2. Copy the ZIP files:
   ```bash
   cp dist/file-protector-client-*.zip frontend/public/downloads/
   ```

### Step 3: Update Download Component

Edit `frontend/src/components/Download.js`:

```javascript
const handleDownload = (platform) => {
  const downloadUrl = `/downloads/file-protector-client-${platform}.zip`;
  window.location.href = downloadUrl;
};
```

### Step 4: Deploy

The files will be available at:
- `https://your-app.vercel.app/downloads/file-protector-client-windows.zip`
- `https://your-app.vercel.app/downloads/file-protector-client-macos.zip`
- `https://your-app.vercel.app/downloads/file-protector-client-linux.zip`

## Option 3: Cloud Storage (AWS S3, Google Cloud, etc.)

### Step 1: Upload to Cloud Storage

Upload the ZIP files to your cloud storage bucket.

### Step 2: Make Files Public

Set the files to be publicly accessible.

### Step 3: Update Download Component

Edit `frontend/src/components/Download.js`:

```javascript
const handleDownload = (platform) => {
  const downloadUrl = `https://your-bucket.s3.amazonaws.com/file-protector-client-${platform}.zip`;
  window.location.href = downloadUrl;
};
```

## Updating the Client

When you update the client:

1. Make changes to `desktop_client/`
2. Run the packaging script
3. Create a new GitHub release (if using Option 1)
4. Or replace files in public folder/cloud storage
5. Update version number in Download.js

## Pre-configuring the Client

You can pre-configure the client with your API URL:

1. Before packaging, edit `desktop_client/client.py`
2. Set a default `API_BASE_URL`:
   ```python
   API_BASE_URL = os.environ.get("API_BASE_URL", "https://your-app.vercel.app")
   ```
3. Package the client

This way, users only need to run the installer and start the client.

## Creating an Installer (Advanced)

For a better user experience, you can create platform-specific installers:

### Windows: NSIS or Inno Setup
- Create an installer that:
  - Checks for Python
  - Installs dependencies
  - Creates desktop shortcut
  - Sets up auto-start

### macOS: DMG with Installer
- Create a DMG file with:
  - Drag-to-install
  - Launch Agent setup
  - Application bundle

### Linux: .deb or .rpm Package
- Create distribution packages for:
  - Debian/Ubuntu (.deb)
  - Red Hat/Fedora (.rpm)

## Testing Downloads

1. Package the client
2. Test downloading each platform's ZIP
3. Verify extraction works
4. Test installation on each platform
5. Verify client connects to your backend

## Current Implementation

The current `Download.js` component uses a placeholder GitHub URL. You need to:

1. **Update the repository URL** in `Download.js`:
   ```javascript
   const repoUrl = 'https://github.com/YOUR_USERNAME/YOUR_REPO/releases/latest';
   ```

2. **Or implement one of the hosting options** above

3. **Test the download links** to ensure they work

## Recommended Approach

For production, I recommend:

1. **Use GitHub Releases** for versioning and distribution
2. **Pre-configure** the client with your API URL
3. **Add clear installation instructions** in the Download page
4. **Provide support** via GitHub Issues or email

This gives you:
- Version control
- Easy updates
- Professional distribution
- User trust (GitHub is well-known)

