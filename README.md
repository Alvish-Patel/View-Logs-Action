# SRE-Jarvis CLI Tool

A powerful CLI tool to manage Confluence server operations like heap dumps, service restarts, and log viewing with ease and automation.

---

## Features

### ✅ Confluence Module

- **heapdump.py**  
  Captures heap dumps from remote Confluence EC2 instances for troubleshooting memory issues.

- **restart.py**  
  Restarts the Confluence service on remote EC2 instances to apply changes or recover from failures.

- **view_logs.py**  
  Fetches and displays Confluence logs remotely. Allows tailing logs or downloading full log files for analysis.

### Other Modules

- Module 2 Name  
- Module 3 Name  
- Module 4 Name  

---

## Prerequisites

- Python 3.8 or higher must be installed on your system.
- You must have SSH access and proper AWS profile setup to connect to EC2 instances remotely.

---

## Step-by-Step Installation Guide

### 1. Install Python

If you don't have Python installed on your system, install Python 3.8+ using the following commands:

```bash
sudo apt update
sudo apt install python3

### 2. Install pip (Python Package Installer)

If pip is not installed, Install pip to manage Python packages:

```bash
sudo apt install python3-pip

### 3. Install Dependencies

Once you have Python and pip ready, navigate to the project root folder and install the required dependencies: (cd /path/to/your/project/SRE-Jarvis)

```bash
pip install .

### 4. Run the CLI Tool

Run the main CLI entry point with:

```bash
python3 main.py


Ensure your AWS CLI profiles are properly configured for EC2 instance access.

Make sure you have the required SSH or .pem keys and permissions set up for remote connections.

### Configuration Setup (Optional)

Before running the tool, update the configuration file to match your environment.

Edit the `config.py` file located in the project root directory. Here's what each setting means:

### AWS Configuration

```python
AWS_PROFILE = "your-AWS-profile-name"     # Name of your AWS CLI profile 
AWS_REGION = "us-east-1"                  # AWS region where your EC2 
S3_BUCKET_NAME = "your-s3-bucket-name"     # Name of your S3 bucket for heap dump uploads

