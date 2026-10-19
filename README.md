# Willhiem (formerly Linux Tube Catcher)

A modern multimedia downloader and device transcoder for Linux, designed with the sleek VLC Community Redesign aesthetic.

## Features

- **Modern VLC Community Redesign UI** - Clean, elegant dark-mode aesthetic with sidebar navigation
- **Custom Application Icon** - Bespoke branding with smooth high-resolution iconography
- **Dynamic Accent Color Picker** - Choose from 9 signature swatches (VLC Orange, Crimson, Amber, Emerald, Teal, Sapphire, Amethyst, Magenta, Slate)
- **Light & Dark Mode Support** - Seamlessly switch between dark and light themes
- **Media Library** - Browse, play, and manage downloaded video and audio files directly in the app
- **Persistent Bottom Player Bar** - Real-time progress scrubber, speed, percentage, and status indicators
- Download videos from YouTube and many other platforms
- **Full playlist support** - Download entire playlists or limit downloads
- **High-quality source mode** - Download highest quality first, then scale for better results
- **Authentication support** - Use browser cookies to access private/age-restricted/membership videos
- Convert videos to various formats (MP4, AVI, MKV, WebM, MOV)
- Convert to a PS3 / PS Vita compatible 720p H.264 MP4 preset
- Convert to a lighter PS3 / PS Vita compatible 480p H.264 MP4 preset for lower CPU/AVC load
- Convert to a PS3 / PS Vita compatible 720p MPEG-4 Simple Profile preset
- Convert to an Xbox 360 compatible 720p H.264 MP4 preset
- Extract audio to different formats (MP3, WAV, AAC, OGG, M4A)
- Convert local videos from your device without downloading
- Show progress for YouTube downloads and local conversions
- Multiple quality options (144p to 1080p, or best available)
- Progress tracking and detailed logging
- Batch downloads support
- Video information extraction
- Automatic playlist detection and organization

## Supported Platforms

- YouTube
- Vimeo
- Dailymotion
- Facebook
- Instagram
- Twitter
- And many more (powered by yt-dlp)

## Installation

### Automatic Installation

1. Make the installation script executable:
   ```bash
   chmod +x easy-install.sh
   ```

2. Run the installation script:
   ```bash
   ./easy-install.sh
   ```

### Manual Installation

1. Install system dependencies:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv ffmpeg ubuntu-restricted-extras libxcb-cursor0
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

1. After installation, search for "Willhiem" in your applications menu

2. Or from terminal:
   ```bash
   willhiem
   # or legacy alias:
   linux-tube-catcher
   ```

3. Or manually:
   ```bash
   source venv/bin/activate
   python3 linux_tube_catcher.py
   ```

### Using the Interface

1. **Enter Video/Playlist URL**: Paste the URL of the video or playlist you want to download
2. **Choose Download Path**: Select where you want to save the file(s)
3. **Playlist Options**: 
   - Check "Download entire playlist" for playlist URLs
   - Set maximum downloads to limit large playlists
4. **Select Type**: Choose between video, audio-only, or just getting video info
5. **Configure Options**: Set quality, video format, audio format, and device preset
6. **High-Quality Mode**: Check "Download highest quality first" for better scaling results
7. **Download YouTube Videos**: Click the download button to start
8. **Convert Local Videos**: Use the local video file section to convert a video already on your device

### High-Quality Source Mode

When enabled, this feature:
- Downloads the highest available quality (usually 1080p or higher)
- Uses FFmpeg to intelligently scale down to your target resolution
- Maintains better visual quality compared to downloading lower quality directly
- Uses efficient encoding settings (H.264, CRF 23) for good quality/size balance
- Copies audio without re-encoding to preserve quality

**Recommended for:** When you want the best possible quality at lower resolutions (like 720p from 4K source)

### Authentication (Cookies Support)

For videos that require login (private, age-restricted, membership-only):
1. **Export cookies from your browser**: Use the "Get cookies.txt" browser extension to export cookies
2. **Load cookies in the app**: Use the "Cookies File" option in the Authentication section
3. **Download authenticated content**: The app will use your cookies for authentication

**Supported formats:**
- Netscape cookies.txt format (standard cookie export)

**Note:** Cookies expire over time and may need to be refreshed if downloads start failing again.

### Playlist Download Behavior

- **With "Download entire playlist" checked**: Downloads all videos (up to max limit)
- **Without playlist option**: Downloads only the specific video from the URL
- **Folder Organization**: Playlist videos are saved in subfolders named after the playlist
- **Numbering**: Videos are automatically numbered based on playlist order

### Supported URL Examples

- **Single Videos:**
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://vimeo.com/VIDEO_ID`
  - `https://www.dailymotion.com/video/VIDEO_ID`

- **Playlists:**
  - `https://www.youtube.com/playlist?list=PLAYLIST_ID`
  - `https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID`
  - `https://vimeo.com/showcase/SHOWCASE_ID`

### Playlist Features

- **Automatic Detection**: The app automatically detects if a URL contains a playlist
- **Smart Organization**: Playlist videos are saved in organized folders with numbering
- **Download Limits**: Set maximum number of videos to download from large playlists
- **Single Video Mode**: Option to download just one video from a playlist URL

## Requirements

### System Requirements

- Linux Mint 22.1 Cinnamon (or compatible Ubuntu-based distribution)
- Python 3.6 or higher
- At least 1GB of free disk space
- Internet connection

### Dependencies

- **yt-dlp**: Video downloading engine (2025.3.31 or newer recommended)
- **ffmpeg**: Video/audio processing
- **tkinter**: GUI framework (usually included with Python)
- **Pillow**: Image processing

## Troubleshooting

### Common Issues

1. **"ffmpeg not found" error**:
   ```bash
   sudo apt install ffmpeg
   ```

2. **"No module named tkinter" error**:
   ```bash
   sudo apt install python3-tk
   ```

3. **Permission denied errors**:
   ```bash
   chmod +x easy-install.sh uninstall.sh
   ```

4. **Installation issues**:
   ```bash
   ./easy-install.sh
   ```

5. **YouTube video fails with 403 / "Precondition check failed"**:
   ```bash
   python3 -m pip install --upgrade yt-dlp
   ```

6. **Video requires authentication but download still fails**:
   - Export fresh cookies: Use "Get cookies.txt" extension in your browser
   - Re-select the cookies file in the app
   - Some videos may have region/account restrictions that cookies alone can't bypass
   - Verify you're logged into the correct account when exporting cookies

### Performance Tips

- For faster downloads, ensure you have a stable internet connection
- Use SSD storage for better I/O performance during conversion
- Close unnecessary applications during large downloads/conversions

## File Structure

```
LinuxTubeCatcher-Distribution/
├── easy-install.sh           # One-click installer
├── uninstall.sh             # Clean uninstaller
├── linux_tube_catcher.py    # Main application
├── requirements.txt         # Python dependencies
├── icon.png                # Application icon
├── README.md               # This file
├── DISTRIBUTION-README.md  # User guide
├── test-system.sh          # System compatibility test
└── LICENSE                 # MIT License
```

## Comparison with Original aTube Catcher

| Feature | aTube Catcher (Windows) | Linux Tube Catcher |
|---------|-------------------------|-------------------|
| Video Download | ✓ | ✓ |
| Audio Extraction | ✓ | ✓ |
| Format Conversion | ✓ | ✓ |
| Batch Downloads | ✓ | ✓ |
| **Playlist Support** | ✓ | ✓ |
| **Playlist Organization** | Limited | ✓ |
| Built-in Browser | ✓ | ✗ |
| DVD Burning | ✓ | ✗ |
| Screen Recording | ✓ | ✗ |
| Cross-platform | Windows only | Linux |

## License

This project is open-source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Changelog

### Version 1.1
- Improved URL validation before downloads start
- Safer threaded UI updates for log/progress/message dialogs
- Better handling for "Video Info" mode and playlist inspection
- Simplified Python dependencies for easier installation

### Version 1.2
- Aligned the dependency minimums with the app's yt-dlp compatibility check
- Removed the stale requests dependency reference from the documentation

### Version 1.3
- Added a PS3 / PS Vita 720p conversion preset using H.264, AAC, and MP4

### Version 1.4
- Added a separate local video conversion workflow
- Added an MPEG-4 Simple Profile 720p preset
- Applied the device presets to both downloaded and local videos

### Version 1.5
- Added an Xbox 360 720p preset
- Added visible progress updates for downloads and local conversions

### Version 1.6
- Auto-uses the repo or install virtualenv when launched directly

### Version 1.0
- Initial release
- Basic video downloading functionality
- Audio extraction
- Format conversion
- GUI interface
- Linux Mint 22.1 compatibility

---
**Created by NamelessPyro**
