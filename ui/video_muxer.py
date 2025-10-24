import subprocess
import os
import tempfile

class VideoMuxer:
    """Handles video cutting, concatenation, and compression"""
    
    def __init__(self, progress_callback=None):
        """
        Initialize the VideoMuxer
        
        Args:
            progress_callback: Function to call with (value, text) for progress updates
        """
        self.progress_callback = progress_callback
    
    def update_progress(self, value, text):
        """Update progress if callback is provided"""
        if self.progress_callback:
            self.progress_callback(value, text)
    
    def process_videos(self, editors, output_path):
        """
        Process videos: split, concatenate, and compress
        
        Args:
            editors: List of FileSegmentEditor objects
            output_path: Path for the output file
            
        Returns:
            True if successful, raises Exception on error
        """
        temp_dir = tempfile.mkdtemp()
        segment_files = []
        concat_file = None
        
        try:
            # Count total segments for progress calculation
            total_segments = 0
            for editor in editors:
                if editor.file_path.get() and os.path.exists(editor.file_path.get()):
                    total_segments += len(editor.segments)
            
            if total_segments == 0:
                raise Exception("No valid segments to process")
            
            # Step 1: Split videos using mkvmerge (0-100% of cutting phase)
            self.update_progress(0, "Starting video cutting...")
            current_segment = 0
            
            for editor_idx, editor in enumerate(editors):
                input_file = editor.file_path.get()
                if not input_file or not os.path.exists(input_file):
                    continue
                
                for seg_idx, segment in enumerate(editor.segments):
                    start_time = segment.start_var.get()
                    end_time = segment.end_var.get()
                    
                    if not start_time or not end_time:
                        continue
                    
                    # Convert time format to seconds for mkvmerge
                    start_seconds = self.time_to_seconds(start_time)
                    end_seconds = self.time_to_seconds(end_time)
                    
                    output_segment = os.path.join(temp_dir, f"segment_{editor_idx}_{seg_idx}.mkv")
                    
                    # Update progress for this segment
                    progress = int((current_segment / total_segments) * 100)
                    self.update_progress(progress, f"Cutting segment {current_segment + 1}/{total_segments}...")
                    
                    # Use mkvmerge to split with timestamp format
                    # Format: --split parts:START-END where times are in format HH:MM:SS.nnnnnnnnn or seconds
                    cmd = [
                        'mkvmerge',
                        '-o', output_segment,
                        '--split', f'parts:{start_seconds}s-{end_seconds}s',
                        input_file
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0 or result.returncode == 1:  # mkvmerge returns 1 for warnings
                        segment_files.append(output_segment)
                        current_segment += 1
                    else:
                        raise Exception(f"mkvmerge error (cmd: {' '.join(cmd)}): {result.stderr}")
            
            if not segment_files:
                raise Exception("No segments were created")
            
            # Cutting complete
            self.update_progress(100, f"Cutting complete! Created {len(segment_files)} segments")
            
            # Calculate total duration from segments
            total_duration_seconds = 0
            for editor in editors:
                if editor.file_path.get() and os.path.exists(editor.file_path.get()):
                    for segment in editor.segments:
                        start_time = segment.start_var.get()
                        end_time = segment.end_var.get()
                        if start_time and end_time:
                            start_seconds = self.time_to_seconds(start_time)
                            end_seconds = self.time_to_seconds(end_time)
                            segment_duration = end_seconds - start_seconds
                            total_duration_seconds += segment_duration
            
            print(f"Calculated total duration: {total_duration_seconds}s")
            
            # Step 2: Create concat file for ffmpeg
            concat_file = os.path.join(temp_dir, 'concat.txt')
            with open(concat_file, 'w') as f:
                for seg_file in segment_files:
                    f.write(f"file '{seg_file}'\n")
            
            # Step 3: Concatenate and compress using ffmpeg (0-100% of compression phase)
            self.update_progress(0, f"Starting compression (total: {int(total_duration_seconds)}s)...")
            
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c:v', 'libx265',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'libvorbis',
                '-q:a', '5',
                '-y',
                output_path
            ]
            
            # Start ffmpeg process
            process = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, 
                                      text=True, bufsize=1)
            
            # Use calculated duration instead of waiting for ffmpeg
            duration_seconds = total_duration_seconds if total_duration_seconds > 0 else None
            last_progress = 0
            
            # Read stdout line by line (stderr is redirected to stdout)
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                
                line = line.strip()
                print(f"FFMPEG: {line}")  # Print to console for debugging
                
                # Track progress using time= format
                if 'time=' in line and duration_seconds:
                    try:
                        # Find time= in the line
                        time_idx = line.find('time=')
                        if time_idx >= 0:
                            # Extract time string (format: time=00:00:10.50)
                            time_part = line[time_idx+5:]
                            time_str = time_part.split()[0]
                            
                            # Parse time
                            time_parts = time_str.split(':')
                            if len(time_parts) == 3:
                                h = int(time_parts[0])
                                m = int(time_parts[1])
                                s = float(time_parts[2])
                                current_seconds = h * 3600 + m * 60 + s
                                
                                if duration_seconds > 0:
                                    progress = min(int((current_seconds / duration_seconds) * 100), 99)
                                    if progress > last_progress:
                                        self.update_progress(progress, f"Compressing video...")
                                        last_progress = progress
                                        print(f"Progress: {progress}% ({current_seconds:.1f}/{duration_seconds}s)")
                    except Exception as e:
                        print(f"Error parsing time: {e} from line: {line}")
            
            process.stdout.close()
            process.wait()
            
            if process.returncode != 0:
                raise Exception(f"ffmpeg error: return code {process.returncode}")
            
            self.update_progress(100, "Complete!")
            return True
            
        finally:
            # Cleanup temp files
            self._cleanup(segment_files, concat_file, temp_dir)
    
    def _cleanup(self, segment_files, concat_file, temp_dir):
        """Clean up temporary files and directory"""
        try:
            for seg_file in segment_files:
                if os.path.exists(seg_file):
                    os.remove(seg_file)
            if concat_file and os.path.exists(concat_file):
                os.remove(concat_file)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except Exception as e:
            # Silent cleanup failure - not critical
            pass
    
    @staticmethod
    def time_to_seconds(time_str):
        """
        Convert time string (hh:mm:ss or mm:ss) to seconds
        
        Args:
            time_str: Time string in format hh:mm:ss or mm:ss
            
        Returns:
            Time in seconds
        """
        parts = time_str.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
        elif len(parts) == 2:
            hours = 0
            minutes, seconds = map(int, parts)
        else:
            return 0
        
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
    
    @staticmethod
    def time_to_milliseconds(time_str):
        """
        Convert time string (hh:mm:ss or mm:ss) to milliseconds
        
        Args:
            time_str: Time string in format hh:mm:ss or mm:ss
            
        Returns:
            Time in milliseconds
        """
        return VideoMuxer.time_to_seconds(time_str) * 1000
