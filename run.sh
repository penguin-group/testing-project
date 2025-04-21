#!/bin/bash

# Function to show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -d, --debug    Run in debug mode"
    echo "  -h, --help     Show this help message"
}

# Default values
DEBUG_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--debug)
            DEBUG_MODE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Get the workspace root directory (parent of pisa-addons)
WORKSPACE_ROOT=$(cd "$(dirname "$0")/.." && pwd)

if [ "$DEBUG_MODE" = true ]; then
    echo "Starting Odoo in debug mode..."
    # Run with debugpy
    python -m debugpy --listen 5678 $WORKSPACE_ROOT/odoo/odoo-bin --config=$WORKSPACE_ROOT/odoo.conf
else
    echo "Starting Odoo in normal mode..."
    # Run normally
    python $WORKSPACE_ROOT/odoo/odoo-bin --config=$WORKSPACE_ROOT/odoo.conf
fi 