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
        
        # Modern colors
        bg_color = '#2b2b2b'
        fg_color = '#e0e0e0'
        entry_bg = '#3c3c3c'
        accent_color = '#3498db'
        success_color = '#27ae60'
        
        # Create main frame for the panel
        self.frame = tk.Frame(parent, bd=0, relief=tk.FLAT, bg=bg_color)
        
        # Output file selection
        output_row = tk.Frame(self.frame, bg=bg_color)
        output_row.pack(fill='x', pady=8, padx=15)
        
        tk.Label(output_row, text="💾 Output File:", bg=bg_color, fg=fg_color,
                font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=8)
        self.output_path = tk.StringVar()
        output_entry = tk.Entry(output_row, textvariable=self.output_path, width=50,
                               bg=entry_bg, fg=fg_color, bd=0, relief=tk.FLAT,
                               insertbackground=fg_color, font=('Segoe UI', 9))
        output_entry.pack(side=tk.LEFT, padx=5, ipady=5)
        
        browse_btn = tk.Button(output_row, text="📁", command=self.browse_output,
                              bg=accent_color, fg='white', bd=0, relief=tk.FLAT,
                              font=('Arial', 12), cursor='hand2', width=3,
                              highlightthickness=0,
                              activebackground='#2980b9', activeforeground='white')
        browse_btn.pack(side=tk.LEFT, padx=8)
        # Add hover effect - darken background, keep text color
        browse_btn.bind('<Enter>', lambda e: browse_btn.config(bg='#2980b9'))
        browse_btn.bind('<Leave>', lambda e: browse_btn.config(bg=accent_color))

        # Start muxing button with border frame
        button_row = tk.Frame(self.frame, bg=bg_color)
        button_row.pack(fill='x', pady=5, padx=15)
        
        # Border frame for the button
        button_border = tk.Frame(button_row, bg=success_color, bd=0)
        button_border.pack(pady=3)
        
        self.start_button = tk.Button(button_border, text="▶ Start Muxing", command=self.start_muxing, 
                                       bg=bg_color, fg=success_color, bd=2, relief=tk.FLAT,
                                       font=('Segoe UI', 12, 'bold'), cursor='hand2',
                                       highlightthickness=0, padx=30, pady=8,
                                       activebackground='#1e1e1e', activeforeground=success_color)
        self.start_button.pack(padx=2, pady=2)
        # Add hover effect - darken background, keep text color
        self.start_button.bind('<Enter>', lambda e: self.start_button.config(bg='#1e1e1e'))
        self.start_button.bind('<Leave>', lambda e: self.start_button.config(bg=bg_color))

        # Progress bar and labels
        progress_frame = tk.Frame(self.frame, bg=bg_color)
        progress_frame.pack(fill='x', pady=8, padx=15)
        
        # Status row with inline percentage
        status_row = tk.Frame(progress_frame, bg=bg_color)
        status_row.pack(fill='x', pady=(0, 5))
        
        # Progress label (status message)
        self.progress_label = tk.Label(status_row, text="Ready", bg=bg_color, fg=fg_color,
                                       font=('Segoe UI', 10))
        self.progress_label.pack(side=tk.LEFT)
        
        # Percentage label (shown inline with status, hidden by default)
        self.percentage_label = tk.Label(status_row, text="", bg=bg_color, fg=accent_color,
                                        font=('Segoe UI', 10, 'bold'))
        self.percentage_label.pack(side=tk.LEFT, padx=10)
        
        # Style the progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.Horizontal.TProgressbar',
                       troughcolor='#3c3c3c',
                       background=accent_color,
                       bordercolor=bg_color,
                       lightcolor=accent_color,
                       darkcolor=accent_color)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400, maximum=100,
                                           style='Custom.Horizontal.TProgressbar')
        self.progress_bar.pack(fill='x', pady=(0, 5))
    
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
        # Show percentage inline if value > 0 (active muxing)
        if value > 0:
            self.root.after(0, lambda: self.percentage_label.config(text=f"({value}%)"))
        else:
            self.root.after(0, lambda: self.percentage_label.config(text=""))
