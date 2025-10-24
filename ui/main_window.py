import tkinter as tk
from .editor_panel import EditorPanel
from .control_panel import ControlPanel

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video Segment Editor")
        self.root.geometry("950x750")
        self.root.iconphoto(False, tk.PhotoImage(file="assets/icon.png"))

        # Modern dark theme
        bg_color = '#1e1e1e'
        self.root.configure(bg=bg_color)

        # Create main container with two sections
        main_container = tk.Frame(self.root, bg=bg_color)
        main_container.pack(fill='both', expand=True)

        # Lower section - control panel (create first to get callback)
        self.control_panel = ControlPanel(main_container, self.get_editors)
        self.control_panel.frame.pack(side='bottom', fill='x', padx=10, pady=10)
        
        # Upper section - scrollable editors panel
        self.editor_panel = EditorPanel(main_container, self.set_output_path)
        self.editor_panel.frame.pack(side='top', fill='both', expand=True)
    
    def get_editors(self):
        """Get all editors from the editor panel"""
        return self.editor_panel.get_editors()
    
    def set_output_path(self, path):
        """Set the output path in the control panel"""
        self.control_panel.output_path.set(path)

    def run(self):
        self.root.mainloop()


