import tkinter as tk
import sys
import os
from .editor_panel import EditorPanel
from .control_panel import ControlPanel


def _asset(relative_path):
    """Resolve a bundled asset path whether running from source or PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller extracts bundled data to a temp folder stored in _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    # Running from source: paths are relative to the project root (one level up)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, relative_path)


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("tk_video_muxer")
        self.root.geometry("950x750")
        self.root.iconphoto(False, tk.PhotoImage(file=_asset("assets/icon.png")))

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


