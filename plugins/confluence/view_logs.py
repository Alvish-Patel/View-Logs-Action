import boto3
import sys
import os
import paramiko
from paramiko import SSHClient, AutoAddPolicy, ProxyCommand
from rich.console import Console

console = Console()

# Define common log paths for different services
LOG_PATHS = {
    "Confluence": [
        "/opt/Confluence/logs/catalina.out",
        "/var/log/confluence/confluence.log",
        "/var/log/messages",
    ],
    "Jira": [
        "/opt/Jira/logs/atlassian-jira.log",
        "/var/log/jira/jira.log",
    ],
    "Custom": []  # Allows users to specify a custom log path
}


def choose_aws_profile():
    session = boto3.Session()
    profiles = session.available_profiles
    if not profiles:
        console.print("[red]No AWS profiles found! Configure AWS CLI profiles first.[/red]")
        sys.exit(1)

    print("\n📜 AWS Profile Setup\n")
    print("Available AWS Profiles:")
    for idx, profile in enumerate(profiles, 1):
        print(f"  {idx}. {profile}")
    print()
    choice = input("Select AWS profile number or press Enter to add new AWS account: ").strip()

    if choice == "":
        console.print("[yellow]Add new AWS account functionality not implemented yet.[/yellow]")
        sys.exit(0)
    elif choice.isdigit() and 1 <= int(choice) <= len(profiles):
        selected_profile = profiles[int(choice) - 1]
        console.print(f"Selected AWS profile: [green]{selected_profile}[/green]")
        return selected_profile
    else:
        console.print("[red]Invalid selection![/red]")
        sys.exit(1)


def get_ec2_instances(profile):
    session = boto3.Session(profile_name=profile)
    ec2 = session.client("ec2")
    try:
        response = ec2.describe_instances(
            Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
        )
    except Exception as e:
        console.print(f"[red]Failed to describe instances: {e}[/red]")
        sys.exit(1)

    instances = []
    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            name = "-"
            for tag in instance.get("Tags", []):
                if tag["Key"] == "Name":
                    name = tag["Value"]
            instances.append({
                "InstanceId": instance.get("InstanceId", "-"),
                "Name": name,
                "PublicIp": instance.get("PublicIpAddress", "-"),
                "PrivateIp": instance.get("PrivateIpAddress", "-"),
            })
    return instances


def display_instances(instances):
    console.print("\nRunning EC2 Instances:")
    for idx, inst in enumerate(instances, 1):
        console.print(f"  {idx}. {inst['InstanceId']} - {inst['Name']} ({inst['PublicIp']})")


def choose_instance(instances):
    choice = input("\nSelect instance to connect (number): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(instances):
        return instances[int(choice) - 1]
    else:
        console.print("[red]Invalid selection![/red]")
        sys.exit(1)


def choose_service_log_path():
    services = list(LOG_PATHS.keys())
    console.print("\nAvailable services for logs:")
    for idx, svc in enumerate(services, 1):
        console.print(f"  {idx}. {svc}")

    choice = input("Select service log paths (number): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(services):
        selected_service = services[int(choice) - 1]
        if selected_service == "Custom":
            path = input("Enter full remote log file path: ").strip()
            if path == "":
                console.print("[red]Log path cannot be empty![/red]")
                sys.exit(1)
            return path
        else:
            paths = LOG_PATHS[selected_service]
            console.print(f"\nSelect log file path for {selected_service}:")
            for idx, p in enumerate(paths, 1):
                console.print(f"  {idx}. {p}")
            path_choice = input("Select log path (number): ").strip()
            if path_choice.isdigit() and 1 <= int(path_choice) <= len(paths):
                return paths[int(path_choice) - 1]
            else:
                console.print("[red]Invalid selection![/red]")
                sys.exit(1)
    else:
        console.print("[red]Invalid selection![/red]")
        sys.exit(1)


def get_jumphost(instances):
    for inst in instances:
        if "jump" in inst["Name"].lower():
            return inst
    return None


def create_ssh_client(hostname, username, pem_path, jumphost=None):
    try:
        key = paramiko.RSAKey.from_private_key_file(pem_path)
    except Exception as e:
        console.print(f"[red]Failed to load PEM key: {e}[/red]")
        sys.exit(1)

    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())

    try:
        if jumphost:
            jumphost_ip = jumphost["PublicIp"]
            if jumphost_ip == "-" or not jumphost_ip:
                console.print("[red]Jumphost does not have a public IP! Cannot use jumphost.[/red]")
                sys.exit(1)
            proxy_cmd = f"ssh -i {pem_path} -W {hostname}:22 ubuntu@{jumphost_ip}"
            proxy = ProxyCommand(proxy_cmd)
            client.connect(hostname=hostname, username=username, pkey=key, sock=proxy, timeout=10)
        else:
            client.connect(hostname=hostname, username=username, pkey=key, timeout=10)
    except Exception as e:
        console.print(f"[red]SSH connection failed: {e}[/red]")
        sys.exit(1)

    return client


def tail_remote_log(ssh_client, remote_path, lines=25):
    cmd = f"tail -n {lines} {remote_path}"
    try:
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        error = stderr.read().decode()
        if error:
            return None, error.strip()
        output = stdout.read().decode()
        return output, None
    except Exception as e:
        return None, str(e)


def download_remote_log(ssh_client, remote_path, local_path):
    try:
        sftp = ssh_client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        return True, None
    except Exception as e:
        return False, str(e)


def run():
    profile = choose_aws_profile()
    instances = get_ec2_instances(profile)
    if not instances:
        console.print("[red]No running instances found![/red]")
        sys.exit(1)

    display_instances(instances)
    selected_instance = choose_instance(instances)

    jumphost = get_jumphost(instances)
    use_jumphost = False
    if jumphost and jumphost["InstanceId"] != selected_instance["InstanceId"]:
        console.print(f"\nJumphost detected: [cyan]{jumphost['Name']} ({jumphost['PublicIp']})[/cyan]")
        use_jumphost = True

    username = input("Enter SSH username (default: ubuntu): ").strip() or "ubuntu"

    pem_path = input("Enter path to PEM key file (e.g. ~/.ssh/id_rsa.pem): ").strip()
    pem_path = os.path.expanduser(pem_path)
    if not os.path.isfile(pem_path):
        console.print(f"[red]PEM key file does not exist: {pem_path}[/red]")
        sys.exit(1)

    remote_log_path = choose_service_log_path()

    console.print(f"\nConnecting to instance [green]{selected_instance['InstanceId']}[/green] ({selected_instance['PrivateIp']})...")
    ssh_client = None
    try:
        if use_jumphost:
            console.print(f"Using jumphost {jumphost['PublicIp']} to connect to private instance {selected_instance['PrivateIp']}...")
            ssh_client = create_ssh_client(
                hostname=selected_instance["PrivateIp"],
                username=username,
                pem_path=pem_path,
                jumphost=jumphost,
            )
        else:
            target_ip = selected_instance["PublicIp"] if selected_instance["PublicIp"] != "-" else selected_instance["PrivateIp"]
            ssh_client = create_ssh_client(
                hostname=target_ip,
                username=username,
                pem_path=pem_path,
                jumphost=None,
            )
    except Exception as e:
        console.print(f"[red]Failed to establish SSH connection: {e}[/red]")
        sys.exit(1)

    console.print(f"\nFetching last 25 lines of log file: [cyan]{remote_log_path}[/cyan]\n")
    output, error = tail_remote_log(ssh_client, remote_log_path, 25)
    if error:
        console.print(f"[red]Error reading remote log file: {error}[/red]")
    else:
        console.print(output)

    download_choice = input("Download full log file? (y/n, default n): ").strip().lower()
    if download_choice == "y":
        local_filename = os.path.basename(remote_log_path)
        home_directory = os.path.expanduser("~")
        local_path = os.path.join(home_directory, "Downloads", local_filename)

        success, err = download_remote_log(ssh_client, remote_log_path, local_path)
        if success:
            console.print(f"[green]Log file downloaded to: {local_path}[/green]")
        else:
            console.print(f"[red]Failed to download log file: {err}[/red]")

    ssh_client.close()


if __name__ == "__main__":
    run()
