#!/usr/bin/env python3
"""
Willhiem - Media Downloader and Transcoder
Modern VLC Redesign Edition
Created by NamelessPyro
"""

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

try:
    from PyQt6.QtWidgets import (
        QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QTextEdit,
        QProgressBar, QFileDialog, QMessageBox, QScrollArea, QFrame,
        QGroupBox, QRadioButton, QButtonGroup, QSpinBox, QStackedWidget,
        QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QSizePolicy
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QUrl
    from PyQt6.QtGui import QFont, QColor, QTextCursor, QIcon, QPixmap, QPainter, QDesktopServices
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    print("Error: PyQt6 is not installed. Please install it with: pip install PyQt6")
    sys.exit(1)

import yt_dlp
import vlc_theme

APP_VERSION = "1.7"
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


class DownloadWorker(QThread):
    """Worker thread for YouTube downloads."""
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str, str)
    
    def __init__(self, url: str, download_dir: str, video_format: str, audio_format: str,
                 quality: str, video_preset: str, download_type: str, playlist_mode: bool,
                 max_downloads: str, high_quality_source: bool, cookies_file: str):
        super().__init__()
        self.url = url
        self.download_dir = download_dir
        self.video_format = video_format
        self.audio_format = audio_format
        self.quality = quality
        self.video_preset = video_preset
        self.download_type = download_type
        self.playlist_mode = playlist_mode
        self.max_downloads = max_downloads
        self.high_quality_source = high_quality_source
        self.cookies_file = cookies_file

    def run(self):
        """Execute the download in a separate thread."""
        try:
            self.progress.emit(-1)
            self.log_message.emit(f"Starting download: {self.url}")
            self.log_message.emit(f"Download path: {self.download_dir}")

            ydl_opts = {
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'ignoreerrors': True,
                'quiet': True,
                'no_warnings': True,
                'retries': 10,
                'fragment_retries': 10,
                'extractor_retries': 3,
            }

            cookies_file = self.cookies_file.strip()
            if cookies_file and os.path.isfile(cookies_file):
                ydl_opts['cookiefile'] = cookies_file
                self.log_message.emit(f"🍪 Using cookies from: {os.path.basename(cookies_file)}")
            elif cookies_file:
                self.log_message.emit(f"⚠️ Cookies file not found: {cookies_file}")

            if self.playlist_mode:
                max_downloads = parse_max_downloads(self.max_downloads)
                if max_downloads is not None:
                    ydl_opts['playlistend'] = max_downloads
                    self.log_message.emit(f"🎵 Playlist mode enabled - Max downloads: {max_downloads}")
                else:
                    self.log_message.emit("🎵 Playlist mode enabled - downloading all available videos")

                ydl_opts['outtmpl'] = os.path.join(
                    self.download_dir,
                    '%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s'
                )
            else:
                ydl_opts['noplaylist'] = True
                self.log_message.emit("📹 Single video mode - ignoring playlist if present")

            if self.download_type == "audio":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': self.audio_format,
                        'preferredquality': '192',
                    }],
                })
                self.log_message.emit(f"Downloading audio in {self.audio_format} format...")

            elif self.download_type == "video":
                if self.video_preset in DEVICE_PRESETS:
                    quality = get_device_preset_target_quality(self.video_preset)
                    video_ext = "mp4"
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
                    ydl_opts['merge_output_format'] = 'mp4'
                    ydl_opts['postprocessor_args'] = {'ffmpeg': build_video_transcode_args(self.video_preset, quality, video_ext)}
                    self.log_message.emit(f"🎮 {self.video_preset} enabled - converting to {quality} device-compatible MP4")
                elif self.high_quality_source and self.quality != "best":
                    self.log_message.emit(f"🎬 High-quality mode: Downloading best quality first, then scaling to {self.quality}")
                    height = self.quality.replace('p', '')
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
                    if self.video_format in {'mp4', 'mkv', 'webm'}:
                        ydl_opts['merge_output_format'] = self.video_format
                    ydl_opts['postprocessor_args'] = {
                        'ffmpeg': [
                            '-vf', f'scale=-2:{height}',
                            '-c:v', 'libx264',
                            '-crf', '23',
                            '-preset', 'medium',
                            '-c:a', 'copy'
                        ]
                    }
                    if self.video_format != 'mp4':
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegVideoConvertor',
                            'preferedformat': self.video_format,
                        }]
                else:
                    self.log_message.emit(f"📹 Standard mode: Downloading {self.quality} quality directly")
                    if self.quality == "best":
                        format_selector = 'bestvideo+bestaudio/best'
                    else:
                        height = self.quality.replace('p', '')
                        format_selector = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
                    ydl_opts['format'] = format_selector
                    if self.video_format in {'mp4', 'mkv', 'webm'}:
                        ydl_opts['merge_output_format'] = self.video_format
                    elif self.video_format != 'mp4':
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegVideoConvertor',
                            'preferedformat': self.video_format,
                        }]

                if self.high_quality_source and self.quality != "best":
                    self.log_message.emit(f"Downloading video: best quality → scale to {self.quality}, {self.video_format} format...")
                elif self.video_preset in DEVICE_PRESETS:
                    self.log_message.emit(f"Downloading video in {self.video_preset} format...")
                else:
                    self.log_message.emit(f"Downloading video in {self.quality} quality, {self.video_format} format...")

            def progress_hook(d):
                status = d.get('status')
                if status == 'downloading':
                    percent = d.get('_percent_str', 'N/A')
                    speed = d.get('_speed_str', 'N/A')
                    filename = os.path.basename(d.get('filename', 'Unknown'))
                    percent_text = percent.strip() if isinstance(percent, str) else percent
                    speed_text = speed.strip() if isinstance(speed, str) else speed
                    percent_num = parse_progress_percent(percent_text)
                    if percent_num is not None:
                        self.progress.emit(int(percent_num))
                    self.log_message.emit(f"📥 {filename}: {percent_text} at {speed_text}")
                elif status == 'finished':
                    filename = os.path.basename(d.get('filename', 'Unknown'))
                    self.progress.emit(100)
                    self.log_message.emit(f"✅ Downloaded: {filename}")
                    if self.download_type == "video" and self.high_quality_source and self.quality != "best":
                        self.log_message.emit(f"🔄 Post-processing: Scaling video to {self.quality}...")
                elif status == 'error':
                    self.log_message.emit(f"❌ Error downloading: {d.get('filename', 'Unknown')}")

            ydl_opts['progress_hooks'] = [progress_hook]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            self.log_message.emit("Download completed successfully!\n")
            self.finished.emit()

        except Exception as e:
            error_text = str(e)
            error_msg = f"Download error: {error_text}"
            self.log_message.emit(error_msg)

            if any(token in error_text for token in ["HTTP Error 403", "Precondition check failed", "Sign in to confirm"]):
                self.log_message.emit("⚠️ This usually means `yt-dlp` needs to be updated for the latest YouTube changes.")
                self.log_message.emit("   Run: python3 -m pip install --upgrade yt-dlp")
                error_msg += "\n\nTip: update yt-dlp with `python3 -m pip install --upgrade yt-dlp` and try again."

            self.error.emit("Download Error", error_msg)
        finally:
            self.progress.emit(-1)


class ConversionWorker(QThread):
    """Worker thread for local video conversions."""
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str, str)

    def __init__(self, source_paths: List[str], output_dir: str, video_preset: str,
                 quality: str, video_format: str):
        super().__init__()
        self.source_paths = source_paths
        self.output_dir = output_dir
        self.video_preset = video_preset
        self.quality = quality
        self.video_format = video_format

    def _convert_single_file(self, source_path: str):
        """Convert one local file using the selected preset."""
        if self.video_preset in DEVICE_PRESETS:
            quality = get_device_preset_target_quality(self.video_preset)
            output_ext = "mp4"
        else:
            quality = self.quality
            output_ext = self.video_format

        source_stem = Path(source_path).stem
        output_path = os.path.join(self.output_dir, f"{source_stem}_converted.{output_ext}")
        duration_seconds = get_media_duration_seconds(source_path)

        self.log_message.emit(f"Starting local conversion: {source_path}")
        self.log_message.emit(f"Output path: {output_path}")
        if duration_seconds is not None:
            self.log_message.emit(f"Input duration: {format_duration(duration_seconds)}")
            self.progress.emit(0)
        else:
            self.log_message.emit("Input duration unavailable; showing indeterminate progress.")

        ffmpeg_args = build_video_transcode_args(self.video_preset, quality, output_ext)
        command = build_ffmpeg_command(
            source_path,
            output_path,
            [*ffmpeg_args, '-progress', 'pipe:1', '-nostats', '-loglevel', 'error'],
        )
        self.log_message.emit(f"Running ffmpeg with preset: {self.video_preset}")
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
                    self.progress.emit(min(99, int(percent)))
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
                        self.progress.emit(min(99, int(percent)))
                except ValueError:
                    pass
            elif line == 'progress=end':
                self.progress.emit(100)

        stderr_output = process.stderr.read().strip()
        return_code = process.wait()
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, command, output=None, stderr=stderr_output)

        self.log_message.emit("Local conversion completed successfully!\n")

    def run(self):
        """Execute all selected conversions in sequence."""
        try:
            self.progress.emit(-1)
            if len(self.source_paths) > 1:
                self.log_message.emit(f"Starting batch conversion for {len(self.source_paths)} files")

            for index, source_path in enumerate(self.source_paths, start=1):
                if not os.path.isfile(source_path):
                    raise FileNotFoundError(f"Selected file does not exist: {source_path}")
                if len(self.source_paths) > 1:
                    self.log_message.emit(f"\n[File {index}/{len(self.source_paths)}]")
                self._convert_single_file(source_path)

            self.finished.emit()

        except subprocess.CalledProcessError as e:
            error_details = e.stderr.strip() if e.stderr else str(e)
            self.log_message.emit(f"Local conversion error: {error_details}")
            self.error.emit("Conversion Error", f"Local conversion failed:\n{error_details}")
        except Exception as e:
            error_msg = str(e)
            self.log_message.emit(f"Local conversion error: {error_msg}")
            self.error.emit("Conversion Error", error_msg)
        finally:
            self.progress.emit(-1)


class InfoWorker(QThread):
    """Worker thread for getting video information."""
    log_message = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str, str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        """Fetch video/playlist information in a separate thread."""
        try:
            self.log_message.emit(f"Getting info for: {self.url}")

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)

            if info.get('_type') == 'playlist' or 'entries' in info:
                entries = [entry for entry in info.get('entries', []) if entry]
                self.log_message.emit("🎵 PLAYLIST DETECTED!")
                self.log_message.emit(f"Playlist Title: {info.get('title', 'N/A')}")
                self.log_message.emit(f"Uploader: {info.get('uploader', 'N/A')}")
                self.log_message.emit(f"Total Videos: {len(entries)}")

                self.log_message.emit("\nFirst 10 videos in playlist:")
                for i, entry in enumerate(entries[:10], start=1):
                    title = entry.get('title', 'N/A')
                    duration = format_duration(entry.get('duration'))
                    self.log_message.emit(f"  {i}. {title} ({duration})")

                if len(entries) > 10:
                    self.log_message.emit(f"  ... and {len(entries) - 10} more videos")

                self.log_message.emit("\n💡 Tip: Check 'Download entire playlist' to download all videos!")
            else:
                self.log_message.emit("📹 SINGLE VIDEO")
                self.log_message.emit(f"Title: {info.get('title', 'N/A')}")
                self.log_message.emit(f"Duration: {format_duration(info.get('duration'))}")
                self.log_message.emit(f"Uploader: {info.get('uploader', 'N/A')}")
                self.log_message.emit(f"View Count: {info.get('view_count', 'N/A')}")
                self.log_message.emit(f"Upload Date: {info.get('upload_date', 'N/A')}")

                formats = info.get('formats') or []
                if formats:
                    self.log_message.emit("\nAvailable formats:")
                    for fmt in formats[-10:]:
                        ext = fmt.get('ext', 'unknown')
                        height = fmt.get('height', 'audio only')
                        self.log_message.emit(f"  {fmt.get('format_id')}: {ext} - {height}")

            self.log_message.emit("\nInfo retrieval complete.\n")
            self.finished.emit()

        except Exception as e:
            error_msg = f"Error getting video info: {str(e)}"
            self.log_message.emit(error_msg)
            self.error.emit("Info Error", error_msg)



class Willhiem(QMainWindow):
    """
    Willhiem Main Window.
    Implements the VLC Community Redesign aesthetic with sidebar navigation,
    customizable accent colors, modern cards, and rich media management.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Willhiem - VLC Community Design")
        self.setGeometry(100, 100, 1160, 820)
        self.setMinimumSize(1080, 760)

        # Theme state
        self.current_accent = vlc_theme.DEFAULT_ACCENT
        self.is_dark = True
        self.nav_buttons: List[QPushButton] = []
        self.swatch_buttons: List[QPushButton] = []

        # Thread workers
        self.download_worker: Optional[DownloadWorker] = None
        self.conversion_worker: Optional[ConversionWorker] = None
        self.info_worker: Optional[InfoWorker] = None

        self.setup_ui()
        self.apply_theme(self.current_accent, self.is_dark)
        self.center_window()
        self.check_dependencies()

    def center_window(self):
        """Center window on screen."""
        frame = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())

    def apply_theme(self, accent_color: str, is_dark: bool = True):
        """Apply the VLC Community Redesign stylesheet dynamically."""
        self.current_accent = accent_color
        self.is_dark = is_dark
        global ACCENT_COLOR, ACCENT_SOFT, BG_COLOR, PANEL_COLOR
        ACCENT_COLOR = accent_color
        ACCENT_SOFT = vlc_theme.adjust_color_brightness(accent_color, 0.85)

        qss = vlc_theme.generate_stylesheet(accent_color, is_dark)
        self.setStyleSheet(qss)

        # Update window icon and brand logo using icon.png if present
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.isfile(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
            if hasattr(self, 'brand_logo_label'):
                self.brand_logo_label.setPixmap(QPixmap(icon_path).scaled(34, 34, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            cone_icon = vlc_theme.render_svg_icon('cone', accent_color, 28)
            self.setWindowIcon(cone_icon)
            if hasattr(self, 'brand_logo_label'):
                self.brand_logo_label.setPixmap(vlc_theme.render_svg_pixmap('cone', accent_color, 32))

        # Re-render navigation icons
        nav_icon_specs = [
            ('home', 0),
            ('download', 1),
            ('convert', 2),
            ('library', 3),
            ('log', 4),
            ('settings', 5),
        ]
        active_idx = self.page_stack.currentIndex() if hasattr(self, 'page_stack') else 0
        for icon_name, idx in nav_icon_specs:
            if idx < len(self.nav_buttons):
                btn = self.nav_buttons[idx]
                is_active = (idx == active_idx)
                col = accent_color if is_active else ("#a1a1aa" if is_dark else "#52525b")
                btn.setIcon(vlc_theme.render_svg_icon(icon_name, col, 18))
                btn.setProperty("active", "true" if is_active else "false")
                btn.style().unpolish(btn)
                btn.style().polish(btn)

        # Update swatch indicators
        for btn in self.swatch_buttons:
            color = btn.property("color_hex")
            if color == accent_color:
                btn.setText("✓")
                btn.setStyleSheet(f"background-color: {color}; color: #ffffff; border: 3px solid #ffffff; border-radius: 16px; font-weight: bold; font-size: 13px;")
            else:
                btn.setText("")
                btn.setStyleSheet(f"background-color: {color}; color: transparent; border: 1px solid rgba(255,255,255,0.2); border-radius: 16px;")

        # Update status accent dot
        if hasattr(self, 'accent_dot'):
            self.accent_dot.setStyleSheet(f"background-color: {accent_color}; border-radius: 5px;")

    def apply_stylesheet(self):
        """Compatibility wrapper for apply_stylesheet."""
        self.apply_theme(self.current_accent, self.is_dark)

    def set_accent_color(self, hex_color: str):
        """Set a new accent color from the palette."""
        self.apply_theme(hex_color, self.is_dark)

    def set_theme_mode(self, is_dark: bool):
        """Toggle between Dark and Light mode."""
        self.apply_theme(self.current_accent, is_dark)

    def setup_ui(self):
        """Build the complete VLC Community Redesign user interface."""
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # -------------------------------------------------------------
        # Left Sidebar
        # -------------------------------------------------------------
        sidebar = QWidget()
        sidebar.setObjectName("sidebarWidget")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 20, 16, 16)
        sidebar_layout.setSpacing(6)

        # Brand Header
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(10)
        self.brand_logo_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.isfile(icon_path):
            self.brand_logo_label.setPixmap(QPixmap(icon_path).scaled(34, 34, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.brand_logo_label.setPixmap(vlc_theme.render_svg_pixmap('cone', self.current_accent, 32))
        brand_layout.addWidget(self.brand_logo_label)

        brand_text_layout = QVBoxLayout()
        brand_text_layout.setSpacing(1)
        brand_title = QLabel("Willhiem")
        brand_title_font = QFont()
        brand_title_font.setPointSize(13)
        brand_title_font.setBold(True)
        brand_title.setFont(brand_title_font)

        brand_sub = QLabel("VLC Redesign")
        brand_sub.setStyleSheet("color: #71717a; font-size: 10px; font-weight: 500;")
        brand_text_layout.addWidget(brand_title)
        brand_text_layout.addWidget(brand_sub)
        brand_layout.addLayout(brand_text_layout)
        brand_layout.addStretch()

        sidebar_layout.addLayout(brand_layout)
        sidebar_layout.addSpacing(20)

        # Section Label
        menu_label = QLabel("MENU")
        menu_label.setStyleSheet("color: #71717a; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;")
        sidebar_layout.addWidget(menu_label)
        sidebar_layout.addSpacing(4)

        # Nav Buttons
        nav_items = [
            ("Home", "home", 0),
            ("Downloader", "download", 1),
            ("Converter", "convert", 2),
            ("Library", "library", 3),
            ("Terminal Log", "log", 4),
            ("Settings", "settings", 5),
        ]

        self.nav_buttons = []
        for title, icon_name, page_idx in nav_items:
            btn = QPushButton(f"  {title}")
            btn.setProperty("class", "vlcNavBtn")
            btn.setIcon(vlc_theme.render_svg_icon(icon_name, "#a1a1aa", 18))
            btn.setIconSize(QSize(18, 18))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=page_idx: self.navigate_to(idx))
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Sidebar Footer: System Status
        footer_frame = QFrame()
        footer_frame.setStyleSheet("background-color: #1e1e23; border: 1px solid #28282e; border-radius: 8px; padding: 6px;")
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(8, 8, 8, 8)
        footer_layout.setSpacing(4)

        ytdlp_ver = get_ytdlp_version()
        self.sidebar_ytdlp_status = QLabel(f"yt-dlp: v{ytdlp_ver}")
        self.sidebar_ytdlp_status.setStyleSheet("color: #a1a1aa; font-size: 10px;")
        self.sidebar_ffmpeg_status = QLabel("ffmpeg: active")
        self.sidebar_ffmpeg_status.setStyleSheet("color: #2ea44f; font-size: 10px;")

        footer_layout.addWidget(self.sidebar_ytdlp_status)
        footer_layout.addWidget(self.sidebar_ffmpeg_status)
        sidebar_layout.addWidget(footer_frame)

        root_layout.addWidget(sidebar)

        # -------------------------------------------------------------
        # Right Area (Topbar + Stack + Bottom Bar)
        # -------------------------------------------------------------
        main_content = QWidget()
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        main_content_layout.setSpacing(0)

        # 1. Topbar
        topbar = QFrame()
        topbar.setObjectName("topbarFrame")
        topbar.setFixedHeight(54)
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(20, 0, 20, 0)

        self.breadcrumb_label = QLabel("Home")
        breadcrumb_font = QFont()
        breadcrumb_font.setPointSize(12)
        breadcrumb_font.setBold(True)
        self.breadcrumb_label.setFont(breadcrumb_font)
        topbar_layout.addWidget(self.breadcrumb_label)

        topbar_layout.addStretch()

        self.top_status_badge = QLabel("● Ready")
        self.top_status_badge.setProperty("class", "vlcBadge")
        topbar_layout.addWidget(self.top_status_badge)

        main_content_layout.addWidget(topbar)

        # 2. Main Stack
        self.page_stack = QStackedWidget()
        self.setup_home_page()
        self.setup_downloader_page()
        self.setup_converter_page()
        self.setup_library_page()
        self.setup_log_page()
        self.setup_settings_page()
        main_content_layout.addWidget(self.page_stack, 1)

        # 3. Bottom Player / Status Bar (Persistent)
        bottombar = QFrame()
        bottombar.setObjectName("bottombarFrame")
        bottombar.setFixedHeight(64)
        bottombar_layout = QHBoxLayout(bottombar)
        bottombar_layout.setContentsMargins(20, 10, 20, 10)
        bottombar_layout.setSpacing(16)

        # Left: Status indicator
        status_info_layout = QVBoxLayout()
        status_info_layout.setSpacing(2)
        self.status_title_label = QLabel("Willhiem")
        status_title_font = QFont()
        status_title_font.setPointSize(11)
        status_title_font.setBold(True)
        self.status_title_label.setFont(status_title_font)

        self.status_detail_label = QLabel("Idle - ready for download or conversion")
        status_info_layout.addWidget(self.status_title_label)
        status_info_layout.addWidget(self.status_detail_label)
        bottombar_layout.addLayout(status_info_layout, 0)

        # Center: Scrubber / Progress Bar
        center_progress_layout = QVBoxLayout()
        center_progress_layout.setSpacing(4)

        progress_header_layout = QHBoxLayout()
        self.progress_percent_label = QLabel("0%")
        self.progress_percent_label.setStyleSheet("font-size: 11px; font-weight: 600; color: #a1a1aa;")
        self.progress_speed_label = QLabel("")
        self.progress_speed_label.setStyleSheet("font-size: 11px; color: #71717a;")
        progress_header_layout.addWidget(self.progress_percent_label)
        progress_header_layout.addStretch()
        progress_header_layout.addWidget(self.progress_speed_label)
        center_progress_layout.addLayout(progress_header_layout)

        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        center_progress_layout.addWidget(self.progress)

        bottombar_layout.addLayout(center_progress_layout, 1)

        # Right: Quick action buttons
        quick_btns_layout = QHBoxLayout()
        quick_btns_layout.setSpacing(8)

        open_folder_btn = QPushButton("Downloads")
        open_folder_btn.setProperty("class", "vlcSecondaryBtn")
        open_folder_btn.setIcon(vlc_theme.render_svg_icon('folder', "#a1a1aa", 14))
        open_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_folder_btn.clicked.connect(self.open_download_folder)

        view_log_btn = QPushButton("Log")
        view_log_btn.setProperty("class", "vlcSecondaryBtn")
        view_log_btn.setIcon(vlc_theme.render_svg_icon('log', "#a1a1aa", 14))
        view_log_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_log_btn.clicked.connect(lambda: self.navigate_to(4))

        self.accent_dot = QLabel()
        self.accent_dot.setFixedSize(10, 10)
        self.accent_dot.setStyleSheet(f"background-color: {self.current_accent}; border-radius: 5px;")

        quick_btns_layout.addWidget(open_folder_btn)
        quick_btns_layout.addWidget(view_log_btn)
        quick_btns_layout.addWidget(self.accent_dot)

        bottombar_layout.addLayout(quick_btns_layout, 0)

        main_content_layout.addWidget(bottombar)
        root_layout.addWidget(main_content, 1)

        # Start on Home page
        self.navigate_to(0)

    def navigate_to(self, page_index: int):
        """Navigate to a page index in the stacked widget."""
        self.page_stack.setCurrentIndex(page_index)

        breadcrumbs = [
            "Home",
            "Downloader › Online Media Stream",
            "Converter › Local Video Transcoding",
            "Library › Media Files",
            "Terminal Log › Console Stream",
            "Settings › Appearance & Preferences",
        ]
        if 0 <= page_index < len(breadcrumbs):
            self.breadcrumb_label.setText(breadcrumbs[page_index])

        # Update sidebar button active state
        for idx, btn in enumerate(self.nav_buttons):
            is_active = (idx == page_index)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Refresh library if navigating to library
        if page_index == 3:
            self.refresh_library()

    # -------------------------------------------------------------
    # Page 0: Home Page
    # -------------------------------------------------------------
    def setup_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        # Hero Banner Card
        hero_card = QFrame()
        hero_card.setProperty("class", "vlcCard")
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(24, 24, 24, 24)
        hero_layout.setSpacing(8)

        hero_title = QLabel("Welcome to Willhiem")
        hero_title_font = QFont()
        hero_title_font.setPointSize(16)
        hero_title_font.setBold(True)
        hero_title.setFont(hero_title_font)

        hero_desc = QLabel(
            "High-performance media downloader and hardware-accelerated device transcoder.\n"
            "Inspired by the VLC Community Redesign — sleek, modular, and built for Linux."
        )
        hero_desc.setStyleSheet("color: #a1a1aa; line-height: 1.4; font-size: 13px;")

        hero_layout.addWidget(hero_title)
        hero_layout.addWidget(hero_desc)
        layout.addWidget(hero_card)

        # Quick Download Strip Card
        quick_card = QFrame()
        quick_card.setProperty("class", "vlcCard")
        quick_layout = QVBoxLayout(quick_card)
        quick_layout.setContentsMargins(20, 20, 20, 20)
        quick_layout.setSpacing(12)

        quick_header = QLabel("Quick Online Stream Download")
        quick_header.setStyleSheet("font-weight: 600; font-size: 14px;")
        quick_layout.addWidget(quick_header)

        quick_input_row = QHBoxLayout()
        quick_input_row.setSpacing(10)

        self.quick_url_input = QLineEdit()
        self.quick_url_input.setPlaceholderText("Paste YouTube, Vimeo, Twitch, or video URL...")

        quick_paste_btn = QPushButton("Paste")
        quick_paste_btn.setProperty("class", "vlcSecondaryBtn")
        quick_paste_btn.setIcon(vlc_theme.render_svg_icon('paste', "#a1a1aa", 14))
        quick_paste_btn.clicked.connect(self.paste_quick_url)

        quick_dl_btn = QPushButton("Download Now")
        quick_dl_btn.setProperty("class", "vlcPrimaryBtn")
        quick_dl_btn.setIcon(vlc_theme.render_svg_icon('download', "#ffffff", 14))
        quick_dl_btn.clicked.connect(self.start_quick_download)

        quick_input_row.addWidget(self.quick_url_input, 1)
        quick_input_row.addWidget(quick_paste_btn, 0)
        quick_input_row.addWidget(quick_dl_btn, 0)
        quick_layout.addLayout(quick_input_row)

        layout.addWidget(quick_card)

        # Two-column action cards
        cards_grid = QGridLayout()
        cards_grid.setSpacing(16)

        # Card 1: Online Downloader
        card1 = QFrame()
        card1.setProperty("class", "vlcCard")
        c1_layout = QVBoxLayout(card1)
        c1_layout.setContentsMargins(20, 20, 20, 20)
        c1_layout.setSpacing(10)

        c1_title = QLabel("Online Downloader")
        c1_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        c1_desc = QLabel("Download single videos, full playlists, or extract high-fidelity audio with cookie auth.")
        c1_desc.setStyleSheet("color: #71717a; font-size: 12px;")
        c1_desc.setWordWrap(True)

        c1_btn = QPushButton("Open Downloader")
        c1_btn.setProperty("class", "vlcSecondaryBtn")
        c1_btn.clicked.connect(lambda: self.navigate_to(1))

        c1_layout.addWidget(c1_title)
        c1_layout.addWidget(c1_desc)
        c1_layout.addStretch()
        c1_layout.addWidget(c1_btn)

        # Card 2: Device Converter
        card2 = QFrame()
        card2.setProperty("class", "vlcCard")
        c2_layout = QVBoxLayout(card2)
        c2_layout.setContentsMargins(20, 20, 20, 20)
        c2_layout.setSpacing(10)

        c2_title = QLabel("Device Transcoder")
        c2_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        c2_desc = QLabel("Hardware-optimized presets for PS3, PS Vita, Xbox 360, and MPEG-4 Simple Profile.")
        c2_desc.setStyleSheet("color: #71717a; font-size: 12px;")
        c2_desc.setWordWrap(True)

        c2_btn = QPushButton("Open Converter")
        c2_btn.setProperty("class", "vlcSecondaryBtn")
        c2_btn.clicked.connect(lambda: self.navigate_to(2))

        c2_layout.addWidget(c2_title)
        c2_layout.addWidget(c2_desc)
        c2_layout.addStretch()
        c2_layout.addWidget(c2_btn)

        cards_grid.addWidget(card1, 0, 0)
        cards_grid.addWidget(card2, 0, 1)
        layout.addLayout(cards_grid)

        layout.addStretch()
        self.page_stack.addWidget(page)

    def paste_quick_url(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.quick_url_input.setText(text)

    def start_quick_download(self):
        url = self.quick_url_input.text().strip()
        if not url:
            self.show_error("Error", "Please paste or enter a video URL")
            return
        self.url_input.setText(url)
        self.navigate_to(1)
        self.start_download()

    # -------------------------------------------------------------
    # Page 1: Downloader Page
    # -------------------------------------------------------------
    def setup_downloader_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 20, 28, 28)
        layout.setSpacing(18)

        # Card 1: Media Source
        source_card = QFrame()
        source_card.setProperty("class", "vlcCard")
        s_layout = QVBoxLayout(source_card)
        s_layout.setContentsMargins(20, 20, 20, 20)
        s_layout.setSpacing(14)

        s_title = QLabel("Media Source")
        s_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        s_layout.addWidget(s_title)

        url_row = QHBoxLayout()
        url_row.setSpacing(10)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter video or playlist URL (e.g. https://www.youtube.com/watch?v=...)")

        paste_btn = QPushButton("Paste")
        paste_btn.setProperty("class", "vlcSecondaryBtn")
        paste_btn.setIcon(vlc_theme.render_svg_icon('paste', "#a1a1aa", 14))
        paste_btn.clicked.connect(self.paste_url)

        clear_url_btn = QPushButton("Clear")
        clear_url_btn.setProperty("class", "vlcSecondaryBtn")
        clear_url_btn.setIcon(vlc_theme.render_svg_icon('clear', "#a1a1aa", 14))
        clear_url_btn.clicked.connect(lambda: self.url_input.clear())

        url_row.addWidget(self.url_input, 1)
        url_row.addWidget(paste_btn, 0)
        url_row.addWidget(clear_url_btn, 0)
        s_layout.addLayout(url_row)

        # Download Type Selector
        type_row = QHBoxLayout()
        type_row.setSpacing(14)
        type_label = QLabel("Mode:")
        type_label.setStyleSheet("font-weight: 600; color: #a1a1aa;")
        type_row.addWidget(type_label)

        self.type_group = QButtonGroup()
        self.video_radio = QRadioButton("Video")
        self.video_radio.setChecked(True)
        self.type_group.addButton(self.video_radio, 0)

        self.audio_radio = QRadioButton("Audio Only")
        self.type_group.addButton(self.audio_radio, 1)

        self.info_radio = QRadioButton("Video Info")
        self.type_group.addButton(self.info_radio, 2)

        type_row.addWidget(self.video_radio)
        type_row.addWidget(self.audio_radio)
        type_row.addWidget(self.info_radio)
        type_row.addStretch()
        s_layout.addLayout(type_row)

        layout.addWidget(source_card)

        # Card 2: Quality & Video Options
        quality_card = QFrame()
        quality_card.setProperty("class", "vlcCard")
        q_layout = QVBoxLayout(quality_card)
        q_layout.setContentsMargins(20, 20, 20, 20)
        q_layout.setSpacing(14)

        q_title = QLabel("Quality & Encoding Options")
        q_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        q_layout.addWidget(q_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)

        # Quality
        lbl_q = QLabel("Quality Resolution:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["144p", "240p", "360p", "480p", "720p", "1080p", "best"])
        self.quality_combo.setCurrentText("720p")
        grid.addWidget(lbl_q, 0, 0)
        grid.addWidget(self.quality_combo, 0, 1)

        # Video Format
        lbl_vf = QLabel("Video Container:")
        self.video_format_combo = QComboBox()
        self.video_format_combo.addItems(["mp4", "avi", "mkv", "webm", "mov"])
        self.video_format_combo.setCurrentText("mp4")
        grid.addWidget(lbl_vf, 0, 2)
        grid.addWidget(self.video_format_combo, 0, 3)

        # Audio Format
        lbl_af = QLabel("Audio Format:")
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(["mp3", "wav", "aac", "ogg", "m4a"])
        self.audio_format_combo.setCurrentText("mp3")
        grid.addWidget(lbl_af, 1, 0)
        grid.addWidget(self.audio_format_combo, 1, 1)

        # Preset
        lbl_pr = QLabel("Device Preset:")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            STANDARD_PRESET,
            PS3_PSVITA_PRESET,
            PS3_PSVITA_480_PRESET,
            MPEG4_SIMPLE_PROFILE_PRESET,
            XBOX_360_PRESET,
        ])
        self.preset_combo.setCurrentText(STANDARD_PRESET)
        grid.addWidget(lbl_pr, 1, 2)
        grid.addWidget(self.preset_combo, 1, 3)

        q_layout.addLayout(grid)

        self.high_quality_check = QCheckBox("Download highest quality source first (superior downscaling)")
        self.high_quality_check.setChecked(True)
        q_layout.addWidget(self.high_quality_check)

        layout.addWidget(quality_card)

        # Card 3: Playlist & Output Directory
        out_card = QFrame()
        out_card.setProperty("class", "vlcCard")
        o_layout = QVBoxLayout(out_card)
        o_layout.setContentsMargins(20, 20, 20, 20)
        o_layout.setSpacing(14)

        o_title = QLabel("Playlist & Storage")
        o_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        o_layout.addWidget(o_title)

        # Playlist Row
        pl_row = QHBoxLayout()
        pl_row.setSpacing(12)
        self.playlist_check = QCheckBox("Download entire playlist")
        max_label = QLabel("Max downloads limit:")
        max_label.setStyleSheet("color: #a1a1aa;")
        self.max_downloads_input = QLineEdit()
        self.max_downloads_input.setText("50")
        self.max_downloads_input.setFixedWidth(80)

        pl_row.addWidget(self.playlist_check)
        pl_row.addSpacing(16)
        pl_row.addWidget(max_label)
        pl_row.addWidget(self.max_downloads_input)
        pl_row.addStretch()
        o_layout.addLayout(pl_row)

        # Path Row
        path_row = QHBoxLayout()
        path_row.setSpacing(10)
        path_label = QLabel("Save to:")
        path_label.setFixedWidth(60)
        self.path_input = QLineEdit()
        self.path_input.setText(str(Path.home() / "Downloads"))

        browse_dl_btn = QPushButton("Browse")
        browse_dl_btn.setProperty("class", "vlcSecondaryBtn")
        browse_dl_btn.clicked.connect(self.browse_download_path)

        path_row.addWidget(path_label)
        path_row.addWidget(self.path_input, 1)
        path_row.addWidget(browse_dl_btn, 0)
        o_layout.addLayout(path_row)

        layout.addWidget(out_card)

        # Card 4: Authentication (Optional)
        auth_card = QFrame()
        auth_card.setProperty("class", "vlcCard")
        a_layout = QVBoxLayout(auth_card)
        a_layout.setContentsMargins(20, 20, 20, 20)
        a_layout.setSpacing(10)

        a_title = QLabel("Authentication & Cookies (Optional)")
        a_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        a_layout.addWidget(a_title)

        cookies_row = QHBoxLayout()
        cookies_row.setSpacing(10)
        self.cookies_input = QLineEdit()
        self.cookies_input.setPlaceholderText("Path to Netscape cookies.txt file for membership / private videos...")

        browse_ck_btn = QPushButton("Browse")
        browse_ck_btn.setProperty("class", "vlcSecondaryBtn")
        browse_ck_btn.clicked.connect(self.browse_cookies_file)

        cookies_row.addWidget(self.cookies_input, 1)
        cookies_row.addWidget(browse_ck_btn, 0)
        a_layout.addLayout(cookies_row)

        cookies_help = QLabel("Tip: Export cookies using browser extensions like 'Get cookies.txt LOCALLY' to bypass sign-in requirements.")
        cookies_help.setStyleSheet("color: #71717a; font-size: 11px;")
        a_layout.addWidget(cookies_help)

        layout.addWidget(auth_card)

        # Action Buttons Row
        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)

        self.download_btn = QPushButton("Start Download")
        self.download_btn.setProperty("class", "vlcPrimaryBtn")
        self.download_btn.setIcon(vlc_theme.render_svg_icon('download', "#ffffff", 16))
        self.download_btn.clicked.connect(self.start_download)

        self.info_btn = QPushButton("Get Video Info")
        self.info_btn.setProperty("class", "vlcSecondaryBtn")
        self.info_btn.setIcon(vlc_theme.render_svg_icon('info', "#a1a1aa", 16))
        self.info_btn.clicked.connect(self.get_video_info)

        open_folder_btn = QPushButton("Open Folder")
        open_folder_btn.setProperty("class", "vlcSecondaryBtn")
        open_folder_btn.setIcon(vlc_theme.render_svg_icon('folder', "#a1a1aa", 16))
        open_folder_btn.clicked.connect(self.open_download_folder)

        actions_row.addWidget(self.download_btn)
        actions_row.addWidget(self.info_btn)
        actions_row.addWidget(open_folder_btn)
        actions_row.addStretch()

        layout.addLayout(actions_row)
        layout.addStretch()

        scroll.setWidget(page)
        self.page_stack.addWidget(scroll)

    def paste_url(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.url_input.setText(text)

    # -------------------------------------------------------------
    # Page 2: Converter Page
    # -------------------------------------------------------------
    def setup_converter_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 20, 28, 28)
        layout.setSpacing(18)

        # Card 1: Source Files
        conv_src_card = QFrame()
        conv_src_card.setProperty("class", "vlcCard")
        cs_layout = QVBoxLayout(conv_src_card)
        cs_layout.setContentsMargins(20, 20, 20, 20)
        cs_layout.setSpacing(14)

        cs_title = QLabel("Local Source Media")
        cs_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        cs_layout.addWidget(cs_title)

        cs_row = QHBoxLayout()
        cs_row.setSpacing(10)
        self.local_video_input = QLineEdit()
        self.local_video_input.setPlaceholderText("Select one or more video files on your computer...")

        browse_files_btn = QPushButton("Browse Files")
        browse_files_btn.setProperty("class", "vlcSecondaryBtn")
        browse_files_btn.setIcon(vlc_theme.render_svg_icon('folder', "#a1a1aa", 14))
        browse_files_btn.clicked.connect(self.browse_local_video_files)

        cs_row.addWidget(self.local_video_input, 1)
        cs_row.addWidget(browse_files_btn, 0)
        cs_layout.addLayout(cs_row)

        layout.addWidget(conv_src_card)

        # Card 2: Transcoding Settings
        conv_opts_card = QFrame()
        conv_opts_card.setProperty("class", "vlcCard")
        co_layout = QVBoxLayout(conv_opts_card)
        co_layout.setContentsMargins(20, 20, 20, 20)
        co_layout.setSpacing(14)

        co_title = QLabel("Conversion Target & Preset")
        co_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        co_layout.addWidget(co_title)

        cgrid = QGridLayout()
        cgrid.setHorizontalSpacing(16)
        cgrid.setVerticalSpacing(12)

        lbl_cp = QLabel("Target Preset:")
        self.conv_preset_combo = QComboBox()
        self.conv_preset_combo.addItems([
            STANDARD_PRESET,
            PS3_PSVITA_PRESET,
            PS3_PSVITA_480_PRESET,
            MPEG4_SIMPLE_PROFILE_PRESET,
            XBOX_360_PRESET,
        ])
        cgrid.addWidget(lbl_cp, 0, 0)
        cgrid.addWidget(self.conv_preset_combo, 0, 1)

        lbl_cq = QLabel("Resolution:")
        self.conv_quality_combo = QComboBox()
        self.conv_quality_combo.addItems(["best", "1080p", "720p", "480p", "360p"])
        self.conv_quality_combo.setCurrentText("720p")
        cgrid.addWidget(lbl_cq, 0, 2)
        cgrid.addWidget(self.conv_quality_combo, 0, 3)

        lbl_cf = QLabel("Output Format:")
        self.conv_format_combo = QComboBox()
        self.conv_format_combo.addItems(["mp4", "mkv", "avi", "webm", "mov"])
        self.conv_format_combo.setCurrentText("mp4")
        cgrid.addWidget(lbl_cf, 1, 0)
        cgrid.addWidget(self.conv_format_combo, 1, 1)

        co_layout.addLayout(cgrid)

        # Output Folder
        out_row = QHBoxLayout()
        out_row.setSpacing(10)
        out_lbl = QLabel("Save to:")
        out_lbl.setFixedWidth(60)
        self.local_output_input = QLineEdit()
        self.local_output_input.setText(str(Path.home() / "Downloads"))

        browse_out_btn = QPushButton("Browse")
        browse_out_btn.setProperty("class", "vlcSecondaryBtn")
        browse_out_btn.clicked.connect(self.browse_local_output_path)

        out_row.addWidget(out_lbl)
        out_row.addWidget(self.local_output_input, 1)
        out_row.addWidget(browse_out_btn, 0)
        co_layout.addLayout(out_row)

        layout.addWidget(conv_opts_card)

        # Action Buttons
        ca_row = QHBoxLayout()
        ca_row.setSpacing(12)

        self.convert_btn = QPushButton("Convert Local Video")
        self.convert_btn.setProperty("class", "vlcPrimaryBtn")
        self.convert_btn.setIcon(vlc_theme.render_svg_icon('convert', "#ffffff", 16))
        self.convert_btn.clicked.connect(self.start_local_conversion)

        open_conv_out_btn = QPushButton("Open Output Folder")
        open_conv_out_btn.setProperty("class", "vlcSecondaryBtn")
        open_conv_out_btn.setIcon(vlc_theme.render_svg_icon('folder', "#a1a1aa", 16))
        open_conv_out_btn.clicked.connect(self.open_output_folder)

        ca_row.addWidget(self.convert_btn)
        ca_row.addWidget(open_conv_out_btn)
        ca_row.addStretch()
        layout.addLayout(ca_row)

        layout.addStretch()
        scroll.setWidget(page)
        self.page_stack.addWidget(scroll)

    # -------------------------------------------------------------
    # Page 3: Media Library
    # -------------------------------------------------------------
    def setup_library_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 20, 28, 28)
        layout.setSpacing(16)

        # Header bar
        header_row = QHBoxLayout()
        header_title = QLabel("Downloaded Media")
        header_title.setStyleSheet("font-weight: bold; font-size: 15px;")
        header_row.addWidget(header_title)

        header_row.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("class", "vlcSecondaryBtn")
        refresh_btn.setIcon(vlc_theme.render_svg_icon('refresh', "#a1a1aa", 14))
        refresh_btn.clicked.connect(self.refresh_library)

        open_lib_btn = QPushButton("Open Folder")
        open_lib_btn.setProperty("class", "vlcSecondaryBtn")
        open_lib_btn.setIcon(vlc_theme.render_svg_icon('folder', "#a1a1aa", 14))
        open_lib_btn.clicked.connect(self.open_download_folder)

        header_row.addWidget(refresh_btn)
        header_row.addWidget(open_lib_btn)
        layout.addLayout(header_row)

        # Media table
        self.library_table = QTableWidget()
        self.library_table.setColumnCount(4)
        self.library_table.setHorizontalHeaderLabels(["Name", "Size", "Modified", "Format"])
        self.library_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.library_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.library_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.library_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.library_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.library_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.library_table.doubleClicked.connect(self.play_library_file)
        layout.addWidget(self.library_table, 1)

        # Library actions row
        lib_actions_row = QHBoxLayout()
        lib_actions_row.setSpacing(10)

        play_btn = QPushButton("Play in Media Player")
        play_btn.setProperty("class", "vlcPrimaryBtn")
        play_btn.setIcon(vlc_theme.render_svg_icon('play', "#ffffff", 14))
        play_btn.clicked.connect(self.play_library_file)

        show_in_folder_btn = QPushButton("Show in File Manager")
        show_in_folder_btn.setProperty("class", "vlcSecondaryBtn")
        show_in_folder_btn.setIcon(vlc_theme.render_svg_icon('folder', "#a1a1aa", 14))
        show_in_folder_btn.clicked.connect(self.show_library_file_in_folder)

        delete_btn = QPushButton("Delete File")
        delete_btn.setProperty("class", "vlcSecondaryBtn")
        delete_btn.setIcon(vlc_theme.render_svg_icon('trash', "#a1a1aa", 14))
        delete_btn.clicked.connect(self.delete_library_file)

        lib_actions_row.addWidget(play_btn)
        lib_actions_row.addWidget(show_in_folder_btn)
        lib_actions_row.addWidget(delete_btn)
        lib_actions_row.addStretch()

        layout.addLayout(lib_actions_row)
        self.page_stack.addWidget(page)

    def refresh_library(self):
        """Scan download directory and populate library table."""
        dl_dir = os.path.expanduser(self.path_input.text().strip())
        if not os.path.isdir(dl_dir):
            self.library_table.setRowCount(0)
            return

        supported_exts = {'.mp4', '.mkv', '.webm', '.avi', '.mov', '.mp3', '.m4a', '.wav', '.ogg', '.aac', '.flac'}
        files = []
        try:
            for entry in os.scandir(dl_dir):
                if entry.is_file() and os.path.splitext(entry.name)[1].lower() in supported_exts:
                    stat = entry.stat()
                    files.append((entry.name, stat.st_size, stat.st_mtime, entry.path))
        except Exception:
            pass

        # Sort newest first
        files.sort(key=lambda x: x[2], reverse=True)

        self.library_table.setRowCount(len(files))
        for row, (name, size, mtime, path) in enumerate(files):
            # Size string
            if size > 1024 * 1024 * 1024:
                size_str = f"{size / (1024*1024*1024):.1f} GB"
            elif size > 1024 * 1024:
                size_str = f"{size / (1024*1024):.1f} MB"
            else:
                size_str = f"{size / 1024:.0f} KB"

            import datetime
            date_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            ext_str = os.path.splitext(name)[1].lstrip('.').upper()

            item_name = QTableWidgetItem(name)
            item_name.setData(Qt.ItemDataRole.UserRole, path)
            item_size = QTableWidgetItem(size_str)
            item_date = QTableWidgetItem(date_str)
            item_fmt = QTableWidgetItem(ext_str)

            self.library_table.setItem(row, 0, item_name)
            self.library_table.setItem(row, 1, item_size)
            self.library_table.setItem(row, 2, item_date)
            self.library_table.setItem(row, 3, item_fmt)

    def get_selected_library_path(self) -> Optional[str]:
        row = self.library_table.currentRow()
        if row >= 0:
            item = self.library_table.item(row, 0)
            if item:
                return item.data(Qt.ItemDataRole.UserRole)
        return None

    def play_library_file(self):
        path = self.get_selected_library_path()
        if path and os.path.isfile(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            self.show_error("Notice", "Please select a media file to play")

    def show_library_file_in_folder(self):
        path = self.get_selected_library_path()
        if path and os.path.isfile(path):
            folder = os.path.dirname(path)
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def delete_library_file(self):
        path = self.get_selected_library_path()
        if path and os.path.isfile(path):
            reply = QMessageBox.question(
                self,
                "Delete Media",
                f"Are you sure you want to delete {os.path.basename(path)}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    os.remove(path)
                    self.refresh_library()
                except Exception as e:
                    self.show_error("Error", f"Failed to delete file: {e}")

    # -------------------------------------------------------------
    # Page 4: Terminal Log Console
    # -------------------------------------------------------------
    def setup_log_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 20, 28, 28)
        layout.setSpacing(14)

        header_row = QHBoxLayout()
        header_title = QLabel("Terminal Activity Log")
        header_title.setStyleSheet("font-weight: bold; font-size: 15px;")
        header_row.addWidget(header_title)

        header_row.addStretch()

        copy_btn = QPushButton("Copy Log")
        copy_btn.setProperty("class", "vlcSecondaryBtn")
        copy_btn.setIcon(vlc_theme.render_svg_icon('copy', "#a1a1aa", 14))
        copy_btn.clicked.connect(self.copy_log)

        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.setProperty("class", "vlcSecondaryBtn")
        self.clear_btn.setIcon(vlc_theme.render_svg_icon('clear', "#a1a1aa", 14))
        self.clear_btn.clicked.connect(self.clear_log)

        header_row.addWidget(copy_btn)
        header_row.addWidget(self.clear_btn)
        layout.addLayout(header_row)

        self.log_text = QTextEdit()
        self.log_text.setObjectName("vlcLogConsole")
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text, 1)

        self.page_stack.addWidget(page)

    def copy_log(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.log_text.toPlainText())
        self.show_info("Copied", "Log output copied to clipboard!")

    # -------------------------------------------------------------
    # Page 5: Settings Page (Appearance & Palette)
    # -------------------------------------------------------------
    def setup_settings_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 20, 28, 28)
        layout.setSpacing(20)

        # Appearance Card (Matches VLC Redesign Page 16 & 71!)
        app_card = QFrame()
        app_card.setProperty("class", "vlcCard")
        ac_layout = QVBoxLayout(app_card)
        ac_layout.setContentsMargins(24, 24, 24, 24)
        ac_layout.setSpacing(16)

        ac_title = QLabel("Appearance & Color Palette")
        ac_title.setStyleSheet("font-weight: bold; font-size: 15px;")
        ac_layout.addWidget(ac_title)

        # Theme mode buttons
        theme_row = QHBoxLayout()
        theme_row.setSpacing(12)
        theme_lbl = QLabel("Theme Mode:")
        theme_lbl.setStyleSheet("font-weight: 600; color: #a1a1aa;")
        theme_row.addWidget(theme_lbl)

        dark_btn = QPushButton("Dark Mode")
        dark_btn.setProperty("class", "vlcSecondaryBtn")
        dark_btn.clicked.connect(lambda: self.set_theme_mode(True))

        light_btn = QPushButton("Light Mode")
        light_btn.setProperty("class", "vlcSecondaryBtn")
        light_btn.clicked.connect(lambda: self.set_theme_mode(False))

        theme_row.addWidget(dark_btn)
        theme_row.addWidget(light_btn)
        theme_row.addStretch()
        ac_layout.addLayout(theme_row)

        # Accent Swatches Picker
        palette_lbl = QLabel("Select Accent Color:")
        palette_lbl.setStyleSheet("font-weight: 600; color: #a1a1aa;")
        ac_layout.addWidget(palette_lbl)

        swatches_row = QHBoxLayout()
        swatches_row.setSpacing(12)
        self.swatch_buttons = []

        for hex_col, name in vlc_theme.ACCENT_PALETTE:
            swatch_btn = QPushButton()
            swatch_btn.setFixedSize(32, 32)
            swatch_btn.setProperty("color_hex", hex_col)
            swatch_btn.setToolTip(name)
            swatch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            swatch_btn.clicked.connect(lambda _, col=hex_col: self.set_accent_color(col))
            self.swatch_buttons.append(swatch_btn)
            swatches_row.addWidget(swatch_btn)

        swatches_row.addStretch()
        ac_layout.addLayout(swatches_row)

        layout.addWidget(app_card)

        # System Diagnostics Card
        sys_card = QFrame()
        sys_card.setProperty("class", "vlcCard")
        sc_layout = QVBoxLayout(sys_card)
        sc_layout.setContentsMargins(24, 24, 24, 24)
        sc_layout.setSpacing(14)

        sc_title = QLabel("System Diagnostics & Backend Tools")
        sc_title.setStyleSheet("font-weight: bold; font-size: 15px;")
        sc_layout.addWidget(sc_title)

        self.diag_ytdlp_label = QLabel(f"yt-dlp version: {get_ytdlp_version()}")
        self.diag_ffmpeg_label = QLabel("ffmpeg status: Checking...")

        sc_layout.addWidget(self.diag_ytdlp_label)
        sc_layout.addWidget(self.diag_ffmpeg_label)

        recheck_btn = QPushButton("Re-check System Tools")
        recheck_btn.setProperty("class", "vlcSecondaryBtn")
        recheck_btn.clicked.connect(self.check_dependencies)
        sc_layout.addWidget(recheck_btn)

        layout.addWidget(sys_card)
        layout.addStretch()

        scroll.setWidget(page)
        self.page_stack.addWidget(scroll)

    # -------------------------------------------------------------
    # Logging & Dialogs
    # -------------------------------------------------------------
    def log(self, message: str):
        """Append a message to the terminal log with formatting."""
        if hasattr(self, 'log_text'):
            self.log_text.append(message)
            self.log_text.ensureCursorVisible()

    def clear_log(self):
        """Clear the log console."""
        if hasattr(self, 'log_text'):
            self.log_text.clear()

    def show_error(self, title: str, message: str):
        """Display an error message box."""
        QMessageBox.critical(self, title, message)

    def show_info(self, title: str, message: str):
        """Display an informational message box."""
        QMessageBox.information(self, title, message)

    # -------------------------------------------------------------
    # File Dialogs
    # -------------------------------------------------------------
    def browse_download_path(self):
        """Browse for download directory."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Download Directory",
            self.path_input.text()
        )
        if folder:
            self.path_input.setText(folder)
            if hasattr(self, 'refresh_library'):
                self.refresh_library()

    def browse_local_video_file(self):
        """Browse for a single local video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a video file",
            "",
            "Video files (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.mpeg *.mpg);;All files (*.*)"
        )
        if file_path:
            self.local_video_input.setText(file_path)

    def browse_local_video_files(self):
        """Browse for multiple local video files."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select video files",
            "",
            "Video files (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.mpeg *.mpg);;All files (*.*)"
        )
        if file_paths:
            self.local_video_input.setText("; ".join(file_paths))

    def browse_local_output_path(self):
        """Browse for local conversion output folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.local_output_input.text()
        )
        if folder:
            self.local_output_input.setText(folder)

    def browse_cookies_file(self):
        """Browse for Netscape cookies.txt file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a cookies.txt file",
            "",
            "Netscape cookies (*.txt);;All files (*.*)"
        )
        if file_path:
            self.cookies_input.setText(file_path)

    def open_download_folder(self):
        """Open the downloads folder in file manager."""
        path = os.path.expanduser(self.path_input.text().strip())
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            self.show_error("Folder Not Found", f"Directory does not exist: {path}")

    def open_output_folder(self):
        """Open the conversion output folder in file manager."""
        path = os.path.expanduser(self.local_output_input.text().strip())
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            self.show_error("Folder Not Found", f"Directory does not exist: {path}")

    # -------------------------------------------------------------
    # Dependencies
    # -------------------------------------------------------------
    def check_dependencies(self):
        """Check availability of yt-dlp and ffmpeg."""
        self.log("Willhiem - VLC Community Design Edition")
        self.log("Checking dependencies...")

        ytdlp_ver = get_ytdlp_version()
        self.log(f"✓ yt-dlp is available ({ytdlp_ver})")
        if is_ytdlp_outdated():
            self.log("⚠️ yt-dlp is older than recommended; update with `python3 -m pip install --upgrade yt-dlp`")

        if hasattr(self, 'sidebar_ytdlp_status'):
            self.sidebar_ytdlp_status.setText(f"yt-dlp: v{ytdlp_ver}")
        if hasattr(self, 'diag_ytdlp_label'):
            self.diag_ytdlp_label.setText(f"yt-dlp: v{ytdlp_ver} {'(Up to date)' if not is_ytdlp_outdated() else '(Update recommended)'}")

        try:
            res = subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, text=True)
            first_line = res.stdout.splitlines()[0] if res.stdout else "ffmpeg active"
            self.log(f"✓ {first_line}")
            if hasattr(self, 'sidebar_ffmpeg_status'):
                self.sidebar_ffmpeg_status.setText("ffmpeg: ready")
            if hasattr(self, 'diag_ffmpeg_label'):
                self.diag_ffmpeg_label.setText(f"ffmpeg: {first_line}")
        except Exception:
            self.log("✗ ffmpeg not found! Please install with: sudo apt install ffmpeg")
            if hasattr(self, 'sidebar_ffmpeg_status'):
                self.sidebar_ffmpeg_status.setText("ffmpeg: missing")
            if hasattr(self, 'diag_ffmpeg_label'):
                self.diag_ffmpeg_label.setText("ffmpeg: NOT FOUND (sudo apt install ffmpeg)")

        self.log("Dependency checks completed.\n")

    # -------------------------------------------------------------
    # Download Execution
    # -------------------------------------------------------------
    def get_video_info(self):
        """Fetch metadata for URL."""
        url = self.url_input.text().strip()
        if not url:
            self.show_error("Error", "Please enter a video URL")
            return

        if not is_valid_media_url(url):
            self.show_error("Error", "Please enter a valid http(s) video or playlist URL")
            return

        self.download_btn.setEnabled(False)
        self.info_btn.setEnabled(False)
        self.convert_btn.setEnabled(False)
        self.progress.setValue(-1)
        self.status_title_label.setText("Fetching Video Metadata...")
        self.status_detail_label.setText(url)
        self.top_status_badge.setText("● Fetching Info")

        self.info_worker = InfoWorker(url)
        self.info_worker.log_message.connect(self.log)
        self.info_worker.finished.connect(self.on_info_finished)
        self.info_worker.error.connect(lambda title, msg: (self.show_error(title, msg), self.log(msg)))
        self.info_worker.start()

    def on_info_finished(self):
        """Worker info completion."""
        self.download_btn.setEnabled(True)
        self.info_btn.setEnabled(True)
        self.convert_btn.setEnabled(True)
        self.progress.setValue(0)
        self.status_title_label.setText("Willhiem")
        self.status_detail_label.setText("Metadata retrieved successfully")
        self.top_status_badge.setText("● Ready")

    def on_download_progress(self, percent: int):
        """Update download progress."""
        if percent < 0:
            self.progress.setValue(0)
            self.progress_percent_label.setText("...")
        else:
            val = min(100, percent)
            self.progress.setValue(val)
            self.progress_percent_label.setText(f"{val}%")

    def on_download_finished(self):
        """Download worker finished successfully."""
        self.show_info("Success", "Download completed successfully!")
        self.download_btn.setEnabled(True)
        self.info_btn.setEnabled(True)
        self.convert_btn.setEnabled(True)
        self.progress.setValue(0)
        self.progress_percent_label.setText("100%")
        self.status_title_label.setText("Willhiem")
        self.status_detail_label.setText("Download completed")
        self.top_status_badge.setText("● Ready")
        if hasattr(self, 'refresh_library'):
            self.refresh_library()

    def on_download_error(self, title: str, message: str):
        """Download worker error handler."""
        self.download_btn.setEnabled(True)
        self.info_btn.setEnabled(True)
        self.convert_btn.setEnabled(True)
        self.progress.setValue(0)
        self.status_title_label.setText("Download Failed")
        self.status_detail_label.setText("Error encountered during download")
        self.top_status_badge.setText("● Error")

    def start_download(self):
        """Initiate YouTube / media download."""
        url = self.url_input.text().strip()
        if not url:
            self.show_error("Error", "Please enter a video URL")
            return

        if not is_valid_media_url(url):
            self.show_error("Error", "Please enter a valid http(s) video or playlist URL")
            return

        btn = self.type_group.checkedButton()
        download_type = "video"
        if btn:
            text = btn.text().lower()
            if "audio" in text:
                download_type = "audio"
            elif "info" in text:
                download_type = "info"

        if download_type == "info":
            self.log("ℹ️ Info mode selected - fetching details instead of downloading.")
            self.get_video_info()
            return

        download_dir = os.path.expanduser(self.path_input.text().strip())
        if not download_dir:
            self.show_error("Error", "Please choose a download directory")
            return

        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except Exception as e:
                self.show_error("Error", f"Cannot create download directory: {e}")
                return

        self.download_btn.setEnabled(False)
        self.info_btn.setEnabled(False)
        self.convert_btn.setEnabled(False)
        self.status_title_label.setText("Downloading...")
        self.status_detail_label.setText(url)
        self.top_status_badge.setText("● Downloading")

        self.download_worker = DownloadWorker(
            url=url,
            download_dir=download_dir,
            video_format=self.video_format_combo.currentText(),
            audio_format=self.audio_format_combo.currentText(),
            quality=self.quality_combo.currentText(),
            video_preset=self.preset_combo.currentText(),
            download_type=download_type,
            playlist_mode=self.playlist_check.isChecked(),
            max_downloads=self.max_downloads_input.text(),
            high_quality_source=self.high_quality_check.isChecked(),
            cookies_file=self.cookies_input.text()
        )
        self.download_worker.progress.connect(self.on_download_progress)
        self.download_worker.log_message.connect(self.log)
        self.download_worker.finished.connect(self.on_download_finished)
        self.download_worker.error.connect(lambda title, msg: (self.show_error(title, msg), self.on_download_error(title, msg)))
        self.download_worker.start()

    # -------------------------------------------------------------
    # Local Conversion Execution
    # -------------------------------------------------------------
    def on_conversion_progress(self, percent: int):
        """Update conversion progress."""
        if percent < 0:
            self.progress.setValue(0)
            self.progress_percent_label.setText("...")
        else:
            val = min(100, percent)
            self.progress.setValue(val)
            self.progress_percent_label.setText(f"{val}%")

    def on_conversion_finished(self):
        """Conversion completed."""
        source_text = self.local_video_input.text().strip()
        source_paths = [p.strip() for p in re.split(r"[;\n]+", source_text) if p.strip()]
        if len(source_paths) > 1:
            self.show_info("Success", f"Batch conversion completed for {len(source_paths)} files!")
        else:
            self.show_info("Success", "Local conversion completed successfully!")

        self.download_btn.setEnabled(True)
        self.info_btn.setEnabled(True)
        self.convert_btn.setEnabled(True)
        self.progress.setValue(0)
        self.progress_percent_label.setText("100%")
        self.status_title_label.setText("Willhiem")
        self.status_detail_label.setText("Conversion finished")
        self.top_status_badge.setText("● Ready")
        if hasattr(self, 'refresh_library'):
            self.refresh_library()

    def on_conversion_error(self, title: str, message: str):
        """Conversion error handler."""
        self.download_btn.setEnabled(True)
        self.info_btn.setEnabled(True)
        self.convert_btn.setEnabled(True)
        self.progress.setValue(0)
        self.status_title_label.setText("Conversion Failed")
        self.status_detail_label.setText("Error during transcoding")
        self.top_status_badge.setText("● Error")

    def start_local_conversion(self):
        """Execute local transcoding job."""
        source_text = self.local_video_input.text().strip()
        output_dir = os.path.expanduser(self.local_output_input.text().strip())

        if not source_text:
            self.show_error("Error", "Please select one or more local video files")
            return

        source_paths = [p.strip() for p in re.split(r"[;\n]+", source_text) if p.strip()]
        if not source_paths:
            self.show_error("Error", "Please select one or more local video files")
            return

        for path in source_paths:
            if not os.path.isfile(path):
                self.show_error("Error", f"Selected file does not exist:\n{path}")
                return

        if not output_dir:
            self.show_error("Error", "Please choose an output directory")
            return

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                self.show_error("Error", f"Cannot create output directory: {e}")
                return

        self.download_btn.setEnabled(False)
        self.info_btn.setEnabled(False)
        self.convert_btn.setEnabled(False)
        self.status_title_label.setText(f"Converting ({len(source_paths)} file{'s' if len(source_paths)>1 else ''})...")
        self.status_detail_label.setText(f"Preset: {self.conv_preset_combo.currentText()}")
        self.top_status_badge.setText("● Converting")

        self.conversion_worker = ConversionWorker(
            source_paths=source_paths,
            output_dir=output_dir,
            video_preset=self.conv_preset_combo.currentText(),
            quality=self.conv_quality_combo.currentText(),
            video_format=self.conv_format_combo.currentText()
        )
        self.conversion_worker.progress.connect(self.on_conversion_progress)
        self.conversion_worker.log_message.connect(self.log)
        self.conversion_worker.finished.connect(self.on_conversion_finished)
        self.conversion_worker.error.connect(lambda title, msg: (self.show_error(title, msg), self.on_conversion_error(title, msg)))
        self.conversion_worker.start()


# Backwards compatibility alias
LinuxTubeCatcher = Willhiem


def main():
    """Main application entry point."""
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = Willhiem()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
