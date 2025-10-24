# Video Segment Editor - Build Instructions

## Building a Linux Executable

### Prerequisites
- Python 3.8 or higher
- pip package manager
- mkvmerge and ffmpeg installed on your system

### Build Steps

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the build script:**
   ```bash
   ./build_linux.sh
   ```

3. **Find your executable:**
   The executable will be created at `dist/VideoSegmentEditor`

4. **Run the executable:**
   ```bash
   ./dist/VideoSegmentEditor
   ```

### Distribution

To distribute your application:

1. **Package the executable with assets:**
   ```bash
   cd dist
   tar -czf VideoSegmentEditor-linux-x64.tar.gz VideoSegmentEditor
   ```

2. **Users will need:**
   - mkvmerge installed (`sudo apt install mkvtoolnix` on Ubuntu/Debian)
   - ffmpeg installed (`sudo apt install ffmpeg` on Ubuntu/Debian)

### Troubleshooting

- **"Permission denied" error:** Make sure the script is executable with `chmod +x build_linux.sh`
- **Import errors:** Install missing dependencies with `pip install -r requirements.txt`
- **mkvmerge/ffmpeg not found:** Make sure these tools are in your PATH

### Manual Build Options

If you want to customize the build:

```bash
pyinstaller --name="VideoSegmentEditor" \
    --onefile \
    --windowed \
    --add-data="assets:assets" \
    --icon="assets/icon.png" \
    app.py
```

Options explained:
- `--onefile`: Creates a single executable file
- `--windowed`: No console window (GUI only)
- `--add-data`: Includes the assets folder
- `--icon`: Sets the application icon
