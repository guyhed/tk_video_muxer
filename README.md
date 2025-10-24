# Video Segment Editor

A modern Linux application for cutting and merging video segments with compression.

## Features

- **File Management**: Select multiple video files to process
- **Time Segments**: Define multiple time segments per file (format: h:mm:ss)
- **Video Thumbnails**: Preview frames at segment start/end times
- **Smart Processing**: Cut segments using mkvmerge, then compress with ffmpeg
- **Progress Tracking**: Real-time progress for cutting and compression phases
- **Modern UI**: Clean dark theme with intuitive controls
- **Keyboard Navigation**: Press Enter to navigate between time fields

## System Requirements

- Linux x64 (Ubuntu 20.04+, Debian 11+, or equivalent)
- **mkvmerge** (from mkvtoolnix package)
- **ffmpeg** with libx265 and libvorbis support

### Installing Dependencies

**Ubuntu/Debian:**
```bash
sudo apt install mkvtoolnix ffmpeg
```

**Fedora:**
```bash
sudo dnf install mkvtoolnix ffmpeg
```

**Arch Linux:**
```bash
sudo pacman -S mkvtoolnix ffmpeg
```

## Usage

1. **Run the application:**
   ```bash
   ./VideoSegmentEditor
   ```

2. **Add video files:**
   - Click "Add File" button
   - Browse and select your video file

3. **Define segments:**
   - Click "Add Segment" for each time range you want to keep
   - Enter start and end times (format: h:mm:ss or hh:mm:ss)
   - Times auto-format as you type
   - Press Enter to move between fields

4. **Process videos:**
   - Choose output file location
   - Click "Start Muxing"
   - Wait for processing to complete

## Output Format

- **Video Codec**: H.265 (x265) - High efficiency compression
- **Audio Codec**: Vorbis - Open source audio compression
- **Quality**: CRF 23 (balanced quality/size), Audio quality 5

## Keyboard Shortcuts

- **Enter**: Navigate from start time to end time field
- **Enter** (on end time): Move to next segment or create new one

## Technical Details

### Processing Pipeline

1. **Segment Extraction**: Uses mkvmerge to cut segments without re-encoding (fast and lossless)
2. **Concatenation**: Merges segments into a temporary file
3. **Compression**: Re-encodes with ffmpeg using H.265 and Vorbis codecs

### Configuration

Settings are stored in `~/.config/video_segment_editor/config.json`:
- Last used input folder path
- (Future settings will be added here)

## Troubleshooting

**"mkvmerge not found" error:**
- Install mkvtoolnix package (see dependencies above)

**"ffmpeg not found" error:**
- Install ffmpeg package (see dependencies above)

**Thumbnails not showing:**
- Ensure ffmpeg is installed and working
- Check that video file is not corrupted
- Verify time format is complete (both digits entered)

**Application won't start:**
- Check you have execute permissions: `chmod +x VideoSegmentEditor`
- Run from terminal to see error messages

## Development

This application is built with:
- Python 3.12
- Tkinter (GUI)
- Pillow (Image processing)
- mkvmerge (Video cutting)
- ffmpeg (Video compression)

### Building from Source

See [BUILD.md](BUILD.md) for complete build instructions.

## License

This software is provided as-is for personal and commercial use.

## Support

For issues, questions, or feature requests, please contact the developer.
