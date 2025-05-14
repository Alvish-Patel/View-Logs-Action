#!/bin/bash

echo "🚀 Starting SRE-Jarvis environment setup..."

# Check if Python is installed
if ! command -v python3 &>/dev/null; then
    echo "❌ Python3 is not installed. Installing Python3..."
    sudo apt install -y python3 python3-pip
else
    echo "✅ Python3 is already installed."
fi

# Check if AWS CLI is installed
if ! command -v aws &>/dev/null; then
    echo "❌ AWS CLI is not installed. Installing AWS CLI..."
    sudo apt install -y awscli
else
    echo "✅ AWS CLI is already installed."
fi

# Install other required system tools
echo "🧰 Installing required system tools..."
sudo apt install -y default-jdk unzip

# Confirm Java & jmap installation
echo "☕ Checking Java and jmap..."
java -version
which jmap

# Upgrade pip and install virtualenv
echo "📦 Setting up Python environment..."
python3 -m pip install --upgrade pip
pip3 install --user virtualenv

# Create a virtual environment if it doesn't exist
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "📁 Creating Python virtual environment..."
  python3 -m virtualenv $VENV_DIR
fi

# Activate the virtual environment
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

# 🔽 Create a requirements.txt file dynamically
# This ensures fresh install without needing to commit this file
cat > requirements.txt <<EOF
boto3
botocore
rich
paramiko
scp
EOF

echo "📄 Generated fresh requirements.txt file."

# Install dependencies from requirements.txt
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Show installed packages
echo "✅ Installed Python packages:"
pip list

# Run main CLI tool
echo "🎮 Launching SRE-Jarvis CLI..."
python3 main.py
