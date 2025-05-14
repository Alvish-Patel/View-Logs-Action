# PowerShell script to set up SRE-Jarvis environment on Windows

Write-Host "Starting SRE-Jarvis environment setup..."

# Check if Python is installed
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "Python is not installed. Please install it from https://www.python.org/downloads/"
    exit
} else {
    Write-Host "Python is installed."
}

# Check if pip is installed
$pipPath = Get-Command pip -ErrorAction SilentlyContinue
if (-not $pipPath) {
    Write-Host "pip is not installed. Installing pip..."
    python -m ensurepip --upgrade
} else {
    Write-Host "pip is already installed."
}

# Check if AWS CLI is installed
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "AWS CLI is not installed. Installing via pip..."
    pip install awscli
} else {
    Write-Host "AWS CLI is already installed."
}

# Set up virtual environment
$venvDir = ".venv"
if (-not (Test-Path $venvDir)) {
    Write-Host "Creating virtual environment..."
    python -m venv $venvDir
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
. .\.venv\Scripts\Activate.ps1

# Create requirements.txt
Write-Host "Creating requirements.txt file..."
@"
boto3
botocore
rich
paramiko
scp
"@ | Set-Content -Encoding UTF8 -Path requirements.txt

# Install Python dependencies
Write-Host "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Show installed packages
Write-Host "Installed Python packages:"
pip list

# Launch CLI
Write-Host "Launching SRE-Jarvis CLI..."
python main.py
