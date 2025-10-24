import subprocess
import os
import tempfile
from PIL import Image, ImageTk
import tkinter as tk

class ThumbnailExtractor:
    """Extract video frame thumbnails using ffmpeg"""
    
    @staticmethod
    def time_to_seconds(time_str):
        """Convert time string (hh:mm:ss or mm:ss) to seconds"""
        if not time_str:
            return 0
        
        parts = time_str.split(':')
        if len(parts) == 2:  # mm:ss
            minutes, seconds = parts
            return int(minutes) * 60 + int(seconds)
        elif len(parts) == 3:  # hh:mm:ss
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        return 0
    
    @staticmethod
    def extract_thumbnail(video_path, timestamp_str, width=120, height=68):
        """
        Extract a frame from a video at the specified timestamp
        
        Args:
            video_path: Path to the video file
            timestamp_str: Time string in format hh:mm:ss or mm:ss
            width: Thumbnail width in pixels
            height: Thumbnail height in pixels
            
        Returns:
            ImageTk.PhotoImage object or None if extraction fails
        """
        if not video_path or not os.path.exists(video_path):
            return None
        
        if not timestamp_str or timestamp_str.strip() == "":
            return None
        
        try:
            # Convert time to seconds
            seconds = ThumbnailExtractor.time_to_seconds(timestamp_str)
            
            # Validate that we have a valid time
            if seconds < 0:
                return None
            
            # Create temporary file for the thumbnail
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            # Use ffmpeg to extract frame at timestamp
            # -ss: seek to position, -i: input file, -frames:v 1: extract 1 frame
            # -s: scale to size, -q:v 2: quality (2 is high)
            cmd = [
                'ffmpeg',
                '-ss', str(seconds),
                '-i', video_path,
                '-frames:v', '1',
                '-s', f'{width}x{height}',
                '-q:v', '2',
                '-y',  # Overwrite output file
                tmp_path
            ]
            
            # Run ffmpeg, suppress output
            result = subprocess.run(cmd, 
                                   capture_output=True, 
                                   text=True,
                                   timeout=5)
            
            # Check if file was created and has content
            if result.returncode == 0 and os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                try:
                    # Load the image and convert to PhotoImage
                    img = Image.open(tmp_path)
                    photo = ImageTk.PhotoImage(img)
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
                    
                    return photo
                except Exception as img_error:
                    # Image file was created but is invalid/corrupted
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    # Only print error if it's not a common case (empty/invalid image)
                    print(f"Warning: Could not load thumbnail image: {img_error}")
                    return None
            else:
                # ffmpeg failed or file wasn't created properly
                # Clean up temp file if it exists
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                # Don't print error - this is normal when timestamp is invalid or out of range
                return None
                
        except subprocess.TimeoutExpired:
            # ffmpeg took too long
            return None
        except Exception as e:
            # Only print unexpected errors
            import traceback
            print(f"Unexpected error extracting thumbnail: {e}")
            traceback.print_exc()
            return None
    
    @staticmethod
    def create_placeholder(width=120, height=68, text="No Preview"):
        """
        Create a placeholder image when thumbnail can't be extracted
        
        Args:
            width: Image width
            height: Image height
            text: Text to display on placeholder
            
        Returns:
            ImageTk.PhotoImage object
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a dark gray placeholder image
            img = Image.new('RGB', (width, height), color='#3c3c3c')
            draw = ImageDraw.Draw(img)
            
            # Try to add text
            try:
                # Use default font
                font = ImageFont.load_default()
                
                # Calculate text position (center)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (width - text_width) // 2
                y = (height - text_height) // 2
                
                draw.text((x, y), text, fill='#888888', font=font)
            except:
                pass  # If text drawing fails, just show gray box
            
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error creating placeholder: {e}")
            return None
