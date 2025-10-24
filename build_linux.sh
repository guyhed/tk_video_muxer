#!/bin/bash
# Build script for Linux executable

echo "Building Video Segment Editor for Linux..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.spec

# Build the executable
echo "Building executable..."
pyinstaller --name="VideoSegmentEditor" \
    --onefile \
    --windowed \
    --add-data="assets:assets" \
    --hidden-import="PIL" \
    --hidden-import="PIL.Image" \
    --hidden-import="PIL.ImageTk" \
    app.py

echo ""
echo "Build complete!"
echo "Executable location: dist/VideoSegmentEditor"
echo ""
echo "You can run it with: ./dist/VideoSegmentEditor"
