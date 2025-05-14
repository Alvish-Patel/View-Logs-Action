import boto3
import paramiko
from rich.console import Console
from rich.prompt import Prompt
from botocore.exceptions import ProfileNotFound
import os
import configparser

console = Console()

# 🔸 Reusable AWS profile logic from restart.py

def list_existing_profiles():
    credentials_config = configparser.ConfigParser()
    credentials_config.read(os.path.expanduser("~/.aws/credentials"))

    config_config = configparser.ConfigParser()
    config_config.read(os.path.expanduser("~/.aws/config"))

    valid_profiles = []
    for profile in credentials_config.sections():
        config_section = f"profile {profile}" if profile != "default" else "default"
        if config_section in config_config and "region" in config_config[config_section]:
            valid_profiles.append(profile)
    return valid_profiles

def prompt_for_aws_configuration():
    console.print("\n[red]❌ AWS credentials or region not found. Please configure them first.[/red]")
    profile_name = Prompt.ask("Enter a profile name (e.g. dev, prod)").strip()
    aws_access_key_id = Prompt.ask("Enter AWS Access Key ID").strip()
    aws_secret_access_key = Prompt.ask("Enter AWS Secret Access Key").strip()
    aws_region = Prompt.ask("Enter AWS Region (e.g. us-west-2)").strip()

    aws_credentials_dir = os.path.expanduser("~/.aws")
    os.makedirs(aws_credentials_dir, exist_ok=True)

    credentials_path = os.path.join(aws_credentials_dir, "credentials")
    credentials_config = configparser.ConfigParser()
    credentials_config.read(credentials_path)
    credentials_config[profile_name] = {
        "aws_access_key_id": aws_access_key_id,
        "aws_secret_access_key": aws_secret_access_key
    }
    with open(credentials_path, "w") as f:
        credentials_config.write(f)

    config_path = os.path.join(aws_credentials_dir, "config")
    config = configparser.ConfigParser()
    config.read(config_path)
    config[f"profile {profile_name}"] = {"region": aws_region}
    with open(config_path, "w") as f:
        config.write(f)

    console.print("\n[green]✅ AWS credentials and region have been configured.[/green]")
    input("Press Enter to continue...")
    return profile_name

def choose_profile():
    profiles = list_existing_profiles()
    if profiles:
        console.print("\n[bold yellow]Available AWS Profiles:[/bold yellow]")
        for i, profile in enumerate(profiles, 1):
            console.print(f"  {i}. {profile}")
        choice = Prompt.ask("\nSelect AWS profile number or press Enter to add new AWS account").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(profiles):
            return profiles[int(choice) - 1]
        else:
            return prompt_for_aws_configuration()
    else:
        return prompt_for_aws_configuration()

# 🔸 Existing logic

def get_instances(profile):
    try:
        session = boto3.Session(profile_name=profile)
        ec2 = session.client("ec2")
        response = ec2.describe_instances()
        instances = []
        for resv in response["Reservations"]:
            for inst in resv["Instances"]:
                if inst["State"]["Name"] == "running":
                    name = "-"
                    for tag in inst.get("Tags", []):
                        if tag["Key"] == "Name":
                            name = tag["Value"]
                    instance_id = inst["InstanceId"]
                    instances.append((name, instance_id))
        return instances
    except ProfileNotFound:
        console.print(f"[red]❌ AWS profile '{profile}' not found.[/red]")
        return []

def ssh_and_fetch_logs(instance_ip, pem_file_path, log_path, user="ubuntu"):
    local_download_path = f"/tmp/{log_path.split('/')[-1]}"
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(instance_ip, username=user, key_filename=pem_file_path)
        console.print(f"[green]✅ Connected to {instance_ip}[/green]")

        # Fetch and print last 25 lines
        console.print(f"\n[cyan]🔍 Showing last 25 lines of:[/cyan] [bold]{log_path}[/bold]\n")
        stdin, stdout, stderr = ssh.exec_command(f"tail -n 25 {log_path}")
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            console.print(output)
        elif error:
            console.print(f"[red]❌ Error reading log file:[/red] {error.strip()}")
            return
        else:
            console.print("[yellow]⚠️ Log file is empty or path is incorrect.[/yellow]")
            return

        # Download full log
        ftp_client = ssh.open_sftp()
        ftp_client.get(log_path, local_download_path)
        ftp_client.close()
        ssh.close()

        console.print(f"\n[green]✅ Full log downloaded to: {local_download_path}[/green]")

    except paramiko.AuthenticationException as auth_error:
        console.print(f"[red]❌ Authentication failed.[/red] {auth_error}")
    except FileNotFoundError:
        console.print(f"[red]❌ Log file not found: {log_path}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error during SSH or file download:[/red] {e}")

def run():
    console.print("[bold yellow]📜 AWS Profile Setup[/bold yellow]")
    profile = choose_profile()

    instances = get_instances(profile)
    if not instances:
        console.print("[red]No running EC2 instances found.[/red]")
        return

    console.print("\n[bold cyan]Available Running EC2 Instances:[/bold cyan]")
    for idx, (name, instance_id) in enumerate(instances, start=1):
        console.print(f"{idx}. {name} ({instance_id})")

    instance_choice = Prompt.ask("\nSelect the instance number to fetch logs from")
    try:
        selected_instance = instances[int(instance_choice) - 1]
    except (ValueError, IndexError):
        console.print("[red]Invalid instance selection.[/red]")
        return

    _, instance_id = selected_instance
    session = boto3.Session(profile_name=profile)
    ec2 = session.resource("ec2")
    instance = ec2.Instance(instance_id)
    ip_address = instance.public_ip_address

    if not ip_address:
        console.print("[red]❌ Instance does not have a public IP address.[/red]")
        return

    pem_path = Prompt.ask("Enter path to the PEM key file")
    user = Prompt.ask("Enter the username (default: 'ubuntu')", default="ubuntu")
    log_path = Prompt.ask("Enter full log file path (e.g. /opt/atlassian/confluence/logs/atlassian-confluence.log)")

    ssh_and_fetch_logs(ip_address, pem_path, log_path, user)

if __name__ == "__main__":
    run()
