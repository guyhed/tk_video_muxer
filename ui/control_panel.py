import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from .video_muxer import VideoMuxer
import threading

class ControlPanel:
    """Lower panel containing output controls and progress tracking"""
    
    def __init__(self, parent, get_editors_callback):
        """
        Initialize the ControlPanel
        
        Args:
            parent: Parent tkinter widget
            get_editors_callback: Function to call to get list of editors
        """
        self.get_editors_callback = get_editors_callback
        self.root = parent.winfo_toplevel()  # Get root window for threading
        
        # Create main frame for the panel
        self.frame = tk.Frame(parent, bd=2, relief=tk.GROOVE, bg='lightgray')
        
        # Output file selection
        output_row = tk.Frame(self.frame, bg='lightgray')
        output_row.pack(fill='x', pady=10, padx=10)
        
        tk.Label(output_row, text="Output File:", bg='lightgray').pack(side=tk.LEFT, padx=5)
        self.output_path = tk.StringVar()
        tk.Entry(output_row, textvariable=self.output_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(output_row, text="Browse", command=self.browse_output).pack(side=tk.LEFT, padx=5)

        # Start muxing button
        button_row = tk.Frame(self.frame, bg='lightgray')
        button_row.pack(fill='x', pady=5, padx=10)
        
        self.start_button = tk.Button(button_row, text="Start Muxing", command=self.start_muxing, 
                                       bg='green', fg='white', font=('Arial', 12, 'bold'))
        self.start_button.pack(pady=5)

        # Progress bar and labels
        progress_frame = tk.Frame(self.frame, bg='lightgray')
        progress_frame.pack(fill='x', pady=10, padx=10)
        
        # Progress label (status message)
        self.progress_label = tk.Label(progress_frame, text="Ready", bg='lightgray', font=('Arial', 10))
        self.progress_label.pack(pady=5)
        
        # Percentage label (shown above progress bar, hidden by default)
        self.percentage_label = tk.Label(progress_frame, text="", bg='lightgray', font=('Arial', 12, 'bold'))
        self.percentage_label.pack(pady=2)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400, maximum=100)
        self.progress_bar.pack(fill='x', pady=5)
    
    def browse_output(self):
        """Open file dialog to select output file"""
        path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if path:
            self.output_path.set(path)

    def start_muxing(self):
        """Start the video muxing process"""
        if not self.output_path.get():
            messagebox.showerror("Error", "Please select an output file")
            return
        
        # Get editors from callback
        editors = self.get_editors_callback()
        
        # Validate that we have editors with segments
        if not editors:
            messagebox.showerror("Error", "No file editors found")
            return
        
        # Disable start button during processing
        self.start_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Starting muxing process...")
        
        # Run muxing in a separate thread to avoid blocking the UI
        thread = threading.Thread(target=self.run_muxing_process, args=(editors,))
        thread.daemon = True
        thread.start()

    def run_muxing_process(self, editors):
        """
        Execute the actual muxing process using VideoMuxer
        
        Args:
            editors: List of FileSegmentEditor instances
        """
        try:
            # Create VideoMuxer instance with progress callback
            muxer = VideoMuxer(progress_callback=self.update_progress)
            
            # Process videos
            muxer.process_videos(editors, self.output_path.get())
            
            # Show success message
            self.root.after(100, lambda: messagebox.showinfo("Success", "Muxing completed successfully!"))
            
        except Exception as e:
            error_msg = str(e)
            self.update_progress(0, "Error occurred")
            self.root.after(100, lambda: messagebox.showerror("Error", f"Muxing failed: {error_msg}"))
        
        finally:
            # Re-enable start button and hide percentage
            self.root.after(100, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(100, lambda: self.percentage_label.config(text=""))
    
    def update_progress(self, value, text):
        """
        Update progress bar and label (thread-safe)
        
        Args:
            value: Progress value (0-100)
            text: Progress text to display
        """
        self.root.after(0, lambda: self.progress_bar.config(value=value))
        self.root.after(0, lambda: self.progress_label.config(text=text))
        # Only show percentage if value > 0 (active muxing)
        if value > 0:
            self.root.after(0, lambda: self.percentage_label.config(text=f"{value}%"))
        else:
            self.root.after(0, lambda: self.percentage_label.config(text=""))
