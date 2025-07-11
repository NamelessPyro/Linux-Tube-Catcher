Linux port of aTube Catcher for Linux Mint 22.1 Cinnamon. This application provides video downloading and conversion capabilities similar to the original aTube Catcher but designed specifically for Linux systems.inux Tube Catcher

A Linux port of aTube Catcher for Linux Mint 22.1 Cinnamon. This application provides video downloading and conversion capabilities similar to the original aTube Catcher but designed specifically for Linux systems.

## Features

- Download videos from YouTube and many other platforms
- **Full playlist support** - Download entire playlists or limit downloads
- **High-quality source mode** - Download highest quality first, then scale for better results
- Convert videos to various formats (MP4, AVI, MKV, WebM, MOV)
- Extract audio to different formats (MP3, WAV, AAC, OGG, M4A)
- Multiple quality options (144p to 1080p, or best available)
- User-friendly GUI built with tkinter
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
   sudo apt install python3 python3-pip python3-venv python3-tk ffmpeg ubuntu-restricted-extras
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

1. After installation, search for "Linux Tube Catcher" in your applications menu

2. Or from terminal:
   ```bash
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
5. **Configure Options**: Set quality, video format, and audio format
6. **High-Quality Mode**: Check "Download highest quality first" for better scaling results
7. **Download**: Click the download button to start

### High-Quality Source Mode

When enabled, this feature:
- Downloads the highest available quality (usually 1080p or higher)
- Uses FFmpeg to intelligently scale down to your target resolution
- Maintains better visual quality compared to downloading lower quality directly
- Uses efficient encoding settings (H.264, CRF 23) for good quality/size balance
- Copies audio without re-encoding to preserve quality

**Recommended for:** When you want the best possible quality at lower resolutions (like 720p from 4K source)

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

- **yt-dlp**: Video downloading engine
- **ffmpeg**: Video/audio processing
- **tkinter**: GUI framework (usually included with Python)
- **Pillow**: Image processing
- **requests**: HTTP library

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

### Version 1.0
- Initial release
- Basic video downloading functionality
- Audio extraction
- Format conversion
- GUI interface
- Linux Mint 22.1 compatibility

---
**Created by NamelessPyro**
