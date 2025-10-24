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
        # Modern color scheme
        self.bg_color = '#2b2b2b'  # Dark background
        self.fg_color = '#e0e0e0'  # Light text
        self.accent_color = '#3498db'  # Blue accent
        self.entry_bg = '#3c3c3c'  # Dark entry background
        
        self.frame = tk.Frame(parent, bg=self.bg_color, bd=0, relief=tk.FLAT)
        self.file_path = tk.StringVar()
        self.video_duration = None  # Store video duration in seconds
        self.set_output_path_callback = set_output_path_callback
        self.remove_callback = remove_callback
        self.config = ConfigManager()

        # Add subtle border/shadow effect
        self.frame.configure(highlightbackground='#1a1a1a', highlightthickness=1)

        # Header row with file selection and remove button
        header_frame = tk.Frame(self.frame, bg=self.bg_color, bd=0)
        header_frame.pack(fill='x', pady=10, padx=15)
        
        # File selection
        file_row = tk.Frame(header_frame, bg=self.bg_color, bd=0)
        file_row.pack(side=tk.LEFT, fill='x', expand=True)
        
        tk.Label(file_row, text="📁 Video File:", bg=self.bg_color, fg=self.fg_color, 
                font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=10, pady=5)
        
        entry = tk.Entry(file_row, textvariable=self.file_path, width=50, 
                        bg=self.entry_bg, fg=self.fg_color, bd=0, 
                        insertbackground=self.fg_color, relief=tk.FLAT,
                        font=('Segoe UI', 9))
        entry.pack(side=tk.LEFT, padx=5, pady=5, ipady=5)
        
        browse_btn = tk.Button(file_row, text="Browse", command=self.browse_file, 
                              bg=self.accent_color, fg='white', bd=0, relief=tk.FLAT,
                              font=('Segoe UI', 9, 'bold'), cursor='hand2',
                              padx=15, pady=5, activebackground='#2980b9', activeforeground='white')
        browse_btn.pack(side=tk.LEFT, padx=10, pady=5)
        # Add hover effect
        browse_btn.bind('<Enter>', lambda e: browse_btn.config(bg='#2980b9'))
        browse_btn.bind('<Leave>', lambda e: browse_btn.config(bg=self.accent_color))
        
        # Remove editor button with red X
        remove_btn = tk.Button(header_frame, text="✕", command=self.remove_editor, 
                              bg=self.bg_color, fg='#e74c3c', font=('Arial', 18, 'bold'),
                              width=2, height=1, bd=0, relief=tk.FLAT,
                              highlightthickness=0, padx=0, pady=0,
                              activebackground='#1e1e1e', activeforeground='#e74c3c',
                              cursor='hand2')
        remove_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        # Add hover effect
        remove_btn.bind('<Enter>', lambda e: remove_btn.config(bg='#1e1e1e'))
        remove_btn.bind('<Leave>', lambda e: remove_btn.config(bg=self.bg_color))

        # Time segments
        self.segments_frame = tk.Frame(self.frame, bg=self.bg_color, bd=0)
        self.segments_frame.pack(fill='x', pady=5, padx=15)
        self.segments = []

        add_btn = tk.Button(self.frame, text="+ Add Segment", command=self.add_segment, 
                           bg='#27ae60', fg='white', bd=0, relief=tk.FLAT,
                           font=('Segoe UI', 9, 'bold'), cursor='hand2',
                           padx=15, pady=5, activebackground='#229954', activeforeground='white')
        add_btn.pack(pady=10, padx=15)
        # Add hover effect
        add_btn.bind('<Enter>', lambda e: add_btn.config(bg='#229954'))
        add_btn.bind('<Leave>', lambda e: add_btn.config(bg='#27ae60'))
        
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
                # Update all segments with new duration and refresh thumbnails
                for segment in self.segments:
                    segment.update_end_time()
                    segment.refresh_thumbnails()
    
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
    
    def focus_next_segment(self, current_segment):
        """Focus the start field of the next segment, or create a new segment"""
        try:
            current_index = self.segments.index(current_segment)
            
            # Check if there's a next segment
            if current_index + 1 < len(self.segments):
                # Focus next segment's start field
                next_segment = self.segments[current_index + 1]
                next_segment.start_entry.focus_set()
                next_segment.start_entry.select_range(0, tk.END)
            else:
                # No next segment - create a new one
                self.add_segment()
                # Focus the newly created segment's start field
                if self.segments:
                    new_segment = self.segments[-1]
                    new_segment.start_entry.focus_set()
                    new_segment.start_entry.select_range(0, tk.END)
        except ValueError:
            # Current segment not in list (shouldn't happen)
            pass
