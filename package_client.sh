#!/bin/bash

echo "========================================"
echo "Packaging Desktop Client for Distribution"
echo "========================================"
echo ""

# Create dist folder if it doesn't exist
mkdir -p dist

# Create platform-specific packages
echo "Creating Windows package..."
cd desktop_client
zip -r ../dist/file-protector-client-windows.zip . -x "*.pyc" "__pycache__/*" "*.git*" > /dev/null 2>&1
echo "✓ Windows package created: dist/file-protector-client-windows.zip"

echo ""
echo "Creating macOS package..."
zip -r ../dist/file-protector-client-macos.zip . -x "*.pyc" "__pycache__/*" "*.git*" > /dev/null 2>&1
echo "✓ macOS package created: dist/file-protector-client-macos.zip"

echo ""
echo "Creating Linux package..."
cp ../dist/file-protector-client-macos.zip ../dist/file-protector-client-linux.zip
echo "✓ Linux package created: dist/file-protector-client-linux.zip"

cd ..

echo ""
echo "========================================"
echo "Packaging Complete!"
echo "========================================"
echo ""
echo "Packages created in 'dist' folder:"
echo "  - file-protector-client-windows.zip"
echo "  - file-protector-client-macos.zip"
echo "  - file-protector-client-linux.zip"
echo ""
echo "Next steps:"
echo "  1. Upload these ZIP files to GitHub Releases"
echo "  2. Or host them in your public folder and update Download.js"
echo "  3. Update Download.js with the correct download URLs"
echo ""

