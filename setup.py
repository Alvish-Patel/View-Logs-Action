import sys
import subprocess
from setuptools import setup, find_packages
from pathlib import Path

# Check if Python is installed
def check_python():
    if sys.version_info < (3, 8):
        print("Python 3.8 or higher is required. Please install it.")
        sys.exit(1)

check_python()

# Read the README file
this_directory = Path(__file__).parent
long_description = ""
readme_path = this_directory / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name='sre-jarvis',
    version='1.0.0',
    author='Alvish',
    description='A CLI tool for SRE automation tasks like heapdump capture, service restart, log viewing, etc.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=[".venv", "tests*", "scripts"]),
    include_package_data=True,
    install_requires=[
        'boto3',
        'paramiko',
        'scp',
        'rich',
        'questionary'
    ],
    entry_points={
        'console_scripts': [
            'sre-jarvis=main:main'  # Ensure main.py has def main(): ...
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)

# Check if pip is installed, and install if necessary
def check_pip():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
    except subprocess.CalledProcessError:
        print("pip is not installed. Installing pip...")
        subprocess.check_call([sys.executable, "-m", "ensurepip"])

check_pip()
