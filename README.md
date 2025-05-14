# SRE-Jarvis Project Setup on Ubuntu machine

## Prerequisites

Before starting the setup process, ensure you have the following:

## Step-by-Step Installation Guide

1. Make the setup.sh Script Executable:
Navigate to the project directory and ensure that the setup.sh script has execute permissions: 

## RUN THIS COMMAND --> chmod +x setup.sh

-----------------

2. Run the setup.sh Script:
Now, you can run the setup script to automatically install all the necessary dependencies and set up the environment: 

## RUN THIS COMMAND --> ./setup.sh

-----------------

3. Run the CLI Tool:
After running setup.sh, the main CLI tool (main.py) will automatically start. To run the tool manually at any point, use:

## RUN THIS COMMAND --> python3 main.py

----------------------------------------------------

# SRE-Jarvis Project Setup on Windows machine

## Prerequisites

Before starting the setup process, ensure you have the following installed:

-  Python 3 (add to PATH during installation)
-  PowerShell (comes pre-installed)

---

## Step-by-Step Installation Guide

### 1. Allow PowerShell Script Execution:

Run PowerShell **as Administrator** and enable script execution:

## RUN THIS COMMAND on powershell➜
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

-----------------

2. Run the setup.ps1 Script:
Now, you can run the setup script to automatically install all the necessary dependencies and set up the environment: 

## RUN THIS COMMAND --> .\setup.ps1

-----------------

3. Run the CLI Tool:
After running setup.ps1, the main CLI tool (main.py) will automatically start. To run the tool manually at any point, use:

## RUN THIS COMMAND --> python3 main.py