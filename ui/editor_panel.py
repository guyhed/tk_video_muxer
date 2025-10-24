import tkinter as tk
from .file_segment_editor import FileSegmentEditor

class EditorPanel:
    """Upper panel containing scrollable file segment editors"""
    
    def __init__(self, parent, set_output_path_callback=None):
        """
        Initialize the EditorPanel
        
        Args:
            parent: Parent tkinter widget
            set_output_path_callback: Function to call to set output path
        """
        self.set_output_path_callback = set_output_path_callback
        
        # Modern dark theme colors
        bg_color = '#1e1e1e'
        scroll_bg = '#2b2b2b'
        accent_color = '#3498db'
        
        # Create main frame for the panel
        self.frame = tk.Frame(parent, bg=bg_color)
        
        # Add button at the top left corner (modern style)
        button_container = tk.Frame(self.frame, bg=bg_color)
        button_container.pack(side="top", fill="x", padx=10, pady=10)
        
        add_editor_btn = tk.Button(button_container, text="➕ Add File", 
                                   command=self.add_editor,
                                   bg=accent_color, fg='white', bd=0, relief=tk.FLAT,
                                   font=('Segoe UI', 10, 'bold'), cursor='hand2',
                                   highlightthickness=0, padx=15, pady=6,
                                   activebackground='#2980b9', activeforeground='white')
        add_editor_btn.pack(side="left")
        
        # Create a canvas with scrollbar for editors
        canvas = tk.Canvas(self.frame, bg=bg_color, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=scroll_bg)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Make scrollable_frame fill the canvas width
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", configure_canvas_width)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # List to hold FileSegmentEditor instances
        self.editors = []

        # Add initial editor
        self.add_editor()
    
    def add_editor(self):
        """Add a new file segment editor"""
        editor = FileSegmentEditor(self.scrollable_frame, self.set_output_path_callback, self.remove_editor)
        self.editors.append(editor)
        editor.frame.pack(pady=10, fill='x', padx=10)
    
    def remove_editor(self, editor):
        """Remove an editor from the panel"""
        if len(self.editors) > 1:  # Keep at least one editor
            editor.frame.destroy()
            self.editors.remove(editor)
        else:
            # Show message that at least one editor is required
            from tkinter import messagebox
            messagebox.showwarning("Cannot Remove", "At least one editor must remain.")
    
    def get_editors(self):
        """
        Get all editors
        
        Returns:
            List of FileSegmentEditor instances
        """
        return self.editors
