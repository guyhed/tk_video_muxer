#!/bin/bash
# Build script for Linux executable

echo "Building tk_video_muxer for Linux..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check if PyInstaller is installed in venv
if ! .venv/bin/python -c "import pyinstaller" &> /dev/null
then
    echo "PyInstaller not found in venv. Installing dependencies..."
    .venv/bin/pip install -r requirements.txt
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.spec

# Build the executable
echo "Building executable..."
.venv/bin/pyinstaller --name="VideoSegmentEditor" \
    --onefile \
    --windowed \
    --add-data="assets:assets" \
    --hidden-import="PIL" \
    --hidden-import="PIL.Image" \
    --hidden-import="PIL.ImageTk" \
    app.py

# Deactivate virtual environment
deactivate

echo ""
echo "Build complete!"
echo "Executable location: dist/VideoSegmentEditor"
echo ""
echo "You can run it with: ./dist/VideoSegmentEditor"
