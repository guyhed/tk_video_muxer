import tkinter as tk
import re

class TimeSegmentRow:
    def __init__(self, parent, editor, start_time="00:00"):
        self.editor = editor
        self.frame = tk.Frame(parent, bg='pink', bd=0)
        self.start_var = tk.StringVar(value=start_time)
        self.end_var = tk.StringVar()
        
        # Add validation
        vcmd = (parent.register(self.validate_time), '%P')
        
        tk.Label(self.frame, text="Start:", bg='pink', bd=0).pack(side=tk.LEFT, padx=5, pady=3)
        self.start_entry = tk.Entry(self.frame, textvariable=self.start_var, width=10, bd=0, validate='key', validatecommand=vcmd)
        self.start_entry.pack(side=tk.LEFT, padx=5, pady=3)
        
        tk.Label(self.frame, text="End:", bg='pink', bd=0).pack(side=tk.LEFT, padx=5, pady=3)
        self.end_entry = tk.Entry(self.frame, textvariable=self.end_var, width=10, bd=0, validate='key', validatecommand=vcmd)
        self.end_entry.pack(side=tk.LEFT, padx=5, pady=3)
        
        self.remove_button = tk.Button(self.frame, text="Remove", command=self.remove, bd=0)
        self.remove_button.pack(side=tk.LEFT, padx=10, pady=3)
        
        # Initialize end time with video duration if available
        self.update_end_time()

    def validate_time(self, value):
        """Validate time format: hh:mm:ss or mm:ss"""
        if value == "":
            return True
        
        # Allow partial input while typing
        pattern = r'^(\d{0,2})?(:)?(\d{0,2})?(:)?(\d{0,2})?$'
        if not re.match(pattern, value):
            return False
        
        parts = value.split(':')
        if len(parts) > 3:
            return False
        
        # Validate each part doesn't exceed valid ranges
        for i, part in enumerate(parts):
            if part and part.isdigit():
                num = int(part)
                if i == len(parts) - 1:  # seconds
                    if num > 59:
                        return False
                elif i == len(parts) - 2:  # minutes
                    if num > 59:
                        return False
                # hours can be any value
        
        return True

    def update_end_time(self):
        """Update end time with video duration if available and not already set"""
        if not self.end_var.get():  # Only update if empty
            duration_str = self.editor.get_duration_str()
            if duration_str:
                self.end_var.set(duration_str)

    def remove(self):
        self.editor.remove_segment(self)
