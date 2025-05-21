"""
Configuration file for SRE-Jarvis CLI Tool.
Update these values according to your environment before running the tool.
"""

# ─────────────────────────────
# 🔐 AWS Configuration
# ─────────────────────────────
AWS_PROFILE = "your-AWS-profile-name"       # AWS Profile name 
AWS_REGION = "us-east-1"                    # AWS Region 

# ─────────────────────────────
# 🔑 EC2 SSH Configuration
# ─────────────────────────────
EC2_SSH_KEY_PATH = "/home/user/project/your-pem-file.pem"   # Path to your .pem key for SSH
EC2_INSTANCE_ID = "i-xxxxxxxxxxxxxxxxxxx"                   # EC2 Instance ID to connect

# ─────────────────────────────
# ☁️ S3 Configuration
# ─────────────────────────────
S3_BUCKET_NAME = "your-s3-bucket-name"     # S3 Bucket name for uploading heap dumps/logs

