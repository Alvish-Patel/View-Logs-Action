import boto3
import logging
import botocore
import os
import configparser
from rich.console import Console
from rich.prompt import Prompt

console = Console()


def setup_logging(log_file_path=None):
    if not log_file_path:
        log_file_path = os.path.expanduser("~/.sre-jarvis/logs/restart.log")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )


def list_existing_profiles():
    credentials_path = os.path.expanduser("~/.aws/credentials")
    config_path = os.path.expanduser("~/.aws/config")

    credentials_config = configparser.ConfigParser()
    credentials_config.read(credentials_path)

    config_config = configparser.ConfigParser()
    config_config.read(config_path)

    valid_profiles = []
    for profile in credentials_config.sections():
        config_section = f"profile {profile}" if profile != "default" else "default"
        if config_section in config_config and "region" in config_config[config_section]:
            valid_profiles.append(profile)
    return valid_profiles


def prompt_for_aws_configuration():
    console.print("\n[red]❌ AWS credentials or region not found. Please configure them first.[/red]")
    profile_name = Prompt.ask("Enter a profile name for this configuration (e.g., dev, prod)").strip()
    aws_access_key_id = Prompt.ask("Enter AWS Access Key ID").strip()
    aws_secret_access_key = Prompt.ask("Enter AWS Secret Access Key").strip()
    aws_region = Prompt.ask("Enter AWS Region (e.g., us-west-2)").strip()

    aws_dir = os.path.expanduser("~/.aws")
    os.makedirs(aws_dir, exist_ok=True)

    credentials_path = os.path.join(aws_dir, "credentials")
    config_path = os.path.join(aws_dir, "config")

    credentials_config = configparser.ConfigParser()
    credentials_config.read(credentials_path)
    credentials_config[profile_name] = {
        "aws_access_key_id": aws_access_key_id,
        "aws_secret_access_key": aws_secret_access_key
    }
    with open(credentials_path, "w") as f:
        credentials_config.write(f)

    config_config = configparser.ConfigParser()
    config_config.read(config_path)
    config_config[f"profile {profile_name}"] = {"region": aws_region}
    with open(config_path, "w") as f:
        config_config.write(f)

    console.print("\n[green]✅ AWS credentials and region have been configured.[/green]")
    input("Press Enter to continue...")
    return profile_name


def choose_profile():
    profiles = list_existing_profiles()
    if profiles:
        console.print("\n[bold yellow]📜 Available AWS Profiles[/bold yellow]")
        for i, profile in enumerate(profiles, 1):
            console.print(f"  {i}. {profile}")
        choice = Prompt.ask("\nSelect a profile number or press Enter to configure a new one").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(profiles):
            return profiles[int(choice) - 1]
        return prompt_for_aws_configuration()
    return prompt_for_aws_configuration()


def restart_all_confluence_instances(profile_name, tag_value="confluence"):
    logging.info(f"Selected AWS Profile: {profile_name}")
    logging.info(f"Instance tag filter: {tag_value}")
    try:
        config_path = os.path.expanduser("~/.aws/config")
        config = configparser.ConfigParser()
        config.read(config_path)
        region = config.get(f"profile {profile_name}", "region", fallback=None)

        if not region:
            raise ValueError("Region is not set for this profile in the AWS config file.")

        session = boto3.Session(profile_name=profile_name, region_name=region)
        ec2 = session.client("ec2")

        response = ec2.describe_instances(
            Filters=[
                {"Name": "tag:Name", "Values": [f"*{tag_value}*"]},
                {"Name": "instance-state-name", "Values": ["running"]}
            ]
        )

        instances = [
            {
                "id": instance["InstanceId"],
                "name": next((tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"), "Unnamed")
            }
            for reservation in response["Reservations"]
            for instance in reservation["Instances"]
        ]

        if not instances:
            logging.warning(f"No running EC2 instances found with tag containing '{tag_value}'")
            console.print(f"[red]❌ No running EC2 instances found with tag matching: {tag_value}[/red]")
            return

        for instance in instances:
            instance_id = instance["id"]
            instance_name = instance["name"]

            logging.info(f"Restarting instance: {instance_name} ({instance_id})")
            console.print(f"\n[bold cyan]🔁 Restarting:[/bold cyan] [yellow]{instance_name}[/yellow] ([green]{instance_id}[/green])")

            ec2.reboot_instances(InstanceIds=[instance_id])

            logging.info(f"Waiting for {instance_name} to pass health checks...")
            console.print(f"[magenta]⏳ Waiting for {instance_name} to pass health checks...[/magenta]")
            waiter = ec2.get_waiter('instance_status_ok')
            waiter.wait(InstanceIds=[instance_id])

            logging.info(f"{instance_name} is healthy.")
            console.print(f"[green]✅ {instance_name} is now healthy and running.[/green]")

        logging.info("All instances restarted successfully.")
        console.print("\n[bold green]✅ All EC2 instances restarted and verified.[/bold green]")

    except botocore.exceptions.BotoCoreError as e:
        logging.error(f"AWS SDK Error: {str(e)}")
        console.print(f"[red]❌ AWS SDK error:[/red] {str(e)}")
    except ValueError as e:
        logging.error(f"Configuration error: {str(e)}")
        console.print(f"[red]❌ {str(e)}[/red]")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        console.print(f"[red]❌ Error: {str(e)}[/red]")

    input("\nPress Enter to return to the submenu...")


def run():
    setup_logging()
    console.print("[bold yellow]📜 AWS Profile Setup[/bold yellow]")
    profile_name = choose_profile()
    console.print("\n[bold cyan]🔁 Restart Confluence EC2 Instances[/bold cyan]")
    tag_value = Prompt.ask("Enter tag value or part of instance name", default="confluence").strip()
    restart_all_confluence_instances(profile_name, tag_value)


if __name__ == "__main__":
    run()
