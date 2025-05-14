# import boto3
# import logging
# import botocore
# import os
# import configparser

# def setup_logging():
#     log_file = os.path.expanduser("~/.sre-jarvis/logs/main.log")
#     os.makedirs(os.path.dirname(log_file), exist_ok=True)
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(levelname)s - %(message)s',
#         handlers=[
#             logging.FileHandler(log_file),
#             logging.StreamHandler()
#         ]
#     )

# def list_existing_profiles():
#     credentials_config = configparser.ConfigParser()
#     credentials_config.read(os.path.expanduser("~/.aws/credentials"))

#     config_config = configparser.ConfigParser()
#     config_config.read(os.path.expanduser("~/.aws/config"))

#     valid_profiles = []
#     for profile in credentials_config.sections():
#         config_section = f"profile {profile}" if profile != "default" else "default"
#         if config_section in config_config and "region" in config_config[config_section]:
#             valid_profiles.append(profile)
#     return valid_profiles

# def prompt_for_aws_configuration():
#     print("\n❌ AWS credentials or region not found. Please configure them first.")
#     profile_name = input("Enter a profile name for this configuration (e.g., dev, prod): ").strip()
#     aws_access_key_id = input("Enter AWS Access Key ID: ").strip()
#     aws_secret_access_key = input("Enter AWS Secret Access Key: ").strip()
#     aws_region = input("Enter AWS Region (e.g., us-west-2): ").strip()

#     aws_credentials_dir = os.path.expanduser("~/.aws")
#     os.makedirs(aws_credentials_dir, exist_ok=True)

#     credentials_path = os.path.join(aws_credentials_dir, "credentials")
#     credentials_config = configparser.ConfigParser()
#     credentials_config.read(credentials_path)
#     credentials_config[profile_name] = {
#         "aws_access_key_id": aws_access_key_id,
#         "aws_secret_access_key": aws_secret_access_key
#     }
#     with open(credentials_path, "w") as f:
#         credentials_config.write(f)

#     config_path = os.path.join(aws_credentials_dir, "config")
#     config = configparser.ConfigParser()
#     config.read(config_path)
#     config[f"profile {profile_name}"] = {"region": aws_region}
#     with open(config_path, "w") as f:
#         config.write(f)

#     print("\n✅ AWS credentials and region have been configured.")
#     input("Press Enter to continue...")
#     return profile_name

# def choose_profile():
#     profiles = list_existing_profiles()
#     if profiles:
#         print("\nAvailable AWS profiles:")
#         for i, profile in enumerate(profiles):
#             print(f"  {i + 1}. {profile}")
#         choice = input("Select AWS profile number or press Enter to add new AWS account: ").strip()
#         if choice.isdigit() and 1 <= int(choice) <= len(profiles):
#             return profiles[int(choice) - 1]
#         else:
#             return prompt_for_aws_configuration()
#     else:
#         return prompt_for_aws_configuration()

# def restart_all_confluence_instances(profile_name, tag_value="confluence"):
#     logging.info(f"Selected AWS Profile: {profile_name}")
#     logging.info(f"Instance tag value: {tag_value}")
#     try:
#         config = configparser.ConfigParser()
#         config.read(os.path.expanduser("~/.aws/config"))
#         region = config.get(f"profile {profile_name}", "region", fallback=None)

#         if not region:
#             raise ValueError("Region is not set for this profile in the AWS config.")

#         session = boto3.Session(profile_name=profile_name, region_name=region)
#         ec2 = session.client("ec2")
        
#         response = ec2.describe_instances(
#             Filters=[
#                 {"Name": "tag:Name", "Values": [f"*{tag_value}*"]},
#                 {"Name": "instance-state-name", "Values": ["running"]}
#             ]
#         )

#         instances = [
#             {
#                 "id": instance["InstanceId"],
#                 "name": next((tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"), "Unnamed")
#             }
#             for reservation in response["Reservations"]
#             for instance in reservation["Instances"]
#         ]

#         if not instances:
#             logging.warning(f"❌ No running EC2 instances found with tag matching: {tag_value}")
#             print(f"❌ No running EC2 instances found with tag matching: {tag_value}")
#             return

#         for idx, instance in enumerate(instances, start=1):
#             instance_id = instance["id"]
#             instance_name = instance["name"]

#             logging.info(f"🔁 Restarting instance: {instance_name} ({instance_id})")
#             print(f"\n🔁 Restarting instance: {instance_name} ({instance_id})")
#             ec2.reboot_instances(InstanceIds=[instance_id])

#             logging.info(f"⏳ Waiting for {instance_name} to pass health checks...")
#             print(f"⏳ Waiting for {instance_name} to pass health checks...")
#             waiter = ec2.get_waiter('instance_status_ok')
#             waiter.wait(InstanceIds=[instance_id])

#             logging.info(f"✅ {instance_name} ({instance_id}) is now healthy and running.")
#             print(f"✅ {instance_name} ({instance_id}) is now healthy and running.")

#         logging.info("\n✅ All EC2 instances restarted and verified.")
#         print("\n✅ All EC2 instances restarted and verified.")

#     except botocore.exceptions.BotoCoreError as e:
#         logging.error(f"❌ AWS SDK error: {str(e)}")
#         print(f"❌ AWS SDK error: {str(e)}")
#     except ValueError as e:
#         logging.error(f"❌ ValueError: {str(e)}")
#         print(f"❌ {str(e)}")
#     except Exception as e:
#         logging.error(f"❌ Exception occurred: {str(e)}")
#         print(f"❌ Error: {str(e)}")

#     input("\nPress Enter to return to the submenu...")

# def run():
#     setup_logging()  # Set up logging at the start
#     profile_name = choose_profile()
#     logging.info(f"Selected profile: {profile_name}")
#     print("\n🔁 Restarting Confluence EC2 Instances via AWS Tag\n")
#     tag_value = input("Enter instance name or tag value to match : ").strip() or "confluence"
#     logging.info(f"Using instance tag: {tag_value}")
#     restart_all_confluence_instances(profile_name, tag_value)




import boto3
import logging
import botocore
import os
import configparser

# Setup logging with dynamic log file location
def setup_logging(log_file_path=None):
    if not log_file_path:
        log_file_path = os.path.expanduser("~/.sre-jarvis/logs/main.log")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )

# List available AWS profiles
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

# Prompt the user to configure AWS credentials if not found
def prompt_for_aws_configuration():
    print("\n❌ AWS credentials or region not found. Please configure them first.")
    profile_name = input("Enter a profile name for this configuration (e.g., dev, prod): ").strip()
    aws_access_key_id = input("Enter AWS Access Key ID: ").strip()
    aws_secret_access_key = input("Enter AWS Secret Access Key: ").strip()
    aws_region = input("Enter AWS Region (e.g., us-west-2): ").strip()

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

    print("\n✅ AWS credentials and region have been configured.")
    input("Press Enter to continue...")
    return profile_name

# Choose an existing AWS profile or configure a new one
def choose_profile():
    profiles = list_existing_profiles()
    if profiles:
        print("\nAvailable AWS profiles:")
        for i, profile in enumerate(profiles):
            print(f"  {i + 1}. {profile}")
        choice = input("Select AWS profile number or press Enter to add new AWS account: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(profiles):
            return profiles[int(choice) - 1]
        else:
            return prompt_for_aws_configuration()
    else:
        return prompt_for_aws_configuration()

# Restart all EC2 instances matching the specified tag value
def restart_all_confluence_instances(profile_name, tag_value="confluence"):
    logging.info(f"Selected AWS Profile: {profile_name}")
    logging.info(f"Instance tag value: {tag_value}")
    try:
        config = configparser.ConfigParser()
        config.read(os.path.expanduser("~/.aws/config"))
        region = config.get(f"profile {profile_name}", "region", fallback=None)

        if not region:
            raise ValueError("Region is not set for this profile in the AWS config.")

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
            logging.warning(f"❌ No running EC2 instances found with tag matching: {tag_value}")
            print(f"❌ No running EC2 instances found with tag matching: {tag_value}")
            return

        for idx, instance in enumerate(instances, start=1):
            instance_id = instance["id"]
            instance_name = instance["name"]

            logging.info(f"🔁 Restarting instance: {instance_name} ({instance_id})")
            print(f"\n🔁 Restarting instance: {instance_name} ({instance_id})")
            ec2.reboot_instances(InstanceIds=[instance_id])

            logging.info(f"⏳ Waiting for {instance_name} to pass health checks...")
            print(f"⏳ Waiting for {instance_name} to pass health checks...")
            waiter = ec2.get_waiter('instance_status_ok')
            waiter.wait(InstanceIds=[instance_id])

            logging.info(f"✅ {instance_name} ({instance_id}) is now healthy and running.")
            print(f"✅ {instance_name} ({instance_id}) is now healthy and running.")

        logging.info("\n✅ All EC2 instances restarted and verified.")
        print("\n✅ All EC2 instances restarted and verified.")

    except botocore.exceptions.BotoCoreError as e:
        logging.error(f"❌ AWS SDK error: {str(e)}")
        print(f"❌ AWS SDK error: {str(e)}")
    except ValueError as e:
        logging.error(f"❌ ValueError: {str(e)}")
        print(f"❌ {str(e)}")
    except Exception as e:
        logging.error(f"❌ Exception occurred: {str(e)}")
        print(f"❌ Error: {str(e)}")

    input("\nPress Enter to return to the submenu...")

# Run the script
def run():
    log_file_path = os.path.expanduser("~/.sre-jarvis/logs/restart.log")
    setup_logging(log_file_path)  # Set up logging with dynamic log file
    profile_name = choose_profile()
    logging.info(f"Selected profile: {profile_name}")
    print("\n🔁 Restarting Confluence EC2 Instances via AWS Tag\n")
    tag_value = input("Enter instance name or tag value to match (default is 'confluence'): ").strip() or "confluence"
    logging.info(f"Using instance tag: {tag_value}")
    restart_all_confluence_instances(profile_name, tag_value)
