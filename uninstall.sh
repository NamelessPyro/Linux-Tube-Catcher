#!/bin/bash

# Linux Tube Catcher - Uninstaller
# Created by NamelessPyro

echo "=================================================="
echo "   Linux Tube Catcher - Uninstaller"
echo "   Created by NamelessPyro"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

INSTALL_DIR="$HOME/.local/share/linux-tube-catcher"
DESKTOP_FILE="$HOME/.local/share/applications/linux-tube-catcher.desktop"
BIN_FILE="$HOME/.local/bin/linux-tube-catcher"

echo "This will remove Linux Tube Catcher from your system."
echo "The following will be deleted:"
echo "  - $INSTALL_DIR"
echo "  - $DESKTOP_FILE"
echo "  - $BIN_FILE"
echo ""
echo -n "Are you sure you want to uninstall? (y/N): "
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    print_status "Removing Linux Tube Catcher..."
    
    # Remove installation directory
    if [[ -d "$INSTALL_DIR" ]]; then
        rm -rf "$INSTALL_DIR"
        print_status "Removed installation directory"
    fi
    
    # Remove desktop file
    if [[ -f "$DESKTOP_FILE" ]]; then
        rm -f "$DESKTOP_FILE"
        print_status "Removed desktop launcher"
    fi
    
    # Remove binary
    if [[ -f "$BIN_FILE" ]]; then
        rm -f "$BIN_FILE"
        print_status "Removed command launcher"
    fi
    
    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    fi
    
    echo ""
    print_status "✅ Linux Tube Catcher has been uninstalled successfully!"
    print_warning "Note: System dependencies (python3, ffmpeg, etc.) were not removed"
    print_warning "as they may be used by other applications."
else
    echo "Uninstallation cancelled."
fi
