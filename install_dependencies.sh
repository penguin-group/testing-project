#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to get Odoo path from odoo.conf
get_odoo_path() {
    local workspace_root=$(cd "$(dirname "$0")/.." && pwd)
    local odoo_conf="$workspace_root/odoo.conf"
    
    if [ ! -f "$odoo_conf" ]; then
        echo -e "${RED}Error: odoo.conf not found. Run setup.sh first.${NC}"
        exit 1
    fi

    # Get the first path from addons_path that contains 'odoo'
    local odoo_path=$(grep "addons_path" "$odoo_conf" | cut -d'=' -f2 | tr ',' '\n' | grep "odoo" | head -n1 | sed 's|/addons||' | tr -d ' ')
    echo "$odoo_path"
}

# Function to create and activate virtual environment
setup_venv() {
    local workspace_root=$(cd "$(dirname "$0")/.." && pwd)
    local venv_path="$workspace_root/.venv"

    echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
    
    # Check if python3 -m venv is available
    if ! python3 -m venv --help > /dev/null 2>&1; then
        echo -e "${RED}Error: python3-venv is not installed${NC}"
        echo -e "${YELLOW}Please install it with: sudo apt-get install python3-venv${NC}"
        exit 1
    fi

    # Create venv if it doesn't exist
    if [ ! -d "$venv_path" ]; then
        echo -e "${YELLOW}Creating virtual environment in $venv_path${NC}"
        if ! python3 -m venv "$venv_path"; then
            echo -e "${RED}Failed to create virtual environment${NC}"
            exit 1
        fi
    fi

    # Activate venv
    echo -e "${YELLOW}Activating virtual environment${NC}"
    source "$venv_path/bin/activate"

    # Upgrade pip
    echo -e "${YELLOW}Upgrading pip...${NC}"
    pip install --upgrade pip

    echo -e "${GREEN}Virtual environment is ready${NC}"
}

# Function to install requirements
install_requirements() {
    local req_file="$1"
    local desc="$2"

    if [ -f "$req_file" ]; then
        echo -e "${YELLOW}Installing $desc requirements...${NC}"
        if pip install -r "$req_file"; then
            echo -e "${GREEN}Successfully installed $desc requirements${NC}"
        else
            echo -e "${RED}Failed to install $desc requirements${NC}"
            return 1
        fi
    else
        echo -e "${RED}Error: $req_file not found${NC}"
        return 1
    fi
}

# Function to install debug dependencies
install_debug_deps() {
    echo -e "${YELLOW}Installing debug dependencies...${NC}"
    if pip install debugpy; then
        echo -e "${GREEN}Successfully installed debugpy${NC}"
    else
        echo -e "${RED}Failed to install debugpy${NC}"
        return 1
    fi
}

# Main installation process
main() {
    echo -e "${YELLOW}Starting dependencies installation...${NC}"

    # Setup and activate virtual environment
    setup_venv

    # Install debug dependencies
    install_debug_deps

    # Get Odoo path
    ODOO_PATH=$(get_odoo_path)
    if [ -z "$ODOO_PATH" ]; then
        echo -e "${RED}Error: Could not find Odoo path in odoo.conf${NC}"
        exit 1
    fi
    echo -e "${GREEN}Found Odoo path: $ODOO_PATH${NC}"

    # Install Odoo requirements
    ODOO_REQ="$ODOO_PATH/requirements.txt"
    install_requirements "$ODOO_REQ" "Odoo"

    # Install PISA addons requirements
    PISA_REQ="$(dirname "$0")/requirements.txt"
    install_requirements "$PISA_REQ" "PISA addons"

    echo -e "${GREEN}All dependencies installation completed!${NC}"
    echo -e "${YELLOW}To activate this virtual environment, run:${NC}"
    echo -e "${GREEN}source ../.venv/bin/activate${NC}"
}

# Run main function
main 