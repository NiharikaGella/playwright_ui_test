#!/bin/bash
# Setup script for CI/CD Ubuntu Agent
# This script creates a Python virtual environment and installs all dependencies
# including Playwright browsers

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    printf "${GREEN}[INFO]${NC} %s\n" "$1"
}

print_error() {
    printf "${RED}[ERROR]${NC} %s\n" "$1"
}

print_warning() {
    printf "${YELLOW}[WARNING]${NC} %s\n" "$1"
}

# Check if Python is installed
print_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed. Please install Python 3.12 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_info "Python version: $PYTHON_VERSION"

# Extract major.minor version (e.g., 3.12 from 3.12.3)
PYTHON_VERSION_SHORT=$(echo $PYTHON_VERSION | cut -d'.' -f1,2)

# Create virtual environment if it doesn't exist
VENV_DIR=".venv"
if [ -d "$VENV_DIR" ]; then
    print_warning "Virtual environment already exists at $VENV_DIR. Removing it..."
    rm -rf "$VENV_DIR"
fi

print_info "Creating Python virtual environment..."
if ! python3 -m venv "$VENV_DIR" 2>/dev/null; then
    print_warning "Failed to create venv. Attempting to install python3-venv..."
    
    # Try installing without sudo first (in case running as root)
    print_info "Attempting to install python3-venv for Python ${PYTHON_VERSION_SHORT}..."
    if apt-get update -qq 2>/dev/null && apt-get install -y python${PYTHON_VERSION_SHORT}-venv python3-pip 2>/dev/null; then
        print_info "Successfully installed python3-venv (without sudo)"
    elif command -v sudo &> /dev/null; then
        # Try with sudo if available
        print_info "Trying with sudo..."
        sudo apt-get update -qq || true
        sudo apt-get install -y python${PYTHON_VERSION_SHORT}-venv python3-pip || {
            print_warning "Failed to install python${PYTHON_VERSION_SHORT}-venv, trying generic python3-venv..."
            sudo apt-get install -y python3-venv python3-pip || {
                print_error "Failed to install python3-venv"
                exit 1
            }
        }
        print_info "Successfully installed python3-venv"
    else
        # Neither method worked
        print_error "==========================================================="
        print_error "Unable to install python3-venv automatically."
        print_error "Please add this as a SEPARATE TASK in your Classic Release Pipeline:"
        print_error ""
        print_error "Task: Bash"
        print_error "Display Name: Install System Dependencies"
        print_error "Script:"
        print_error "  apt-get update -qq"
        print_error "  apt-get install -y python${PYTHON_VERSION_SHORT}-venv python3-pip"
        print_error ""
        print_error "Place this task BEFORE the 'Install Python and Playwright Dependencies' task"
        print_error "==========================================================="
        exit 1
    fi
    
    # Try creating venv again
    print_info "Retrying virtual environment creation..."
    python3 -m venv "$VENV_DIR" || {
        print_error "Failed to create virtual environment after installing python3-venv"
        exit 1
    }
fi
print_info "Virtual environment created successfully"

# Activate virtual environment
print_info "Activating virtual environment..."
source "$VENV_DIR/bin/activate" || {
    print_error "Failed to activate virtual environment"
    exit 1
}

# Verify we're in the virtual environment
print_info "Virtual environment activated: $(which python3)"

# Upgrade pip in virtual environment
print_info "Upgrading pip in virtual environment..."
python3 -m pip install --upgrade pip || {
    print_error "Failed to upgrade pip in virtual environment"
    exit 1
}

# Install wheel and setuptools for better compatibility
print_info "Installing wheel and setuptools..."
pip install --upgrade wheel setuptools || {
    print_warning "Failed to install wheel and setuptools, continuing..."
}

# Install requirements from requirements.txt
print_info "Installing Python dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt || {
        print_error "Failed to install requirements from requirements.txt"
        exit 1
    }
    print_info "Successfully installed Python dependencies"
else
    print_error "requirements.txt not found in current directory"
    exit 1
fi

# Install Playwright browsers with system dependencies
print_info "Installing Playwright browsers with system dependencies..."
# The --with-deps flag installs system dependencies required for browsers
playwright install --with-deps || {
    print_error "Failed to install Playwright browsers"
    exit 1
}
print_info "Successfully installed Playwright browsers"

# Verify Playwright installation
print_info "Verifying Playwright installation..."
python3 -c "from playwright.sync_api import sync_playwright; print('Playwright import successful')" || {
    print_error "Playwright verification failed"
    exit 1
}

# Display installed packages
print_info "Installed packages:"
pip list

print_info "============================================"
print_info "Setup completed successfully!"
print_info "============================================"
print_info "Virtual environment: $VENV_DIR"
print_info "To activate manually, run: source $VENV_DIR/bin/activate"
print_info "============================================"

exit 0
