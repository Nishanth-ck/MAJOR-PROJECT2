"""
Script to package desktop client and upload to MongoDB
"""

import os
import shutil
import sys
from pathlib import Path

# Create dist folder if it doesn't exist
dist_folder = Path("dist")
dist_folder.mkdir(exist_ok=True)

# Create ZIP files
print("=" * 60)
print("Packaging Desktop Client Files")
print("=" * 60)
print()

platforms = ["windows", "macos", "linux"]
desktop_client_folder = Path("desktop_client")

if not desktop_client_folder.exists():
    print(f"❌ Error: {desktop_client_folder} folder not found!")
    sys.exit(1)

for platform in platforms:
    zip_path = dist_folder / f"file-protector-client-{platform}.zip"
    
    # Remove existing ZIP if it exists
    if zip_path.exists():
        zip_path.unlink()
    
    # Create ZIP file
    print(f"Creating {platform} package...")
    shutil.make_archive(
        str(dist_folder / f"file-protector-client-{platform}"),
        'zip',
        desktop_client_folder
    )
    
    if zip_path.exists():
        size = zip_path.stat().st_size
        print(f"✅ Created {zip_path.name} ({size:,} bytes)")
    else:
        print(f"❌ Failed to create {zip_path.name}")

print()
print("=" * 60)
print("Packaging Complete!")
print("=" * 60)
print()

# Now upload to MongoDB
print("=" * 60)
print("Uploading to MongoDB")
print("=" * 60)
print()

# Change to backend directory and run upload script
backend_folder = Path("backend")
if backend_folder.exists():
    os.chdir(backend_folder)
    sys.path.insert(0, str(Path.cwd()))
    
    # Import and run upload script
    try:
        from upload_client import main as upload_main
        upload_main()
    except Exception as e:
        print(f"❌ Error uploading to MongoDB: {e}")
        print("\nYou can manually upload by running:")
        print("  cd backend")
        print("  python upload_client.py")
else:
    print("❌ backend folder not found!")
    print("\nPlease run manually:")
    print("  cd backend")
    print("  python upload_client.py")

