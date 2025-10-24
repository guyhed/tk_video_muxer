import tkinter as tk
import re

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
        
        # Add validation
        vcmd = (parent.register(self.validate_time), '%P')
        
        tk.Label(self.frame, text="⏱ Start:", bg=bg_color, fg=fg_color, 
                font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=8, pady=5)
        self.start_entry = tk.Entry(self.frame, textvariable=self.start_var, width=10, 
                                    bg=entry_bg, fg=fg_color, bd=0, relief=tk.FLAT,
                                    insertbackground=fg_color, font=('Consolas', 9),
                                    validate='key', validatecommand=vcmd)
        self.start_entry.pack(side=tk.LEFT, padx=5, pady=5, ipady=3)
        
        tk.Label(self.frame, text="End:", bg=bg_color, fg=fg_color, 
                font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=8, pady=5)
        self.end_entry = tk.Entry(self.frame, textvariable=self.end_var, width=10, 
                                  bg=entry_bg, fg=fg_color, bd=0, relief=tk.FLAT,
                                  insertbackground=fg_color, font=('Consolas', 9),
                                  validate='key', validatecommand=vcmd)
        self.end_entry.pack(side=tk.LEFT, padx=5, pady=5, ipady=3)
        
        self.remove_button = tk.Button(self.frame, text="✕", command=self.remove, 
                                       bg=bg_color, fg='#e74c3c', bd=0, relief=tk.FLAT,
                                       font=('Arial', 12, 'bold'), cursor='hand2',
                                       highlightthickness=0, width=2,
                                       activebackground=bg_color, activeforeground='#c0392b')
        self.remove_button.pack(side=tk.LEFT, padx=10, pady=5)
        
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
