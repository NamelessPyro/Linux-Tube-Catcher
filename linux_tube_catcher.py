#!/usr/bin/env python3
"""
Linux Tube Catcher - A Linux port of aTube Catcher
Video downloader and converter for Linux Mint 22.1 Cinnamon
Created by NamelessPyro
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import subprocess
import json
import urllib.parse
import requests
from pathlib import Path
import yt_dlp
import ffmpeg
import tempfile
import shutil

class LinuxTubeCatcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux Tube Catcher v1.0 - by NamelessPyro")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
        self.download_path = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.video_url = tk.StringVar()
        self.video_format = tk.StringVar(value="mp4")
        self.audio_format = tk.StringVar(value="mp3")
        self.quality = tk.StringVar(value="720p")
        self.download_type = tk.StringVar(value="video")
        self.playlist_mode = tk.BooleanVar(value=False)
        self.max_downloads = tk.StringVar(value="50")
        self.high_quality_source = tk.BooleanVar(value=True)
        
        self.setup_ui()
        self.check_dependencies()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Linux Tube Catcher", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Credit
        credit_label = ttk.Label(main_frame, text="Created by NamelessPyro", 
                                font=("Arial", 9, "italic"))
        credit_label.grid(row=0, column=2, sticky=tk.E, pady=(20, 0))
        
        # URL input
        ttk.Label(main_frame, text="Video/Playlist URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        url_entry = ttk.Entry(main_frame, textvariable=self.video_url, width=60)
        url_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Download path
        ttk.Label(main_frame, text="Download Path:").grid(row=2, column=0, sticky=tk.W, pady=5)
        path_entry = ttk.Entry(main_frame, textvariable=self.download_path, width=50)
        path_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        browse_btn = ttk.Button(main_frame, text="Browse", 
                               command=self.browse_download_path)
        browse_btn.grid(row=2, column=2, padx=(5, 0), pady=5)
        
        # Download type
        type_frame = ttk.LabelFrame(main_frame, text="Download Type", padding="5")
        type_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Radiobutton(type_frame, text="Video", variable=self.download_type, 
                       value="video").grid(row=0, column=0, padx=10)
        ttk.Radiobutton(type_frame, text="Audio Only", variable=self.download_type, 
                       value="audio").grid(row=0, column=1, padx=10)
        ttk.Radiobutton(type_frame, text="Video Info", variable=self.download_type, 
                       value="info").grid(row=0, column=2, padx=10)
        
        # Playlist options
        playlist_frame = ttk.LabelFrame(main_frame, text="Playlist Options", padding="5")
        playlist_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        playlist_check = ttk.Checkbutton(playlist_frame, text="Download entire playlist", 
                                       variable=self.playlist_mode)
        playlist_check.grid(row=0, column=0, padx=10, sticky=tk.W)
        
        ttk.Label(playlist_frame, text="Max downloads:").grid(row=0, column=1, padx=10, sticky=tk.W)
        max_downloads_entry = ttk.Entry(playlist_frame, textvariable=self.max_downloads, width=10)
        max_downloads_entry.grid(row=0, column=2, padx=5)
        
        # Quality and format options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        options_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Quality
        ttk.Label(options_frame, text="Quality:").grid(row=0, column=0, sticky=tk.W, padx=5)
        quality_combo = ttk.Combobox(options_frame, textvariable=self.quality,
                                   values=["144p", "240p", "360p", "480p", "720p", "1080p", "best"],
                                   width=10)
        quality_combo.grid(row=0, column=1, padx=5)
        
        # Video format
        ttk.Label(options_frame, text="Video Format:").grid(row=0, column=2, sticky=tk.W, padx=5)
        video_format_combo = ttk.Combobox(options_frame, textvariable=self.video_format,
                                        values=["mp4", "avi", "mkv", "webm", "mov"],
                                        width=10)
        video_format_combo.grid(row=0, column=3, padx=5)
        
        # Audio format
        ttk.Label(options_frame, text="Audio Format:").grid(row=1, column=0, sticky=tk.W, padx=5)
        audio_format_combo = ttk.Combobox(options_frame, textvariable=self.audio_format,
                                        values=["mp3", "wav", "aac", "ogg", "m4a"],
                                        width=10)
        audio_format_combo.grid(row=1, column=1, padx=5)
        
        # High quality source option
        high_quality_check = ttk.Checkbutton(options_frame, 
                                           text="Download highest quality first (better scaling)", 
                                           variable=self.high_quality_source)
        high_quality_check.grid(row=1, column=2, columnspan=2, padx=5, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        self.download_btn = ttk.Button(button_frame, text="Download", 
                                      command=self.start_download)
        self.download_btn.grid(row=0, column=0, padx=5)
        
        self.info_btn = ttk.Button(button_frame, text="Get Info", 
                                  command=self.get_video_info)
        self.info_btn.grid(row=0, column=1, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Clear Log", 
                                   command=self.clear_log)
        self.clear_btn.grid(row=0, column=2, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame row weights
        main_frame.rowconfigure(8, weight=1)
        
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """Clear the log area"""
        self.log_text.delete(1.0, tk.END)
        
    def browse_download_path(self):
        """Browse for download directory"""
        folder = filedialog.askdirectory(initialdir=self.download_path.get())
        if folder:
            self.download_path.set(folder)
            
    def check_dependencies(self):
        """Check if required dependencies are available"""
        self.log("Linux Tube Catcher - Created by NamelessPyro")
        self.log("Checking dependencies...")
        
        # Check yt-dlp
        try:
            import yt_dlp
            self.log("✓ yt-dlp is available")
        except ImportError:
            self.log("✗ yt-dlp not found. Please install: pip install yt-dlp")
            
        # Check ffmpeg
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            self.log("✓ ffmpeg is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("✗ ffmpeg not found. Please install: sudo apt install ffmpeg")
            
        self.log("Dependencies check complete.\n")
        
    def get_video_info(self):
        """Get video information"""
        url = self.video_url.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL")
            return
            
        def info_thread():
            try:
                self.progress.start()
                self.log(f"Getting info for: {url}")
                
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,  # For playlist detection
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    # Check if it's a playlist
                    if 'entries' in info:
                        self.log(f"🎵 PLAYLIST DETECTED!")
                        self.log(f"Playlist Title: {info.get('title', 'N/A')}")
                        self.log(f"Uploader: {info.get('uploader', 'N/A')}")
                        self.log(f"Total Videos: {len(info['entries'])}")
                        
                        self.log("\nFirst 10 videos in playlist:")
                        for i, entry in enumerate(info['entries'][:10]):
                            if entry:
                                title = entry.get('title', 'N/A')
                                duration = entry.get('duration', 'N/A')
                                self.log(f"  {i+1}. {title} ({duration}s)")
                        
                        if len(info['entries']) > 10:
                            self.log(f"  ... and {len(info['entries']) - 10} more videos")
                            
                        self.log("\n💡 Tip: Check 'Download entire playlist' to download all videos!")
                        
                    else:
                        # Single video
                        self.log(f"📹 SINGLE VIDEO")
                        self.log(f"Title: {info.get('title', 'N/A')}")
                        self.log(f"Duration: {info.get('duration', 'N/A')} seconds")
                        self.log(f"Uploader: {info.get('uploader', 'N/A')}")
                        self.log(f"View Count: {info.get('view_count', 'N/A')}")
                        self.log(f"Upload Date: {info.get('upload_date', 'N/A')}")
                        
                        # Get detailed info for single video
                        detailed_info = ydl.extract_info(url, download=False)
                        
                        # Available formats
                        if 'formats' in detailed_info:
                            self.log("\nAvailable formats:")
                            for fmt in detailed_info['formats'][-10:]:  # Show last 10 formats
                                ext = fmt.get('ext', 'unknown')
                                height = fmt.get('height', 'audio only')
                                self.log(f"  {fmt.get('format_id')}: {ext} - {height}")
                    
                    self.log("\nInfo retrieval complete.\n")
                    
            except Exception as e:
                self.log(f"Error getting video info: {str(e)}")
            finally:
                self.progress.stop()
                
        threading.Thread(target=info_thread, daemon=True).start()
        
    def start_download(self):
        """Start the download process"""
        url = self.video_url.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL")
            return
            
        download_dir = self.download_path.get()
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create download directory: {str(e)}")
                return
                
        def download_thread():
            try:
                self.progress.start()
                self.download_btn.config(state='disabled')
                
                self.log(f"Starting download: {url}")
                self.log(f"Download path: {download_dir}")
                
                # Configure yt-dlp options
                ydl_opts = {
                    'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                    'ignoreerrors': True,
                }
                
                # Playlist handling
                if self.playlist_mode.get():
                    try:
                        max_downloads = int(self.max_downloads.get())
                        if max_downloads > 0:
                            ydl_opts['playlistend'] = max_downloads
                        self.log(f"🎵 Playlist mode enabled - Max downloads: {max_downloads}")
                    except ValueError:
                        self.log("⚠️ Invalid max downloads value, downloading all")
                    
                    # Better playlist naming
                    ydl_opts['outtmpl'] = os.path.join(download_dir, '%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s')
                else:
                    # Single video mode
                    ydl_opts['noplaylist'] = True
                    self.log("📹 Single video mode - ignoring playlist if present")
                
                if self.download_type.get() == "audio":
                    # Audio only
                    audio_ext = self.audio_format.get()
                    ydl_opts.update({
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': audio_ext,
                            'preferredquality': '192',
                        }],
                    })
                    self.log(f"Downloading audio in {audio_ext} format...")
                    
                elif self.download_type.get() == "video":
                    # Video download
                    quality = self.quality.get()
                    video_ext = self.video_format.get()
                    use_high_quality_source = self.high_quality_source.get()
                    
                    if use_high_quality_source and quality != "best":
                        # Download highest quality first, then scale down
                        self.log(f"🎬 High-quality mode: Downloading best quality first, then scaling to {quality}")
                        
                        # Download best quality available (prefer high resolution)
                        ydl_opts['format'] = 'best[height>=720]/best'
                        
                        # Add FFmpeg post-processor for scaling
                        height = quality.replace('p', '')
                        
                        postprocessors = [{
                            'key': 'FFmpegVideoConvertor',
                            'preferedformat': video_ext,
                            'preferedcodec': 'libx264',
                            'preferedquality': '23',  # CRF value for good quality
                        }]
                        
                        # Add custom FFmpeg arguments for scaling
                        ydl_opts['postprocessor_args'] = {
                            'ffmpeg': [
                                '-vf', f'scale=-2:{height}',  # Scale to target height, maintain aspect ratio
                                '-c:v', 'libx264',
                                '-crf', '23',
                                '-preset', 'medium',
                                '-c:a', 'copy'  # Copy audio without re-encoding
                            ]
                        }
                        
                        ydl_opts['postprocessors'] = postprocessors
                        
                    else:
                        # Standard quality selection (original behavior)
                        self.log(f"📹 Standard mode: Downloading {quality} quality directly")
                        
                        if quality == "best":
                            format_selector = f"best[ext={video_ext}]/best"
                        else:
                            height = quality.replace('p', '')
                            format_selector = f"best[height<={height}][ext={video_ext}]/best[height<={height}]/best"
                        
                        ydl_opts['format'] = format_selector
                        
                        if video_ext != 'mp4':
                            ydl_opts['postprocessors'] = [{
                                'key': 'FFmpegVideoConvertor',
                                'preferedformat': video_ext,
                            }]
                    
                    if use_high_quality_source and quality != "best":
                        self.log(f"Downloading video: best quality → scale to {quality}, {video_ext} format...")
                    else:
                        self.log(f"Downloading video in {quality} quality, {video_ext} format...")
                
                # Progress hook
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        percent = d.get('_percent_str', 'N/A')
                        speed = d.get('_speed_str', 'N/A')
                        filename = os.path.basename(d.get('filename', 'Unknown'))
                        self.log(f"📥 {filename}: {percent} at {speed}")
                    elif d['status'] == 'finished':
                        filename = os.path.basename(d['filename'])
                        self.log(f"✅ Downloaded: {filename}")
                        if use_high_quality_source and quality != "best":
                            self.log(f"🔄 Post-processing: Scaling video to {quality}...")
                    elif d['status'] == 'error':
                        self.log(f"❌ Error downloading: {d.get('filename', 'Unknown')}")
                
                ydl_opts['progress_hooks'] = [progress_hook]
                
                # Download
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                self.log("Download completed successfully!\n")
                messagebox.showinfo("Success", "Download completed!")
                
            except Exception as e:
                error_msg = f"Download error: {str(e)}"
                self.log(error_msg)
                messagebox.showerror("Error", error_msg)
            finally:
                self.progress.stop()
                self.download_btn.config(state='normal')
                
        threading.Thread(target=download_thread, daemon=True).start()

def main():
    """Main function"""
    # Check Python version
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        sys.exit(1)
    
    # Create and run the application
    root = tk.Tk()
    app = LinuxTubeCatcher(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
