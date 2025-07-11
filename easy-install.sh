#!/bin/bash

# Linux Tube Catcher - Easy Installer for General Public
# Created by NamelessPyro
# Version 1.0

set -e  # Exit on any error

echo "=================================================="
echo "   Linux Tube Catcher - Easy Installer v1.0"
echo "   Created by NamelessPyro"
echo "=================================================="
echo ""

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running on supported system
print_step "Checking system compatibility..."
if [[ ! -f /etc/os-release ]]; then
    print_error "Cannot determine OS. This installer is designed for Ubuntu/Debian-based systems."
    exit 1
fi

source /etc/os-release
if [[ "$ID" != "ubuntu" && "$ID" != "debian" && "$ID" != "linuxmint" && "$ID" != "pop" ]]; then
    print_warning "This installer is optimized for Ubuntu/Debian-based systems."
    print_warning "Your system: $PRETTY_NAME"
    echo -n "Do you want to continue anyway? (y/N): "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 1
    fi
fi

print_status "System: $PRETTY_NAME - Compatible!"
echo ""

# Check if user has sudo privileges
print_step "Checking for sudo privileges..."
if ! sudo -n true 2>/dev/null; then
    print_status "You will be prompted for your password to install system packages."
    if ! sudo true; then
        print_error "This installer requires sudo privileges to install system dependencies."
        exit 1
    fi
fi

print_status "Sudo access confirmed!"
echo ""

# Set installation directory
INSTALL_DIR="$HOME/.local/share/linux-tube-catcher"
DESKTOP_FILE="$HOME/.local/share/applications/linux-tube-catcher.desktop"
BIN_DIR="$HOME/.local/bin"

print_step "Installation will be performed in: $INSTALL_DIR"
echo ""

# Update package list
print_step "Updating package list..."
sudo apt update

# Install system dependencies
print_step "Installing system dependencies..."
print_status "Installing: python3, python3-pip, python3-venv, python3-tkinter, ffmpeg"

# Try to install packages, with fallbacks
PACKAGES="python3 python3-pip python3-venv python3-tk ffmpeg"

# For older systems, try alternative package names
if ! sudo apt install -y $PACKAGES; then
    print_warning "Trying alternative package names for older systems..."
    sudo apt install -y python3 python3-pip python3-venv python3-tkinter ffmpeg || {
        print_error "Failed to install required system packages."
        print_error "Please manually install: python3, python3-pip, python3-venv, python3-tk/python3-tkinter, ffmpeg"
        exit 1
    }
fi

# Install multimedia codecs (optional, but recommended)
print_step "Installing multimedia codecs (may require user confirmation)..."
if command -v ubuntu-drivers &> /dev/null; then
    sudo apt install -y ubuntu-restricted-extras || print_warning "Could not install ubuntu-restricted-extras (this is optional)"
else
    print_status "Skipping ubuntu-restricted-extras (not available on this system)"
fi

# Create installation directory
print_step "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$(dirname "$DESKTOP_FILE")"

# Copy application files
print_step "Installing application files..."
cp linux_tube_catcher.py "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"
cp icon.png "$INSTALL_DIR/" 2>/dev/null || print_warning "Icon file not found, will create default"
cp README.md "$INSTALL_DIR/" 2>/dev/null || print_warning "README not found"

# Create Python virtual environment
print_step "Creating Python virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv venv

# Activate virtual environment and install Python dependencies
print_step "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create icon if not present
if [[ ! -f "$INSTALL_DIR/icon.png" ]]; then
    print_step "Creating application icon..."
    python3 -c "
from PIL import Image, ImageDraw
import os

size = 128
img = Image.new('RGBA', (size, size), color=(45, 45, 45, 255))
draw = ImageDraw.Draw(img)

# Draw a play button symbol
play_color = (255, 69, 0, 255)  # Orange-red color

# Triangle for play button
triangle_points = [
    (size//3, size//4),
    (size//3, 3*size//4),
    (3*size//4, size//2)
]
draw.polygon(triangle_points, fill=play_color)

# Draw border
draw.rectangle([0, 0, size-1, size-1], outline=(200, 200, 200, 255), width=2)

# Save the icon
img.save('$INSTALL_DIR/icon.png', 'PNG')
print('Icon created successfully')
" || print_warning "Could not create icon (Pillow not available)"
fi

# Create launcher script
print_step "Creating launcher script..."
cat > "$BIN_DIR/linux-tube-catcher" << 'EOF'
#!/bin/bash
# Linux Tube Catcher Launcher
INSTALL_DIR="$HOME/.local/share/linux-tube-catcher"
cd "$INSTALL_DIR"
source venv/bin/activate
python3 linux_tube_catcher.py "$@"
EOF

chmod +x "$BIN_DIR/linux-tube-catcher"

# Create desktop entry
print_step "Creating desktop launcher..."
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Linux Tube Catcher
Comment=Download and convert videos from YouTube and other platforms
Comment[es]=Descarga y convierte videos de YouTube y otras plataformas
Exec=$BIN_DIR/linux-tube-catcher
Icon=$INSTALL_DIR/icon.png
Terminal=false
Categories=AudioVideo;Video;Network;
Keywords=video;download;youtube;converter;
StartupNotify=true
MimeType=text/uri-list;
EOF

chmod +x "$DESKTOP_FILE"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    print_step "Updating desktop database..."
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

# Add ~/.local/bin to PATH if not already there
print_step "Setting up PATH..."
SHELL_RC=""
if [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
elif [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
fi

if [[ -n "$SHELL_RC" && -f "$SHELL_RC" ]]; then
    if ! grep -q "$HOME/.local/bin" "$SHELL_RC"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        print_status "Added ~/.local/bin to PATH in $SHELL_RC"
        print_warning "Please restart your terminal or run: source $SHELL_RC"
    fi
fi

# Test installation
print_step "Testing installation..."
cd "$INSTALL_DIR"
source venv/bin/activate
python3 -c "
import sys
import tkinter as tk
try:
    import yt_dlp
    print('✓ yt-dlp available')
except ImportError:
    print('✗ yt-dlp not available')
    sys.exit(1)

try:
    import subprocess
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
    if result.returncode == 0:
        print('✓ ffmpeg available')
    else:
        print('✗ ffmpeg not working')
        sys.exit(1)
except Exception:
    print('✗ ffmpeg test failed')
    sys.exit(1)

# Test tkinter by creating a hidden window
try:
    root = tk.Tk()
    root.withdraw()  # Hide the window
    root.destroy()
    print('✓ tkinter working')
except Exception as e:
    print(f'✗ tkinter error: {e}')
    sys.exit(1)

print('✓ All dependencies working!')
"

if [[ $? -eq 0 ]]; then
    echo ""
    echo "=================================================="
    print_status "✅ Installation completed successfully!"
    echo "=================================================="
    echo ""
    echo "🚀 How to run Linux Tube Catcher:"
    echo ""
    echo "1. 📱 From Applications Menu:"
    echo "   Search for 'Linux Tube Catcher' in your app launcher"
    echo ""
    echo "2. 💻 From Terminal:"
    echo "   linux-tube-catcher"
    echo "   (restart terminal first if command not found)"
    echo ""
    echo "3. 📁 Installation location:"
    echo "   $INSTALL_DIR"
    echo ""
    echo "🎯 Features available:"
    echo "   • Download videos from YouTube, Vimeo, and 1000+ sites"
    echo "   • Full playlist support with smart organization"
    echo "   • High-quality download mode for better video scaling"
    echo "   • Convert to multiple formats (MP4, AVI, MKV, WebM, MOV)"
    echo "   • Extract audio to MP3, WAV, AAC, OGG, M4A"
    echo ""
    echo "📚 Documentation: $INSTALL_DIR/README.md"
    echo ""
    print_status "Created by NamelessPyro"
    echo "=================================================="
else
    print_error "Installation completed but there were issues with dependencies."
    print_error "Please check the error messages above."
    exit 1
fi
