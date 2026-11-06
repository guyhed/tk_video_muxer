#!/bin/bash
# Build script for Linux executable

echo "Building tk_video_muxer for Linux..."

# Check the virtual environment exists AND still works.  A venv keeps its
# packages in .venv/lib/pythonX.Y/, so when the system python is upgraded
# (3.12 -> 3.14, say) the interpreter stops looking in the old directory and
# every installed package silently vanishes.  Detect that and rebuild.
VENV_STALE=""
if [ ! -d ".venv" ]; then
    VENV_STALE="not found"
elif ! .venv/bin/python -c "import sys" &> /dev/null; then
    VENV_STALE="interpreter is broken"
else
    PYVER=$(.venv/bin/python -c 'import sys; print("%d.%d" % sys.version_info[:2])')
    if [ ! -d ".venv/lib/python$PYVER" ]; then
        echo "Virtual environment was built for a different Python."
        echo "  interpreter is now: $PYVER   (no .venv/lib/python$PYVER)"
        VENV_STALE="built for another Python version"
    fi
fi

if [ -n "$VENV_STALE" ]; then
    echo "Virtual environment $VENV_STALE. Creating..."
    rm -rf .venv
    python3 -m venv .venv || { echo "ERROR: could not create .venv"; exit 1; }
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check the build dependencies are importable in the venv
if ! .venv/bin/python -c "import PIL, PyInstaller" &> /dev/null
then
    echo "Build dependencies missing in venv. Installing..."
    .venv/bin/pip install -r requirements.txt || { echo "ERROR: pip install failed"; exit 1; }
fi

# Clean previous builds (the .spec is deliberately kept — see below)
echo "Cleaning previous builds..."
rm -rf build dist

# Build the executable.  If a spec file already exists it is the source of
# truth, so any customisation in it survives a rebuild; otherwise generate
# one from the flags below.
SPEC="VideoSegmentEditor.spec"
if [ -f "$SPEC" ]; then
    echo "Building executable from $SPEC..."
    .venv/bin/pyinstaller --noconfirm "$SPEC"
else
    echo "No $SPEC found. Generating one and building..."
    .venv/bin/pyinstaller --noconfirm --name="VideoSegmentEditor" \
        --onefile \
        --windowed \
        --add-data="assets:assets" \
        --hidden-import="PIL" \
        --hidden-import="PIL.Image" \
        --hidden-import="PIL.ImageTk" \
        app.py
fi

# Deactivate virtual environment
deactivate

echo ""
echo "Build complete!"
echo "Executable location: dist/VideoSegmentEditor"
echo ""
echo "You can run it with: ./dist/VideoSegmentEditor"
