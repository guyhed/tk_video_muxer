import tkinter as tk
from tkinter import filedialog
from .time_segment_row import TimeSegmentRow
import os
import sys

# Add parent directory to path to import config_manager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_manager import ConfigManager

class FileSegmentEditor:
    def __init__(self, parent, set_output_path_callback=None, remove_callback=None):
        self.frame = tk.Frame(parent, bg='pink', bd=0)
        self.file_path = tk.StringVar()
        self.video_duration = None  # Store video duration in seconds
        self.set_output_path_callback = set_output_path_callback
        self.remove_callback = remove_callback
        self.config = ConfigManager()

        # Header row with file selection and remove button
        header_frame = tk.Frame(self.frame, bg='pink', bd=0)
        header_frame.pack(fill='x', pady=5, padx=15)
        
        # File selection
        file_row = tk.Frame(header_frame, bg='pink', bd=0)
        file_row.pack(side=tk.LEFT, fill='x', expand=True)
        
        tk.Label(file_row, text="Select File:", bg='pink', bd=0).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Entry(file_row, textvariable=self.file_path, width=50, bd=0).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(file_row, text="Browse", command=self.browse_file, bd=0).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Remove editor button with red X on transparent background
        remove_btn = tk.Button(header_frame, text="✕", command=self.remove_editor, 
                              bg='pink', fg='red', font=('Arial', 16, 'bold'),
                              width=2, height=1, bd=0, relief=tk.FLAT,
                              highlightthickness=0, padx=0, pady=0,
                              activebackground='pink', activeforeground='darkred',
                              cursor='hand2')
        remove_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        # Time segments
        self.segments_frame = tk.Frame(self.frame, bg='pink', bd=0)
        self.segments_frame.pack(fill='x', pady=5, padx=15)
        self.segments = []

        tk.Button(self.frame, text="Add Segment", command=self.add_segment, bd=0).pack(pady=10, padx=15)
        
        # Don't add initial segment - wait for file selection

    def browse_file(self):
        # Video file extensions
        video_types = [
            ("Video files", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.m4v *.mpg *.mpeg *.3gp"),
            ("MP4 files", "*.mp4"),
            ("MKV files", "*.mkv"),
            ("AVI files", "*.avi"),
            ("All files", "*.*")
        ]
        
        # Get initial directory from config
        initial_dir = self.config.get_input_folder_path()
        
        if initial_dir:
            path = filedialog.askopenfilename(filetypes=video_types, initialdir=initial_dir)
        else:
            path = filedialog.askopenfilename(filetypes=video_types)
        if path:
            self.file_path.set(path)
            self.get_video_duration(path)
            
            # Generate output filename
            self.generate_output_filename(path)
            
            # Add first segment if this is the first file selection
            if not self.segments:
                self.add_segment()
            else:
                # Update all segments with new duration
                for segment in self.segments:
                    segment.update_end_time()
    
    def generate_output_filename(self, input_path):
        """Generate output filename based on input file"""
        if not self.set_output_path_callback:
            return
        
        # Get the base name and directory
        dir_name = os.path.dirname(input_path)
        file_name = os.path.basename(input_path)
        name_without_ext, ext = os.path.splitext(file_name)
        
        # Generate output name
        if ext.lower() == '.mkv':
            output_name = f"{name_without_ext}.output.mkv"
        else:
            output_name = f"{name_without_ext}.mkv"
        
        output_path = os.path.join(dir_name, output_name)
        self.set_output_path_callback(output_path)

    def get_video_duration(self, file_path):
        """Get video duration using ffprobe or moviepy"""
        try:
            import subprocess
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                self.video_duration = float(result.stdout.strip())
            else:
                self.video_duration = None
        except (FileNotFoundError, Exception):
            # ffprobe not available, try moviepy
            try:
                from moviepy.editor import VideoFileClip
                clip = VideoFileClip(file_path)
                self.video_duration = clip.duration
                clip.close()
            except:
                self.video_duration = None

    def add_segment(self):
        # Determine start time from previous segment
        start_time = "00:00"
        if self.segments:
            # Get end time of last segment
            prev_end = self.segments[-1].end_var.get()
            if prev_end:
                start_time = prev_end
        
        segment = TimeSegmentRow(self.segments_frame, self, start_time)
        self.segments.append(segment)
        segment.frame.pack(fill='x', pady=2)
        self.update_remove_buttons()

    def remove_segment(self, segment):
        if len(self.segments) > 1:  # Only remove if more than one segment
            segment.frame.destroy()
            self.segments.remove(segment)
            self.update_remove_buttons()
    
    def update_remove_buttons(self):
        # Disable remove button if only one segment remains
        for segment in self.segments:
            if len(self.segments) <= 1:
                segment.remove_button.config(state=tk.DISABLED)
            else:
                segment.remove_button.config(state=tk.NORMAL)
    
    def get_duration_str(self):
        """Convert video duration to time string"""
        if self.video_duration is None:
            return ""
        
        total_seconds = int(self.video_duration)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def remove_editor(self):
        """Remove this editor from the parent"""
        if self.remove_callback:
            self.remove_callback(self)
