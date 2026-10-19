#!/bin/bash

# Willhiem - Uninstaller
# Created by NamelessPyro

echo "=================================================="
echo "   Willhiem - Uninstaller"
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

INSTALL_DIR="$HOME/.local/share/willhiem"
DESKTOP_FILE="$HOME/.local/share/applications/willhiem.desktop"
BIN_FILE="$HOME/.local/bin/willhiem"
LEGACY_INSTALL_DIR="$HOME/.local/share/linux-tube-catcher"
LEGACY_DESKTOP_FILE="$HOME/.local/share/applications/linux-tube-catcher.desktop"
LEGACY_BIN_FILE="$HOME/.local/bin/linux-tube-catcher"

echo "This will remove Willhiem from your system."
echo "The following will be deleted:"
echo "  - $INSTALL_DIR"
echo "  - $DESKTOP_FILE"
echo "  - $BIN_FILE"
echo ""
echo -n "Are you sure you want to uninstall? (y/N): "
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    print_status "Removing Willhiem..."
    
    # Remove installation directory
    for dir in "$INSTALL_DIR" "$LEGACY_INSTALL_DIR"; do
        if [[ -d "$dir" ]]; then
            rm -rf "$dir"
            print_status "Removed installation directory: $dir"
        fi
    done
    
    # Remove desktop file
    for df in "$DESKTOP_FILE" "$LEGACY_DESKTOP_FILE"; do
        if [[ -f "$df" ]]; then
            rm -f "$df"
            print_status "Removed desktop launcher: $df"
        fi
    done
    
    # Remove binary
    for bf in "$BIN_FILE" "$LEGACY_BIN_FILE"; do
        if [[ -f "$bf" || -L "$bf" ]]; then
            rm -f "$bf"
            print_status "Removed command launcher: $bf"
        fi
    done
    
    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    fi
    
    echo ""
    print_status "✅ Willhiem has been uninstalled successfully!"
    print_warning "Note: System dependencies (python3, ffmpeg, etc.) were not removed"
    print_warning "as they may be used by other applications."
else
    echo "Uninstallation cancelled."
fi
