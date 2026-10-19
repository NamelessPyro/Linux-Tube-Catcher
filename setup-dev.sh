#!/bin/bash
# Quick dev setup — run this once from the repo folder to create a local venv
# then launch with: ./run.sh

set -e

echo "=== Willhiem - Dev Setup ==="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Step 1: system library required by Qt6 xcb plugin
echo "[1/4] Installing system library for Qt6 (libxcb-cursor0)..."
if ! dpkg -s libxcb-cursor0 &>/dev/null; then
    sudo apt install -y libxcb-cursor0
    echo "  ✓ libxcb-cursor0 installed"
else
    echo "  ✓ libxcb-cursor0 already installed"
fi

# Step 2: create local venv if it doesn't exist
echo "[2/4] Setting up Python virtual environment..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    echo "  ✓ venv created"
else
    echo "  ✓ venv already exists"
fi

# Step 3: install Python dependencies into the venv
echo "[3/4] Installing Python packages (PyQt6, yt-dlp, Pillow)..."
venv/bin/pip install --upgrade pip -q
venv/bin/pip install --upgrade -r requirements.txt -q
echo "  ✓ Packages installed"

# Step 4: verify
echo "[4/4] Verifying dependencies..."
venv/bin/python3 -c "
import yt_dlp, subprocess
from PyQt6.QtWidgets import QApplication
result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
assert result.returncode == 0, 'ffmpeg missing'
print('  ✓ yt-dlp:', yt_dlp.version.__version__)
print('  ✓ PyQt6: OK')
print('  ✓ ffmpeg: OK')
"

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Run the app with:"
echo "  ./run.sh"
echo ""
