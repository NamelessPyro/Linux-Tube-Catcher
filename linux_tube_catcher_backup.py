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
import re
import urllib.parse
from pathlib import Path
from typing import List, Optional

def bootstrap_local_venv():
    """Prefer the repository or installed app virtualenv when running directly."""
    base_dir = Path(__file__).resolve().parent
    for venv_dir in (base_dir / ".venv", base_dir / "venv"):
        if not venv_dir.exists():
            continue

        for site_packages in sorted(venv_dir.glob("lib/python*/site-packages")):
            site_path = str(site_packages)
            if site_path not in sys.path:
                sys.path.insert(0, site_path)
            return


bootstrap_local_venv()

import yt_dlp

APP_VERSION = "1.6"
MIN_YTDLP_VERSION = (2025, 3, 31)
PS3_PSVITA_PRESET = "PS3 / PS Vita 720p"
PS3_PSVITA_480_PRESET = "PS3 / PS Vita 480p (light)"
MPEG4_SIMPLE_PROFILE_PRESET = "MPEG-4 Simple Profile 720p"
XBOX_360_PRESET = "Xbox 360 720p"
STANDARD_PRESET = "Standard"
DEVICE_PRESETS = {PS3_PSVITA_PRESET, PS3_PSVITA_480_PRESET, MPEG4_SIMPLE_PROFILE_PRESET, XBOX_360_PRESET}

BG_COLOR = "#000000"
PANEL_COLOR = "#050000"
ACCENT_COLOR = "#ff3333"
ACCENT_SOFT = "#dd0000"
BORDER_COLOR = "#660000"
TEXT_DIM = "#770000"


def get_ytdlp_version() -> str:
    """Return the installed yt-dlp version string."""
    return getattr(getattr(yt_dlp, "version", None), "__version__", "0.0.0")


def is_ytdlp_outdated() -> bool:
    """Return True when the installed yt-dlp is older than the known-good minimum."""
    try:
        version_parts = tuple(int(part) for part in get_ytdlp_version().split(".")[:3])
    except (TypeError, ValueError):
        return False
    return version_parts < MIN_YTDLP_VERSION


def is_valid_media_url(url: str) -> bool:
    """Return True when the URL looks like a supported HTTP(S) media URL."""
    if not url:
        return False

    parsed = urllib.parse.urlparse(url.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def parse_max_downloads(value: str) -> Optional[int]:
    """Parse a positive max-download count. Returns None for invalid values."""
    try:
        count = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    return count if count > 0 else None


def format_duration(seconds) -> str:
    """Format a duration in seconds as HH:MM:SS or MM:SS."""
    if seconds in (None, "", "N/A"):
        return "N/A"

    try:
        total_seconds = int(float(seconds))
    except (TypeError, ValueError):
        return str(seconds)

    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def build_ps3_ps_vita_video_args() -> List[str]:
    """Return ffmpeg arguments for a PS3 / PS Vita compatible 720p encode."""
    return [
        '-vf', 'scale=-2:720',
        '-c:v', 'libx264',
        '-profile:v', 'main',
        '-level', '4.1',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        '-c:a', 'aac',
        '-b:a', '192k',
    ]


def build_ps3_ps_vita_480_video_args() -> List[str]:
    """Return ffmpeg arguments for a lighter PS3 / PS Vita compatible 480p encode."""
    return [
        '-vf', 'scale=-2:480',
        '-c:v', 'libx264',
        '-profile:v', 'baseline',
        '-level', '3.1',
        '-pix_fmt', 'yuv420p',
        '-preset', 'medium',
        '-crf', '24',
        '-movflags', '+faststart',
        '-c:a', 'aac',
        '-b:a', '128k',
    ]


def build_mpeg4_simple_profile_video_args() -> List[str]:
    """Return ffmpeg arguments for a PS3 / PS Vita compatible MPEG-4 Simple Profile encode."""
    return [
        '-vf', 'scale=-2:720',
        '-c:v', 'mpeg4',
        '-q:v', '4',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        '-c:a', 'aac',
        '-b:a', '192k',
    ]


def build_xbox_360_video_args() -> List[str]:
    """Return ffmpeg arguments for an Xbox 360 compatible 720p encode."""
    return [
        '-vf', 'scale=-2:720',
        '-c:v', 'libx264',
        '-profile:v', 'main',
        '-level', '4.0',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        '-c:a', 'aac',
        '-b:a', '192k',
    ]


def build_video_transcode_args(preset: str, quality: str, output_ext: str) -> List[str]:
    """Return ffmpeg arguments for a selected video preset or standard conversion."""
    if preset == PS3_PSVITA_PRESET:
        return build_ps3_ps_vita_video_args()
    if preset == PS3_PSVITA_480_PRESET:
        return build_ps3_ps_vita_480_video_args()
    if preset == MPEG4_SIMPLE_PROFILE_PRESET:
        return build_mpeg4_simple_profile_video_args()
    if preset == XBOX_360_PRESET:
        return build_xbox_360_video_args()

    args: List[str] = []
    if quality != "best":
        args.extend(['-vf', f'scale=-2:{quality.replace("p", "")}'])

    if output_ext == 'webm':
        args.extend(['-c:v', 'libvpx-vp9', '-crf', '32', '-b:v', '0', '-c:a', 'libopus'])
        return args

    args.extend(['-c:v', 'libx264', '-crf', '23', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k'])
    if output_ext in {'mp4', 'mov'}:
        args.extend(['-movflags', '+faststart'])
    return args


def get_device_preset_target_quality(preset: str) -> str:
    """Return the target output resolution for a device preset."""
    if preset == PS3_PSVITA_480_PRESET:
        return "480p"
    return "720p"


def build_ffmpeg_command(input_path: str, output_path: str, ffmpeg_args: List[str]) -> List[str]:
    """Build a complete ffmpeg command for a conversion job."""
    return ['ffmpeg', '-y', '-i', input_path, *ffmpeg_args, output_path]


def parse_progress_percent(value: str) -> Optional[float]:
    """Extract a numeric percent value from a progress string."""
    if not value:
        return None

    match = re.search(r"(\d+(?:\.\d+)?)\s*%", str(value))
    if match:
        return float(match.group(1))

    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def get_media_duration_seconds(path: str) -> Optional[float]:
    """Return the duration of a media file in seconds, if ffprobe can read it."""
    try:
        result = subprocess.run(
            [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

    try:
        return float(result.stdout.strip())
    except (TypeError, ValueError):
        return None

class LinuxTubeCatcher:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Linux Tube Catcher v{APP_VERSION} - by NamelessPyro")
        self.root.geometry("1100x800")
        self.root.minsize(1050, 750)
        self.root.configure(bg=BG_COLOR)

        # Variables
        self.download_path = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.video_url = tk.StringVar()
        self.video_format = tk.StringVar(value="mp4")
        self.audio_format = tk.StringVar(value="mp3")
        self.quality = tk.StringVar(value="720p")
        self.video_preset = tk.StringVar(value=STANDARD_PRESET)
        self.download_type = tk.StringVar(value="video")
        self.playlist_mode = tk.BooleanVar(value=False)
        self.max_downloads = tk.StringVar(value="50")
        self.high_quality_source = tk.BooleanVar(value=True)
        self.local_video_path = tk.StringVar()
        self.local_output_path = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.cookies_file = tk.StringVar()
        self._progress_total = None

        self.configure_styles()
        self.setup_ui()
        self.check_dependencies()

    def configure_styles(self):
        """Apply the website-inspired terminal theme to the UI."""
        self.ui_font = "Courier"
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".",
                        background=BG_COLOR,
                        foreground=ACCENT_COLOR,
                        fieldbackground=BG_COLOR,
                        bordercolor=BORDER_COLOR,
                        lightcolor=BORDER_COLOR,
                        darkcolor=BORDER_COLOR,
                        font=(self.ui_font, 10))
        style.configure("Terminal.TFrame", background=BG_COLOR)
        style.configure("Terminal.TLabel", background=BG_COLOR, foreground=ACCENT_COLOR, font=(self.ui_font, 10))
        style.configure("TerminalTitle.TLabel", background=BG_COLOR, foreground=ACCENT_COLOR, font=(self.ui_font, 16, "bold"))
        style.configure("Muted.TLabel", background=BG_COLOR, foreground=TEXT_DIM, font=(self.ui_font, 9))
        style.configure("Terminal.TLabelframe",
                        background=BG_COLOR,
                        foreground=ACCENT_SOFT,
                        bordercolor=BORDER_COLOR,
                        relief="solid")
        style.configure("Terminal.TLabelframe.Label",
                        background=BG_COLOR,
                        foreground=ACCENT_SOFT,
                        font=(self.ui_font, 10, "bold"))
        style.configure("Accent.TButton",
                        background=BG_COLOR,
                        foreground=ACCENT_COLOR,
                        bordercolor=ACCENT_COLOR,
                        lightcolor=ACCENT_COLOR,
                        darkcolor=ACCENT_COLOR,
                        relief="solid",
                        padding=(10, 6))
        style.map("Accent.TButton",
                  background=[("active", ACCENT_COLOR), ("pressed", ACCENT_SOFT)],
                  foreground=[("active", BG_COLOR), ("pressed", BG_COLOR)])
        style.configure("Terminal.TEntry",
                        fieldbackground=BG_COLOR,
                        foreground=ACCENT_COLOR,
                        bordercolor=BORDER_COLOR,
                        lightcolor=BORDER_COLOR,
                        darkcolor=BORDER_COLOR)
        style.configure("Terminal.TCombobox",
                        fieldbackground=BG_COLOR,
                        foreground=ACCENT_COLOR,
                        background=BG_COLOR,
                        arrowcolor=ACCENT_COLOR,
                        bordercolor=BORDER_COLOR,
                        lightcolor=BORDER_COLOR,
                        darkcolor=BORDER_COLOR)
        style.configure("Terminal.TRadiobutton", background=BG_COLOR, foreground=ACCENT_COLOR)
        style.configure("Terminal.TCheckbutton", background=BG_COLOR, foreground=ACCENT_COLOR)
        style.configure("Terminal.Horizontal.TProgressbar",
                        troughcolor=PANEL_COLOR,
                        background=ACCENT_COLOR,
                        bordercolor=BORDER_COLOR,
                        lightcolor=ACCENT_COLOR,
                        darkcolor=ACCENT_SOFT)

        self.root.option_add("*TCombobox*Listbox*Background", BG_COLOR)
        self.root.option_add("*TCombobox*Listbox*Foreground", ACCENT_COLOR)
        self.root.option_add("*TCombobox*Listbox*selectBackground", BORDER_COLOR)
        self.root.option_add("*TCombobox*Listbox*selectForeground", ACCENT_COLOR)

    def setup_ui(self):
        """Setup the user interface with the website's terminal style."""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        terminal_frame = tk.Frame(self.root, bg=ACCENT_COLOR, padx=2, pady=2)
        terminal_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=18, pady=18)
        terminal_frame.columnconfigure(0, weight=1)
        terminal_frame.rowconfigure(1, weight=1)

        terminal_header = tk.Label(
            terminal_frame,
            text="~/Desktop/LinuxTubeCatcher>",
            bg=ACCENT_COLOR,
            fg=BG_COLOR,
            anchor="w",
            padx=8,
            pady=4,
            font=(self.ui_font, 10, "bold")
        )
        terminal_header.grid(row=0, column=0, sticky="ew")

        main_frame = ttk.Frame(terminal_frame, padding="12", style="Terminal.TFrame")
        main_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(10, weight=1)

        title_label = ttk.Label(main_frame, text="[ Linux Tube Catcher ]", style="TerminalTitle.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 2))

        credit_label = ttk.Label(
            main_frame,
            text=f"Created by NamelessPyro // terminal build v{APP_VERSION}",
            style="Muted.TLabel"
        )
        credit_label.grid(row=0, column=2, sticky=tk.E, pady=(2, 6))

        ttk.Label(main_frame, text="Video/Playlist URL:", style="Terminal.TLabel").grid(row=1, column=0, sticky=tk.W, pady=6)
        url_entry = ttk.Entry(main_frame, textvariable=self.video_url, width=60, style="Terminal.TEntry")
        url_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=6)

        ttk.Label(main_frame, text="Download Path:", style="Terminal.TLabel").grid(row=2, column=0, sticky=tk.W, pady=6)
        path_entry = ttk.Entry(main_frame, textvariable=self.download_path, width=50, style="Terminal.TEntry")
        path_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=6)

        browse_btn = ttk.Button(main_frame, text="Browse", command=self.browse_download_path, style="Accent.TButton")
        browse_btn.grid(row=2, column=2, padx=(6, 0), pady=6)

        type_frame = ttk.LabelFrame(main_frame, text="DOWNLOAD TYPE", padding="8", style="Terminal.TLabelframe")
        type_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        ttk.Radiobutton(type_frame, text="Video", variable=self.download_type, value="video", style="Terminal.TRadiobutton").grid(row=0, column=0, padx=10)
        ttk.Radiobutton(type_frame, text="Audio Only", variable=self.download_type, value="audio", style="Terminal.TRadiobutton").grid(row=0, column=1, padx=10)
        ttk.Radiobutton(type_frame, text="Video Info", variable=self.download_type, value="info", style="Terminal.TRadiobutton").grid(row=0, column=2, padx=10)

        playlist_frame = ttk.LabelFrame(main_frame, text="PLAYLIST OPTIONS", padding="8", style="Terminal.TLabelframe")
        playlist_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        playlist_check = ttk.Checkbutton(
            playlist_frame,
            text="Download entire playlist",
            variable=self.playlist_mode,
            style="Terminal.TCheckbutton"
        )
        playlist_check.grid(row=0, column=0, padx=10, sticky=tk.W)

        ttk.Label(playlist_frame, text="Max downloads:", style="Terminal.TLabel").grid(row=0, column=1, padx=10, sticky=tk.W)
        max_downloads_entry = ttk.Entry(playlist_frame, textvariable=self.max_downloads, width=10, style="Terminal.TEntry")
        max_downloads_entry.grid(row=0, column=2, padx=5)

        options_frame = ttk.LabelFrame(main_frame, text="VIDEO OPTIONS", padding="8", style="Terminal.TLabelframe")
        options_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(3, weight=1)

        ttk.Label(options_frame, text="Quality:", style="Terminal.TLabel").grid(row=0, column=0, sticky=tk.W, padx=5)
        quality_combo = ttk.Combobox(
            options_frame,
            textvariable=self.quality,
            values=["144p", "240p", "360p", "480p", "720p", "1080p", "best"],
            width=10,
            state="readonly",
            style="Terminal.TCombobox"
        )
        quality_combo.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))

        ttk.Label(options_frame, text="Video Format:", style="Terminal.TLabel").grid(row=0, column=2, sticky=tk.W, padx=5)
        video_format_combo = ttk.Combobox(
            options_frame,
            textvariable=self.video_format,
            values=["mp4", "avi", "mkv", "webm", "mov"],
            width=10,
            state="readonly",
            style="Terminal.TCombobox"
        )
        video_format_combo.grid(row=0, column=3, padx=5, sticky=(tk.W, tk.E))

        ttk.Label(options_frame, text="Audio Format:", style="Terminal.TLabel").grid(row=1, column=0, sticky=tk.W, padx=5)
        audio_format_combo = ttk.Combobox(
            options_frame,
            textvariable=self.audio_format,
            values=["mp3", "wav", "aac", "ogg", "m4a"],
            width=10,
            state="readonly",
            style="Terminal.TCombobox"
        )
        audio_format_combo.grid(row=1, column=1, padx=5, sticky=(tk.W, tk.E))

        ttk.Label(options_frame, text="Device Preset:", style="Terminal.TLabel").grid(row=2, column=0, sticky=tk.W, padx=5)
        preset_combo = ttk.Combobox(
            options_frame,
            textvariable=self.video_preset,
            values=[
                STANDARD_PRESET,
                PS3_PSVITA_PRESET,
                PS3_PSVITA_480_PRESET,
                MPEG4_SIMPLE_PROFILE_PRESET,
                XBOX_360_PRESET,
            ],
            width=45,
            state="readonly",
            style="Terminal.TCombobox"
        )
        preset_combo.grid(row=2, column=1, columnspan=3, padx=5, sticky=(tk.W, tk.E))

        high_quality_check = ttk.Checkbutton(
            options_frame,
            text="Download highest quality first (better scaling)",
            variable=self.high_quality_source,
            style="Terminal.TCheckbutton"
        )
        high_quality_check.grid(row=3, column=0, columnspan=4, padx=5, sticky=tk.W, pady=5)

        auth_frame = ttk.LabelFrame(main_frame, text="AUTHENTICATION (Optional)", padding="8", style="Terminal.TLabelframe")
        auth_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(auth_frame, text="Cookies File:", style="Terminal.TLabel").grid(row=0, column=0, sticky=tk.W, padx=5)
        cookies_entry = ttk.Entry(auth_frame, textvariable=self.cookies_file, width=60, style="Terminal.TEntry")
        cookies_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=6, padx=5)

        cookies_browse_btn = ttk.Button(auth_frame, text="Browse", command=self.browse_cookies_file, style="Accent.TButton")
        cookies_browse_btn.grid(row=0, column=2, padx=(6, 0), pady=6)

        cookies_help = ttk.Label(
            auth_frame,
            text="Use browser cookies to access private/age-restricted videos. Export with 'Get cookies.txt' extension.",
            style="Muted.TLabel"
        )
        cookies_help.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5)

        local_frame = ttk.LabelFrame(main_frame, text="ON-DEVICE CONVERSION", padding="8", style="Terminal.TLabelframe")
        local_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        local_frame.columnconfigure(1, weight=1)

        ttk.Label(local_frame, text="Local Video File:", style="Terminal.TLabel").grid(row=0, column=0, sticky=tk.W, pady=6, padx=5)
        local_video_entry = ttk.Entry(local_frame, textvariable=self.local_video_path, width=60, style="Terminal.TEntry")
        local_video_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=6)

        local_browse_btn = ttk.Button(local_frame, text="Browse File", command=self.browse_local_video_file, style="Accent.TButton")
        local_browse_btn.grid(row=0, column=2, padx=(6, 0), pady=6)

        ttk.Label(local_frame, text="Output Folder:", style="Terminal.TLabel").grid(row=1, column=0, sticky=tk.W, pady=6, padx=5)
        local_output_entry = ttk.Entry(local_frame, textvariable=self.local_output_path, width=60, style="Terminal.TEntry")
        local_output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=6)

        local_output_btn = ttk.Button(local_frame, text="Browse Folder", command=self.browse_local_output_path, style="Accent.TButton")
        local_output_btn.grid(row=1, column=2, padx=(6, 0), pady=6)

        self.convert_btn = ttk.Button(local_frame, text="Convert Local Video", command=self.start_local_conversion, style="Accent.TButton")
        self.convert_btn.grid(row=2, column=1, pady=(10, 0), sticky=tk.W)

        button_frame = ttk.Frame(main_frame, style="Terminal.TFrame")
        button_frame.grid(row=8, column=0, columnspan=3, pady=18)

        self.download_btn = ttk.Button(button_frame, text="Download", command=self.start_download, style="Accent.TButton")
        self.download_btn.grid(row=0, column=0, padx=5)

        self.info_btn = ttk.Button(button_frame, text="Get Info", command=self.get_video_info, style="Accent.TButton")
        self.info_btn.grid(row=0, column=1, padx=5)

        self.clear_btn = ttk.Button(button_frame, text="Clear Log", command=self.clear_log, style="Accent.TButton")
        self.clear_btn.grid(row=0, column=2, padx=5)

        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', style="Terminal.Horizontal.TProgressbar")
        self.progress.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        log_frame = ttk.LabelFrame(main_frame, text="TERMINAL LOG", padding="6", style="Terminal.TLabelframe")
        log_frame.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            width=80,
            bg=BG_COLOR,
            fg=ACCENT_COLOR,
            insertbackground=ACCENT_COLOR,
            selectbackground=BORDER_COLOR,
            selectforeground=ACCENT_COLOR,
            relief="flat",
            borderwidth=0,
            font=(self.ui_font, 10)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def run_on_ui_thread(self, callback, *args, **kwargs):
        """Execute a callback safely on the Tkinter main thread."""
        self.root.after(0, lambda: callback(*args, **kwargs))

    def set_progress_active(self, active):
        """Start or stop the progress animation safely."""
        def update():
            self.progress.configure(mode='indeterminate')
            if active:
                self.progress.start(10)
            else:
                self.progress.stop()
                self.progress['value'] = 0

        self.run_on_ui_thread(update)

    def set_progress_percent(self, percent):
        """Set the progress bar to a determinate percentage."""
        def update():
            self.progress.stop()
            self.progress.configure(mode='determinate')
            self.progress['value'] = max(0, min(100, percent))

        self.run_on_ui_thread(update)

    def set_download_state(self, busy):
        """Enable or disable the download button safely."""
        state = 'disabled' if busy else 'normal'
        self.run_on_ui_thread(self.download_btn.config, state=state)
        if hasattr(self, "convert_btn"):
            self.run_on_ui_thread(self.convert_btn.config, state=state)

    def log(self, message):
        """Add message to log safely from any thread."""
        def append():
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()

        if threading.current_thread() is threading.main_thread():
            append()
        else:
            self.run_on_ui_thread(append)

    def show_error(self, title, message):
        """Show an error dialog safely from any thread."""
        self.run_on_ui_thread(messagebox.showerror, title, message)

    def show_info(self, title, message):
        """Show an info dialog safely from any thread."""
        self.run_on_ui_thread(messagebox.showinfo, title, message)
        
    def clear_log(self):
        """Clear the log area"""
        self.log_text.delete(1.0, tk.END)
        
    def browse_download_path(self):
        """Browse for download directory"""
        folder = filedialog.askdirectory(initialdir=self.download_path.get())
        if folder:
            self.download_path.set(folder)

    def browse_local_video_file(self):
        """Browse for a local video file to convert."""
        file_path = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=[
                ("Video files", "*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.mpeg *.mpg"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            self.local_video_path.set(file_path)

    def browse_local_output_path(self):
        """Browse for a local output directory."""
        folder = filedialog.askdirectory(initialdir=self.local_output_path.get())
        if folder:
            self.local_output_path.set(folder)

    def browse_cookies_file(self):
        """Browse for a cookies file."""
        file_path = filedialog.askopenfilename(
            title="Select a cookies.txt file",
            filetypes=[
                ("Netscape cookies", "*.txt"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            self.cookies_file.set(file_path)

    def _update_progress_from_text(self, percent_text):
        percent = parse_progress_percent(percent_text)
        if percent is not None:
            self.set_progress_percent(percent)
            
    def check_dependencies(self):
        """Check if required dependencies are available"""
        self.log("Linux Tube Catcher - Created by NamelessPyro")
        self.log("Checking dependencies...")
        
        # Check yt-dlp
        try:
            version = get_ytdlp_version()
            self.log(f"✓ yt-dlp is available ({version})")
            if is_ytdlp_outdated():
                self.log("⚠️ yt-dlp is outdated. Recent YouTube downloads may fail with HTTP 403 errors.")
                self.log("   Update it with: python3 -m pip install --upgrade yt-dlp")
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
        """Get video or playlist information."""
        url = self.video_url.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL")
            return

        if not is_valid_media_url(url):
            messagebox.showerror("Error", "Please enter a valid http(s) video or playlist URL")
            return

        def info_thread():
            try:
                self.set_progress_active(True)
                self.log(f"Getting info for: {url}")

                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': 'in_playlist',
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                if info.get('_type') == 'playlist' or 'entries' in info:
                    entries = [entry for entry in info.get('entries', []) if entry]
                    self.log("🎵 PLAYLIST DETECTED!")
                    self.log(f"Playlist Title: {info.get('title', 'N/A')}")
                    self.log(f"Uploader: {info.get('uploader', 'N/A')}")
                    self.log(f"Total Videos: {len(entries)}")

                    self.log("\nFirst 10 videos in playlist:")
                    for i, entry in enumerate(entries[:10], start=1):
                        title = entry.get('title', 'N/A')
                        duration = format_duration(entry.get('duration'))
                        self.log(f"  {i}. {title} ({duration})")

                    if len(entries) > 10:
                        self.log(f"  ... and {len(entries) - 10} more videos")

                    self.log("\n💡 Tip: Check 'Download entire playlist' to download all videos!")
                else:
                    self.log("📹 SINGLE VIDEO")
                    self.log(f"Title: {info.get('title', 'N/A')}")
                    self.log(f"Duration: {format_duration(info.get('duration'))}")
                    self.log(f"Uploader: {info.get('uploader', 'N/A')}")
                    self.log(f"View Count: {info.get('view_count', 'N/A')}")
                    self.log(f"Upload Date: {info.get('upload_date', 'N/A')}")

                    formats = info.get('formats') or []
                    if formats:
                        self.log("\nAvailable formats:")
                        for fmt in formats[-10:]:
                            ext = fmt.get('ext', 'unknown')
                            height = fmt.get('height', 'audio only')
                            self.log(f"  {fmt.get('format_id')}: {ext} - {height}")

                self.log("\nInfo retrieval complete.\n")

            except Exception as e:
                self.log(f"Error getting video info: {str(e)}")
            finally:
                self.set_progress_active(False)

        threading.Thread(target=info_thread, daemon=True).start()
        
    def start_download(self):
        """Start the download process."""
        url = self.video_url.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL")
            return

        if not is_valid_media_url(url):
            messagebox.showerror("Error", "Please enter a valid http(s) video or playlist URL")
            return

        if self.download_type.get() == "info":
            self.log("ℹ️ Info mode selected - fetching details instead of downloading.")
            self.get_video_info()
            return

        download_dir = os.path.expanduser(self.download_path.get().strip())
        self.download_path.set(download_dir)
        if not download_dir:
            messagebox.showerror("Error", "Please choose a download directory")
            return

        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create download directory: {str(e)}")
                return

        def download_thread():
            quality = self.quality.get()
            video_ext = self.video_format.get()
            audio_ext = self.audio_format.get()
            use_high_quality_source = self.high_quality_source.get()
            download_mode = self.download_type.get()
            video_preset = self.video_preset.get()

            try:
                self.set_progress_active(True)
                self.set_download_state(True)

                self.log(f"Starting download: {url}")
                self.log(f"Download path: {download_dir}")

                ydl_opts = {
                    'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                    'ignoreerrors': True,
                    'quiet': True,
                    'no_warnings': True,
                    'retries': 10,
                    'fragment_retries': 10,
                    'extractor_retries': 3,
                }

                cookies_file = self.cookies_file.get().strip()
                if cookies_file and os.path.isfile(cookies_file):
                    ydl_opts['cookiefile'] = cookies_file
                    self.log(f"🍪 Using cookies from: {os.path.basename(cookies_file)}")
                elif cookies_file:
                    self.log(f"⚠️ Cookies file not found: {cookies_file}")

                if self.playlist_mode.get():
                    max_downloads = parse_max_downloads(self.max_downloads.get())
                    if max_downloads is not None:
                        ydl_opts['playlistend'] = max_downloads
                        self.log(f"🎵 Playlist mode enabled - Max downloads: {max_downloads}")
                    else:
                        self.log("🎵 Playlist mode enabled - downloading all available videos")

                    ydl_opts['outtmpl'] = os.path.join(
                        download_dir,
                        '%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s'
                    )
                else:
                    ydl_opts['noplaylist'] = True
                    self.log("📹 Single video mode - ignoring playlist if present")

                if download_mode == "audio":
                    ydl_opts.update({
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': audio_ext,
                            'preferredquality': '192',
                        }],
                    })
                    self.log(f"Downloading audio in {audio_ext} format...")

                elif download_mode == "video":
                    if video_preset in DEVICE_PRESETS:
                        quality = get_device_preset_target_quality(video_preset)
                        video_ext = "mp4"
                        ydl_opts['format'] = 'bestvideo+bestaudio/best'
                        ydl_opts['merge_output_format'] = 'mp4'
                        ydl_opts['postprocessor_args'] = {'ffmpeg': build_video_transcode_args(video_preset, quality, video_ext)}
                        self.log(f"🎮 {video_preset} enabled - converting to {quality} device-compatible MP4")
                    elif use_high_quality_source and quality != "best":
                        self.log(f"🎬 High-quality mode: Downloading best quality first, then scaling to {quality}")
                        height = quality.replace('p', '')
                        ydl_opts['format'] = 'bestvideo+bestaudio/best'
                        if video_ext in {'mp4', 'mkv', 'webm'}:
                            ydl_opts['merge_output_format'] = video_ext
                        ydl_opts['postprocessor_args'] = {
                            'ffmpeg': [
                                '-vf', f'scale=-2:{height}',
                                '-c:v', 'libx264',
                                '-crf', '23',
                                '-preset', 'medium',
                                '-c:a', 'copy'
                            ]
                        }
                        if video_ext != 'mp4':
                            ydl_opts['postprocessors'] = [{
                                'key': 'FFmpegVideoConvertor',
                                'preferedformat': video_ext,
                            }]
                    else:
                        self.log(f"📹 Standard mode: Downloading {quality} quality directly")
                        if quality == "best":
                            format_selector = 'bestvideo+bestaudio/best'
                        else:
                            height = quality.replace('p', '')
                            format_selector = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
                        ydl_opts['format'] = format_selector
                        if video_ext in {'mp4', 'mkv', 'webm'}:
                            ydl_opts['merge_output_format'] = video_ext
                        elif video_ext != 'mp4':
                            ydl_opts['postprocessors'] = [{
                                'key': 'FFmpegVideoConvertor',
                                'preferedformat': video_ext,
                            }]

                    if use_high_quality_source and quality != "best":
                        self.log(f"Downloading video: best quality → scale to {quality}, {video_ext} format...")
                    elif video_preset in DEVICE_PRESETS:
                        self.log(f"Downloading video in {video_preset} format...")
                    else:
                        self.log(f"Downloading video in {quality} quality, {video_ext} format...")

                def progress_hook(d):
                    status = d.get('status')
                    if status == 'downloading':
                        percent = d.get('_percent_str', 'N/A')
                        speed = d.get('_speed_str', 'N/A')
                        filename = os.path.basename(d.get('filename', 'Unknown'))
                        percent_text = percent.strip() if isinstance(percent, str) else percent
                        speed_text = speed.strip() if isinstance(speed, str) else speed
                        self._update_progress_from_text(percent_text)
                        self.log(f"📥 {filename}: {percent_text} at {speed_text}")
                    elif status == 'finished':
                        filename = os.path.basename(d.get('filename', 'Unknown'))
                        self.set_progress_percent(100)
                        self.log(f"✅ Downloaded: {filename}")
                        if download_mode == "video" and use_high_quality_source and quality != "best":
                            self.log(f"🔄 Post-processing: Scaling video to {quality}...")
                    elif status == 'error':
                        self.log(f"❌ Error downloading: {d.get('filename', 'Unknown')}")

                ydl_opts['progress_hooks'] = [progress_hook]

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                self.log("Download completed successfully!\n")
                self.show_info("Success", "Download completed!")

            except Exception as e:
                error_text = str(e)
                error_msg = f"Download error: {error_text}"
                self.log(error_msg)

                if any(token in error_text for token in ["HTTP Error 403", "Precondition check failed", "Sign in to confirm"]):
                    self.log("⚠️ This usually means `yt-dlp` needs to be updated for the latest YouTube changes.")
                    self.log("   Run: python3 -m pip install --upgrade yt-dlp")
                    error_msg += "\n\nTip: update yt-dlp with `python3 -m pip install --upgrade yt-dlp` and try again."

                self.show_error("Error", error_msg)
            finally:
                self.set_progress_active(False)
                self.set_download_state(False)

        threading.Thread(target=download_thread, daemon=True).start()

    def start_local_conversion(self):
        """Convert a video file from the local device."""
        source_path = self.local_video_path.get().strip()
        output_dir = os.path.expanduser(self.local_output_path.get().strip())
        preset = self.video_preset.get()
        quality = self.quality.get()
        output_ext = self.video_format.get()

        if not source_path:
            messagebox.showerror("Error", "Please select a local video file")
            return

        if not os.path.isfile(source_path):
            messagebox.showerror("Error", "The selected local video file does not exist")
            return

        if not output_dir:
            messagebox.showerror("Error", "Please choose an output directory")
            return

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create output directory: {str(e)}")
                return

        if preset in DEVICE_PRESETS:
            quality = get_device_preset_target_quality(preset)
            output_ext = "mp4"

        source_stem = Path(source_path).stem
        output_path = os.path.join(output_dir, f"{source_stem}_converted.{output_ext}")
        duration_seconds = get_media_duration_seconds(source_path)

        def convert_thread():
            try:
                self.set_progress_active(True)
                self.set_download_state(True)
                self.log(f"Starting local conversion: {source_path}")
                self.log(f"Output path: {output_path}")
                if duration_seconds is not None:
                    self.log(f"Input duration: {format_duration(duration_seconds)}")
                    self.set_progress_percent(0)
                else:
                    self.log("Input duration unavailable; showing indeterminate progress.")

                ffmpeg_args = build_video_transcode_args(preset, quality, output_ext)
                command = build_ffmpeg_command(
                    source_path,
                    output_path,
                    [*ffmpeg_args, '-progress', 'pipe:1', '-nostats', '-loglevel', 'error'],
                )
                self.log(f"Running ffmpeg with preset: {preset}")
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                while True:
                    line = process.stdout.readline()
                    if not line:
                        if process.poll() is not None:
                            break
                        continue

                    line = line.strip()
                    if line.startswith('out_time_ms=') and duration_seconds:
                        try:
                            out_time_ms = int(line.split('=', 1)[1])
                            percent = (out_time_ms / 1000000.0) / duration_seconds * 100
                            self.set_progress_percent(percent)
                        except ValueError:
                            pass
                    elif line.startswith('out_time=') and duration_seconds:
                        try:
                            out_time = line.split('=', 1)[1]
                            parts = out_time.split(':')
                            if len(parts) == 3:
                                hours = float(parts[0])
                                minutes = float(parts[1])
                                seconds = float(parts[2])
                                total_seconds = hours * 3600 + minutes * 60 + seconds
                                percent = total_seconds / duration_seconds * 100
                                self.set_progress_percent(percent)
                        except ValueError:
                            pass
                    elif line == 'progress=end':
                        self.set_progress_percent(100)

                stderr_output = process.stderr.read().strip()
                return_code = process.wait()
                if return_code != 0:
                    raise subprocess.CalledProcessError(return_code, command, output=None, stderr=stderr_output)

                self.log("Local conversion completed successfully!\n")
                self.show_info("Success", "Local conversion completed!")
            except subprocess.CalledProcessError as e:
                error_details = e.stderr.strip() if e.stderr else str(e)
                self.log(f"Local conversion error: {error_details}")
                self.show_error("Error", f"Local conversion failed:\n{error_details}")
            finally:
                self.set_progress_active(False)
                self.set_download_state(False)

        threading.Thread(target=convert_thread, daemon=True).start()

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
