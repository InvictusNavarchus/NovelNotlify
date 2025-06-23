#!/bin/bash

# Script to setup ecosystem.config.js from example
# This script copies the example config and updates the Python binary path

set -e  # Exit on any error

# Get the absolute path of the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define file paths
EXAMPLE_CONFIG="$SCRIPT_DIR/ecosystem.config.example.js"
TARGET_CONFIG="$SCRIPT_DIR/ecosystem.config.js"
PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"

echo "Setting up ecosystem.config.js..."

# Check if example config exists
if [ ! -f "$EXAMPLE_CONFIG" ]; then
    echo "Error: ecosystem.config.example.js not found!"
    exit 1
fi

# Check if virtual environment exists
if [ ! -f "$PYTHON_BIN" ]; then
    echo "Error: Python binary not found at $PYTHON_BIN"
    echo "Make sure the virtual environment is created with 'uv venv'"
    exit 1
fi

# Copy example to target config
cp "$EXAMPLE_CONFIG" "$TARGET_CONFIG"
echo "Copied ecosystem.config.example.js to ecosystem.config.js"

# Replace the script path with the absolute Python binary path
# Using sed to replace the placeholder with the actual path
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS sed syntax
    sed -i '' "s|script : \"./venv/bin/python\"|script : \"$PYTHON_BIN\"|g" "$TARGET_CONFIG"
else
    # Linux sed syntax
    sed -i "s|script : \"./venv/bin/python\"|script : \"$PYTHON_BIN\"|g" "$TARGET_CONFIG"
fi

echo "Updated Python binary path to: $PYTHON_BIN"
echo "✅ ecosystem.config.js is ready!"
echo ""
echo "You can now start the application with:"
echo "pm2 start ecosystem.config.js"
