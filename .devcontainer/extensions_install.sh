#!/bin/bash
# Install VSIX extensions from .plugins folder
# This script installs VSIX files that were downloaded during container initialization

PLUGINS_DIR=".plugins"

if [ ! -d "$PLUGINS_DIR" ]; then
    echo "Warning: .plugins directory not found. Run container initialization first."
    exit 0
fi

# Function to install a VSIX file if it exists
install_vsix() {
    local vsix_file="$1"
    local display_name="$2"
    
    if [ -f "$vsix_file" ]; then
        if [ ! -s "$vsix_file" ]; then
            echo "Warning: $display_name file is empty, skipping installation"
            return 1
        fi
        
        # Check file type - VSIX files should start with "PK" (zip signature)
        FILE_HEADER=$(head -c 2 "$vsix_file" 2>/dev/null)
        if [ "$FILE_HEADER" != "PK" ]; then
            echo "Warning: $display_name is not a valid VSIX (zip) file, skipping installation"
            return 1
        fi
        
        # Verify it's a valid zip file
        if ! unzip -t "$vsix_file" > /dev/null 2>&1; then
            echo "Warning: $display_name failed zip validation, skipping installation"
            return 1
        fi
        
        echo "Installing $display_name..."
        if code --install-extension "$vsix_file" --force; then
            echo "$display_name installed successfully."
            return 0
        else
            echo "Error: Failed to install $display_name"
            return 1
        fi
    else
        echo "Warning: $display_name not found at $vsix_file, skipping installation"
        return 1
    fi
}

# Install AgentForce Assistant Universal VSIX
install_vsix "$PLUGINS_DIR/agentforce-assistant-universal.vsix" "AgentForce Assistant Universal"

# Install Qbrix Dev Plugin Universal VSIX
install_vsix "$PLUGINS_DIR/qbrixdev-vscode-universal.vsix" "Qbrix Dev Plugin Universal"

echo "Extension installation complete."

