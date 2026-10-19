#!/bin/bash

# Willhiem - Quick Test Script
# Tests the installation without full setup

echo "🧪 Willhiem - Quick Test"
echo "========================"

# Test Python
if command -v python3 &> /dev/null; then
    echo "✓ Python3 available: $(python3 --version)"
else
    echo "✗ Python3 not found"
    exit 1
fi

# Test pip
if command -v pip3 &> /dev/null || python3 -m pip --version &> /dev/null; then
    echo "✓ pip available"
else
    echo "✗ pip not found"
    exit 1
fi

# Test tkinter
if python3 -c "import tkinter" 2>/dev/null; then
    echo "✓ tkinter available"
else
    echo "✗ tkinter not available - install python3-tk"
fi

# Test yt-dlp
if YTDLP_VERSION=$(python3 -c "import yt_dlp; print(yt_dlp.version.__version__)" 2>/dev/null); then
    echo "✓ yt-dlp available: $YTDLP_VERSION"

    python3 - <<'PY' >/dev/null 2>&1
import sys
import yt_dlp
version = tuple(int(part) for part in yt_dlp.version.__version__.split('.')[:3])
sys.exit(0 if version >= (2025, 3, 31) else 1)
PY
    if [[ $? -ne 0 ]]; then
        echo "⚠ yt-dlp is outdated; recent YouTube links may fail until you upgrade it"
        echo "  Run: python3 -m pip install --upgrade yt-dlp"
    fi
else
    echo "✗ yt-dlp not available - install with: python3 -m pip install --upgrade yt-dlp"
fi

# Test ffmpeg
if command -v ffmpeg &> /dev/null; then
    echo "✓ ffmpeg available: $(ffmpeg -version 2>&1 | head -1 | cut -d' ' -f3)"
else
    echo "✗ ffmpeg not found - install ffmpeg package"
fi

# Test virtual environment creation
if python3 -m venv test_venv 2>/dev/null; then
    echo "✓ Virtual environment creation works"
    rm -rf test_venv
else
    echo "✗ Cannot create virtual environment - install python3-venv"
fi

echo ""
echo "🎯 System readiness check complete!"
echo "If all items show ✓, you can run ./easy-install.sh"
