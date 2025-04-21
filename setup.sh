#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get workspace root directory
WORKSPACE_ROOT=$(cd "$(dirname "$0")/.." && pwd)

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to ask user for confirmation
confirm() {
    read -p "$1 [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            echo "debian"
        elif [ -f /etc/redhat-release ]; then
            echo "redhat"
        else
            echo "unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Function to install Python
install_python() {
    local os_type=$(detect_os)
    echo -e "${YELLOW}Installing Python...${NC}"
    
    case $os_type in
        "debian")
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        "redhat")
            sudo yum install -y python3 python3-pip python3-devel
            ;;
        "macos")
            if command_exists brew; then
                brew install python
            else
                echo -e "${YELLOW}Installing Homebrew first...${NC}"
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                brew install python
            fi
            ;;
        *)
            echo -e "${RED}Unsupported operating system for automatic Python installation${NC}"
            echo -e "${YELLOW}Please install Python 3.8 or higher manually${NC}"
            exit 1
            ;;
    esac
}

# Function to install PostgreSQL
install_postgres() {
    local os_type=$(detect_os)
    echo -e "${YELLOW}Installing PostgreSQL...${NC}"
    
    case $os_type in
        "debian")
            sudo apt-get update
            sudo apt-get install -y postgresql postgresql-contrib
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
            ;;
        "redhat")
            sudo yum install -y postgresql-server postgresql-contrib
            sudo postgresql-setup --initdb
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
            ;;
        "macos")
            if command_exists brew; then
                brew install postgresql@16
                brew services start postgresql@16
            else
                echo -e "${YELLOW}Installing Homebrew first...${NC}"
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                brew install postgresql@16
                brew services start postgresql@16
            fi
            ;;
        *)
            echo -e "${RED}Unsupported operating system for automatic PostgreSQL installation${NC}"
            echo -e "${YELLOW}Please install PostgreSQL manually${NC}"
            exit 1
            ;;
    esac

    # Setup PostgreSQL user for Odoo
    echo -e "${YELLOW}Setting up PostgreSQL user for Odoo...${NC}"
    case $os_type in
        "debian"|"redhat")
            sudo -u postgres createuser -s odoo 2>/dev/null || true
            sudo -u postgres psql -c "ALTER USER odoo WITH PASSWORD '123';" 2>/dev/null || true
            ;;
        "macos")
            createuser -s odoo 2>/dev/null || true
            psql postgres -c "ALTER USER odoo WITH PASSWORD '123';" 2>/dev/null || true
            ;;
    esac
}

# Function to install Git
install_git() {
    local os_type=$(detect_os)
    echo -e "${YELLOW}Installing Git...${NC}"
    
    case $os_type in
        "debian")
            sudo apt-get update
            sudo apt-get install -y git
            ;;
        "redhat")
            sudo yum install -y git
            ;;
        "macos")
            if command_exists brew; then
                brew install git
            else
                echo -e "${YELLOW}Installing Homebrew first...${NC}"
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                brew install git
            fi
            ;;
        *)
            echo -e "${RED}Unsupported operating system for automatic Git installation${NC}"
            echo -e "${YELLOW}Please install Git manually${NC}"
            exit 1
            ;;
    esac
}

# Function to check Git
check_git() {
    if command_exists git; then
        return 0
    else
        return 1
    fi
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$MAJOR" -gt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 8 ]); then
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}

# Function to check PostgreSQL
check_postgres() {
    if command_exists psql; then
        return 0
    else
        return 1
    fi
}

# Function to check required directories
check_directories() {
    local missing_dirs=()

    if [ ! -d "$WORKSPACE_ROOT/odoo" ]; then
        missing_dirs+=("odoo")
    fi

    if [ ! -d "$WORKSPACE_ROOT/enterprise" ]; then
        missing_dirs+=("enterprise")
    fi

    if [ ${#missing_dirs[@]} -ne 0 ]; then
        echo -e "${RED}Error: Required directories not found:${NC}"
        for dir in "${missing_dirs[@]}"; do
            echo -e "${YELLOW}- $dir${NC}"
        done
        echo -e "${YELLOW}Please ensure both 'odoo' and 'enterprise' directories are present in:${NC}"
        echo -e "${YELLOW}$WORKSPACE_ROOT${NC}"
        exit 1
    fi
}

# Function to install Python dependencies
install_python_deps() {
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    # Dependencies are now installed by install_dependencies.sh
    return 0
}

# Function to create aliases
create_aliases() {
    local shell_rc
    # Properly escape paths and commands for zsh
    local alias_cmd1="alias pisa=\"source '$WORKSPACE_ROOT/.venv/bin/activate' && cd '$WORKSPACE_ROOT/pisa-addons' && ./run.sh\""
    local alias_cmd2="alias pisa-debug=\"source '$WORKSPACE_ROOT/.venv/bin/activate' && cd '$WORKSPACE_ROOT/pisa-addons' && ./run.sh --debug\""
    
    # Detect shell and set appropriate rc file
    if [[ "$SHELL" == *"zsh"* ]]; then
        shell_rc="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        shell_rc="$HOME/.bashrc"
    else
        echo -e "${YELLOW}Unsupported shell: $SHELL${NC}"
        echo -e "${YELLOW}Please add the following aliases manually to your shell configuration:${NC}"
        echo -e "${GREEN}$alias_cmd1${NC}"
        echo -e "${GREEN}$alias_cmd2${NC}"
        return 1
    fi

    # Check if aliases already exist
    if grep -q "alias pisa=" "$shell_rc" && grep -q "alias pisa-debug=" "$shell_rc"; then
        echo -e "${GREEN}Aliases already exist in $shell_rc${NC}"
        # Remove existing aliases to replace them
        sed -i '' '/# PISA Addons aliases/,/^$/d' "$shell_rc"
    fi

    echo -e "\n${BLUE}Would you like to create aliases in $shell_rc?${NC}"
    if confirm "This will add 'pisa' and 'pisa-debug' commands to your shell"; then
        echo -e "\n# PISA Addons aliases" >> "$shell_rc"
        echo "$alias_cmd1" >> "$shell_rc"
        echo "$alias_cmd2" >> "$shell_rc"
        echo -e "${GREEN}Aliases added to $shell_rc${NC}"
        
        # Source the shell configuration file
        echo -e "${YELLOW}Refreshing shell configuration...${NC}"
        if [[ "$SHELL" == *"zsh"* ]]; then
            source "$shell_rc"
        elif [[ "$SHELL" == *"bash"* ]]; then
            source "$shell_rc"
        fi
        echo -e "${GREEN}Shell configuration refreshed! You can now use 'pisa' and 'pisa-debug' commands.${NC}"
    else
        echo -e "\n${YELLOW}To add aliases manually, add these lines to your shell configuration:${NC}"
        echo -e "${GREEN}$alias_cmd1${NC}"
        echo -e "${GREEN}$alias_cmd2${NC}"
    fi
}

# Function to check and clone Odoo Community
check_and_clone_odoo() {
    local workspace_root=$(cd "$(dirname "$0")/.." && pwd)
    local odoo_dir="$workspace_root/odoo"
    
    if [ ! -d "$odoo_dir" ]; then
        echo -e "${YELLOW}Odoo Community repository not found.${NC}"
        if confirm "Would you like to clone Odoo Community repository?"; then
            echo -e "${YELLOW}Cloning Odoo Community repository...${NC}"
            if git clone https://github.com/odoo/odoo.git "$odoo_dir"; then
                echo -e "${GREEN}Successfully cloned Odoo Community repository${NC}"
                
                # Checkout version 18.0
                echo -e "${YELLOW}Checking out version 18.0...${NC}"
                cd "$odoo_dir" && git checkout 18.0 && cd - > /dev/null
                echo -e "${GREEN}Successfully checked out version 18.0${NC}"
            else
                echo -e "${RED}Failed to clone Odoo Community repository${NC}"
                echo -e "${YELLOW}Please clone it manually:${NC}"
                echo -e "${GREEN}git clone https://github.com/odoo/odoo.git $odoo_dir${NC}"
                echo -e "${GREEN}cd $odoo_dir && git checkout 18.0${NC}"
                exit 1
            fi
        else
            echo -e "${YELLOW}Please clone Odoo Community repository manually:${NC}"
            echo -e "${GREEN}git clone https://github.com/odoo/odoo.git $odoo_dir${NC}"
            echo -e "${GREEN}cd $odoo_dir && git checkout 18.0${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}Odoo Community repository found.${NC}"
        
        # Check if it's version 18.0
        cd "$odoo_dir"
        if ! git branch --show-current | grep -q "18.0"; then
            echo -e "${YELLOW}Current branch is not 18.0.${NC}"
            if confirm "Would you like to checkout version 18.0?"; then
                if git checkout 18.0; then
                    echo -e "${GREEN}Successfully checked out version 18.0${NC}"
                else
                    echo -e "${RED}Failed to checkout version 18.0${NC}"
                    echo -e "${YELLOW}Please checkout manually:${NC}"
                    echo -e "${GREEN}cd $odoo_dir && git checkout 18.0${NC}"
                    exit 1
                fi
            else
                echo -e "${YELLOW}Please checkout version 18.0 manually:${NC}"
                echo -e "${GREEN}cd $odoo_dir && git checkout 18.0${NC}"
                exit 1
            fi
        fi
        cd - > /dev/null
    fi
}

# Check Git
echo -e "${YELLOW}Checking Git installation...${NC}"
if ! check_git; then
    echo -e "${RED}Git is required but not found.${NC}"
    if confirm "Would you like to install Git?"; then
        install_git
        if ! check_git; then
            echo -e "${RED}Git installation failed. Please install Git manually.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Please install Git and run this script again.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Git found.${NC}"
fi

# Check Python
echo -e "${YELLOW}Checking Python installation...${NC}"
if ! check_python_version; then
    echo -e "${RED}Python 3.8 or higher is required but not found.${NC}"
    if confirm "Would you like to install Python 3.8 or higher?"; then
        install_python
        if ! check_python_version; then
            echo -e "${RED}Python installation failed. Please install Python 3.8 or higher manually.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Please install Python 3.8 or higher and run this script again.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Python version $PYTHON_VERSION found.${NC}"
fi

# Check PostgreSQL
echo -e "${YELLOW}Checking PostgreSQL installation...${NC}"
if ! check_postgres; then
    echo -e "${RED}PostgreSQL is required but not found.${NC}"
    if confirm "Would you like to install PostgreSQL?"; then
        install_postgres
        if ! check_postgres; then
            echo -e "${RED}PostgreSQL installation failed. Please install PostgreSQL manually.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Please install PostgreSQL and run this script again.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}PostgreSQL found.${NC}"
fi

# Check required directories
echo -e "${YELLOW}Checking required directories...${NC}"
check_directories

# Check and clone Odoo Community if needed
check_and_clone_odoo

# Create .vscode directory if it doesn't exist
echo -e "${YELLOW}Creating VS Code configuration...${NC}"
mkdir -p "$WORKSPACE_ROOT/.vscode"

# Create launch.json
cat > "$WORKSPACE_ROOT/.vscode/launch.json" << 'EOL'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "pisa",
            "type": "debugpy",
            "request": "launch",
            "stopOnEntry": false,
            "python": "${command:python.interpreterPath}",
            "program": "${workspaceRoot}/odoo/odoo-bin",
            "args": [
                "--config=${workspaceRoot}/odoo.conf",
                "-u", "all"
            ],
            "cwd": "${workspaceRoot}",
            "envFile": "${workspaceRoot}/.env"
        }
    ]
}
EOL

# Create odoo.conf with absolute paths
cat > "$WORKSPACE_ROOT/odoo.conf" << EOL
[options]
db_host = localhost
db_port = 5432
db_user = odoo
db_password = 123
addons_path = $WORKSPACE_ROOT/odoo/addons,$WORKSPACE_ROOT/enterprise,$WORKSPACE_ROOT/pisa-addons
admin_passwd = your_admin_password
EOL

# Make install_dependencies.sh executable
chmod +x "$(dirname "$0")/install_dependencies.sh"

# Run dependencies installation
echo -e "${YELLOW}Installing project dependencies...${NC}"
if "$(dirname "$0")/install_dependencies.sh"; then
    echo -e "${GREEN}Dependencies installed successfully!${NC}"
else
    echo -e "${RED}Failed to install dependencies. Please check the error messages above.${NC}"
    exit 1
fi

echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${YELLOW}Please update the database credentials in odoo.conf if needed.${NC}"

# Ask to activate virtual environment
echo -e "\n${BLUE}Would you like to activate the virtual environment now?${NC}"
if confirm "This will modify your shell session"; then
    echo -e "\n${GREEN}Activating virtual environment...${NC}"
    source "$WORKSPACE_ROOT/.venv/bin/activate"
    echo -e "${GREEN}Virtual environment activated!${NC}"
else
    echo -e "\n${YELLOW}To activate the virtual environment later, run:${NC}"
    echo -e "${GREEN}source $WORKSPACE_ROOT/.venv/bin/activate${NC}"
fi

# Create aliases
create_aliases

echo -e "\n${BLUE}Next steps:${NC}"
echo -e "1. Update database credentials in ${YELLOW}odoo.conf${NC} if needed"
echo -e "2. Make sure virtual environment is activated (you should see ${GREEN}(venv)${NC} in your prompt)"
echo -e "3. Run ${YELLOW}./run.sh${NC} to start Odoo in normal mode"
echo -e "4. Run ${YELLOW}./run.sh --debug${NC} to start Odoo in debug mode" 