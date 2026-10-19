#!/bin/bash
# Launch Willhiem from the repo folder using the local venv
# Run setup-dev.sh first if you haven't already

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ! -d "venv" ]]; then
    echo "Error: venv not found. Run ./setup-dev.sh first."
    exit 1
fi

exec venv/bin/python3 linux_tube_catcher.py "$@"
