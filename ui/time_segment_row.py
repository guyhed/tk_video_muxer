import tkinter as tk
import re
import threading
from .thumbnail_extractor import ThumbnailExtractor

class TimeSegmentRow:
    def __init__(self, parent, editor, start_time="00:00"):
        self.editor = editor
        
        # Modern colors matching parent editor
        bg_color = '#2b2b2b'
        fg_color = '#e0e0e0'
        entry_bg = '#3c3c3c'
        
        self.frame = tk.Frame(parent, bg=bg_color, bd=0)
        self.start_var = tk.StringVar(value=start_time)
        self.end_var = tk.StringVar()
        
        # Store references to thumbnails to prevent garbage collection
        self.start_thumbnail = None
        self.end_thumbnail = None
        
        # Add validation
        vcmd = (parent.register(self.validate_time), '%P')
        
        tk.Label(self.frame, text="⏱ Start:", bg=bg_color, fg=fg_color, 
                font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=8, pady=5)
        self.start_entry = tk.Entry(self.frame, textvariable=self.start_var, width=10, 
                                    bg=entry_bg, fg=fg_color, bd=0, relief=tk.FLAT,
                                    insertbackground=fg_color, font=('Consolas', 9),
                                    validate='key', validatecommand=vcmd)
        self.start_entry.pack(side=tk.LEFT, padx=5, pady=5, ipady=3)
        
        # Start thumbnail
        self.start_thumb_label = tk.Label(self.frame, bg=bg_color, bd=1, relief=tk.SOLID)
        self.start_thumb_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Label(self.frame, text="End:", bg=bg_color, fg=fg_color, 
                font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=8, pady=5)
        self.end_entry = tk.Entry(self.frame, textvariable=self.end_var, width=10, 
                                  bg=entry_bg, fg=fg_color, bd=0, relief=tk.FLAT,
                                  insertbackground=fg_color, font=('Consolas', 9),
                                  validate='key', validatecommand=vcmd)
        self.end_entry.pack(side=tk.LEFT, padx=5, pady=5, ipady=3)
        
        # End thumbnail
        self.end_thumb_label = tk.Label(self.frame, bg=bg_color, bd=1, relief=tk.SOLID)
        self.end_thumb_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.remove_button = tk.Button(self.frame, text="✕", command=self.remove, 
                                       bg=bg_color, fg='#e74c3c', bd=0, relief=tk.FLAT,
                                       font=('Arial', 12, 'bold'), cursor='hand2',
                                       highlightthickness=0, width=2,
                                       activebackground='#1e1e1e', activeforeground='#e74c3c')
        self.remove_button.pack(side=tk.LEFT, padx=10, pady=5)
        # Add hover effect - darken background, keep text color
        self.remove_button.bind('<Enter>', lambda e: self.remove_button.config(bg='#1e1e1e'))
        self.remove_button.bind('<Leave>', lambda e: self.remove_button.config(bg=bg_color))
        
        # Bind events to update thumbnails when time changes
        self.start_var.trace('w', lambda *args: self.schedule_thumbnail_update('start'))
        self.end_var.trace('w', lambda *args: self.schedule_thumbnail_update('end'))
        
        # Bind Enter key for navigation
        self.start_entry.bind('<Return>', self.on_start_enter)
        self.end_entry.bind('<Return>', self.on_end_enter)
        
        # Bind key release for auto-colon insertion
        self.start_entry.bind('<KeyRelease>', lambda e: self.auto_format_time(self.start_entry, self.start_var))
        self.end_entry.bind('<KeyRelease>', lambda e: self.auto_format_time(self.end_entry, self.end_var))
        
        # Initialize placeholders
        self.update_thumbnail_placeholder('start')
        self.update_thumbnail_placeholder('end')
        
        # Initialize end time with video duration if available
        self.update_end_time()

    def validate_time(self, value):
        """Validate time format: flexible formats like h:mm:ss, hh:mm:ss, m:ss, mm:ss"""
        if value == "":
            return True
        
        # Allow flexible partial input while typing
        # Each part can be 1-2 digits, and we can have up to 3 parts separated by colons
        # Also allow trailing colon
        pattern = r'^(\d{1,2})?(:)?(\d{0,2})?(:)?(\d{0,2})?$'
        if not re.match(pattern, value):
            return False
        
        parts = value.split(':')
        if len(parts) > 3:
            return False
        
        # Validate each part doesn't exceed valid ranges
        for i, part in enumerate(parts):
            if part and part.isdigit():
                num = int(part)
                if i == len(parts) - 1:  # seconds (last part)
                    if num > 59:
                        return False
                elif i == len(parts) - 2 and len(parts) > 1:  # minutes (middle part when we have multiple parts)
                    if num > 59:
                        return False
                # hours (first part) can be any value
        
        return True
    
    def auto_format_time(self, entry, var):
        """Automatically insert colons after every 2 digits and pad single digits when user types colon"""
        value = var.get()
        cursor_pos = entry.index(tk.INSERT)
        
        # Check if user just typed a colon
        if value.endswith(':'):
            # Split by colon to check the last segment before the colon
            parts = value[:-1].split(':')
            if parts:
                last_part = parts[-1]
                # If last part is a single digit, pad it with 0
                if len(last_part) == 1 and last_part.isdigit():
                    parts[-1] = '0' + last_part
                    formatted = ':'.join(parts) + ':'
                    var.set(formatted)
                    entry.icursor(len(formatted))
                    return
        
        # Don't auto-format if user has already typed colons manually
        # This allows formats like 1:23:45
        if ':' in value:
            return
        
        # Remove any existing colons for processing (only for continuous digit entry)
        digits_only = value.replace(':', '')
        
        # Only process if we have digits
        if not digits_only or not digits_only.isdigit():
            return
        
        # Build formatted string with colons - only auto-add for continuous digit entry
        formatted = ''
        for i, digit in enumerate(digits_only):
            formatted += digit
            # Add colon after 2nd and 4th digit (but not at the end)
            if (i == 1 or i == 3) and i < len(digits_only) - 1:
                formatted += ':'
        
        # Only update if the format changed
        if formatted != value:
            var.set(formatted)
            # Try to maintain cursor position
            # Account for added colons
            new_cursor_pos = len(formatted)
            if cursor_pos <= len(formatted):
                new_cursor_pos = min(cursor_pos + (formatted.count(':') - value.count(':')), len(formatted))
            entry.icursor(new_cursor_pos)

    def update_end_time(self):
        """Update end time with video duration if available and not already set"""
        if not self.end_var.get():  # Only update if empty
            duration_str = self.editor.get_duration_str()
            if duration_str:
                self.end_var.set(duration_str)

    def remove(self):
        self.editor.remove_segment(self)
    
    def schedule_thumbnail_update(self, field):
        """Schedule a thumbnail update after a short delay (debouncing)"""
        # Cancel any pending update
        if hasattr(self, f'_{field}_update_timer'):
            timer = getattr(self, f'_{field}_update_timer')
            if timer:
                timer.cancel()
        
        # Schedule new update after 500ms delay
        timer = threading.Timer(0.5, lambda: self.update_thumbnail(field))
        timer.daemon = True
        timer.start()
        setattr(self, f'_{field}_update_timer', timer)
    
    def update_thumbnail_placeholder(self, field):
        """Show a placeholder when no thumbnail is available"""
        placeholder = ThumbnailExtractor.create_placeholder(width=120, height=68)
        if placeholder:
            if field == 'start':
                self.start_thumbnail = placeholder
                self.start_thumb_label.config(image=placeholder)
            else:
                self.end_thumbnail = placeholder
                self.end_thumb_label.config(image=placeholder)
    
    def update_thumbnail(self, field):
        """Update thumbnail for start or end time"""
        # Get video path from editor
        video_path = self.editor.file_path.get()
        if not video_path:
            self.update_thumbnail_placeholder(field)
            return
        
        # Get time value
        time_var = self.start_var if field == 'start' else self.end_var
        time_str = time_var.get()
        
        # Validate time format before extracting
        if not time_str or not self.validate_time(time_str):
            self.update_thumbnail_placeholder(field)
            return
        
        # Check if time has proper format (contains at least one colon)
        if ':' not in time_str:
            self.update_thumbnail_placeholder(field)
            return
        
        # Check if time string is complete (not partial like "01:" or "01:2")
        parts = time_str.split(':')
        if len(parts) == 2:  # m:ss or mm:ss format
            if len(parts[0]) == 0 or len(parts[1]) < 2:
                self.update_thumbnail_placeholder(field)
                return
        elif len(parts) == 3:  # h:mm:ss or hh:mm:ss format
            if len(parts[0]) == 0 or len(parts[1]) < 2 or len(parts[2]) < 2:
                self.update_thumbnail_placeholder(field)
                return
        else:
            self.update_thumbnail_placeholder(field)
            return
        
        # Extract thumbnail in background thread
        def extract_and_update():
            thumbnail = ThumbnailExtractor.extract_thumbnail(video_path, time_str)
            
            # Update UI in main thread
            if thumbnail:
                if field == 'start':
                    self.start_thumbnail = thumbnail
                    self.start_thumb_label.config(image=thumbnail)
                else:
                    self.end_thumbnail = thumbnail
                    self.end_thumb_label.config(image=thumbnail)
            else:
                self.update_thumbnail_placeholder(field)
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=extract_and_update, daemon=True)
        thread.start()
    
    def refresh_thumbnails(self):
        """Refresh both thumbnails (called when file changes)"""
        self.update_thumbnail('start')
        self.update_thumbnail('end')
    
    def on_start_enter(self, event):
        """Handle Enter key in start field - move to end field"""
        self.end_entry.focus_set()
        self.end_entry.select_range(0, tk.END)
        return 'break'  # Prevent default behavior
    
    def on_end_enter(self, event):
        """Handle Enter key in end field - move to next segment or create one"""
        # Ask editor to focus next segment or create new one
        self.editor.focus_next_segment(self)
        return 'break'  # Prevent default behavior
