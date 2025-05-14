# import paramiko
# import time
# import os
# import logging

# logger = logging.getLogger(__name__)

# def run():
#     ec2_ip = input("Enter the EC2 instance IP address: ").strip()
#     ssh_user = input("Enter the SSH username for the EC2 instance: ").strip()
#     ssh_key_path = input("Enter the path to the SSH private key file: ").strip()

#     logger.info(f"Starting heapdump creation for EC2: {ec2_ip}")
#     print(f"\n🔗 Connecting to EC2 instance {ec2_ip}...")

#     log_lines = []
#     log_file = "/tmp/heapdump_creation.log"
#     heapdump_path = f"/tmp/heapdump_{int(time.time())}.hprof"

#     try:
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         ssh.connect(ec2_ip, username=ssh_user, key_filename=ssh_key_path)
#         print(f"✅ Successfully connected to EC2 instance {ec2_ip}")
#         log_lines.append("Connected successfully to EC2 instance.")
#         logger.info(f"Connected to EC2 {ec2_ip} as {ssh_user}")

#         def exec_cmd(cmd, wait=True):
#             stdin, stdout, stderr = ssh.exec_command(cmd)
#             if wait:
#                 stdout.channel.recv_exit_status()
#             out = stdout.read().decode().strip()
#             err = stderr.read().decode().strip()
#             return out, err

#         print("🔍 Searching for Java process (MemoryLeakDemo or Confluence)...")
#         out, err = exec_cmd("pgrep -f MemoryLeakDemo || pgrep -f confluence")
#         if not out:
#             print("❌ Java process not found.")
#             log_lines.append("No Java process found.")
#             logger.warning("Java process not found on EC2.")
#             return

#         pid = out.strip().splitlines()[0]
#         print(f"✅ Java process running with PID: {pid}")
#         log_lines.append(f"Target Java process PID: {pid}")
#         logger.info(f"Found Java process with PID: {pid}")

#         print(f"🧠 Creating heapdump at {heapdump_path}...")
#         out, err = exec_cmd(f"jmap -dump:format=b,file={heapdump_path} {pid}")

#         if out:
#             print(f"📤 STDOUT:\n{out}")
#             log_lines.append(f"STDOUT:\n{out}")
#         if err:
#             print(f"⚠️ STDERR:\n{err}")
#             log_lines.append(f"STDERR:\n{err}")

#         verify_out, _ = exec_cmd(f"ls {heapdump_path}")
#         if heapdump_path in verify_out:
#             print(f"✅ Heapdump successfully created at: {heapdump_path}")
#             log_lines.append(f"Heapdump created at {heapdump_path}")
#             logger.info(f"Heapdump created at {heapdump_path}")
#         else:
#             print("❌ Heapdump creation failed.")
#             log_lines.append("Heapdump creation failed.")
#             logger.error("Heapdump creation failed.")
#             return

#         s3_bucket = input("Enter the S3 bucket name: ").strip()
#         print(f"☁️ Uploading heapdump to S3 bucket: {s3_bucket} ...")
#         upload_cmd = f"aws s3 cp {heapdump_path} s3://{s3_bucket}/"
#         out, err = exec_cmd(upload_cmd)

#         if "upload:" in out:
#             print(f"✅ Successfully uploaded to S3: s3://{s3_bucket}/{os.path.basename(heapdump_path)}")
#             log_lines.append(f"Heapdump uploaded to S3: s3://{s3_bucket}/{os.path.basename(heapdump_path)}")
#             logger.info(f"Uploaded heapdump to s3://{s3_bucket}/{os.path.basename(heapdump_path)}")
#         else:
#             print(f"❌ Error uploading to S3: {err}")
#             log_lines.append(f"S3 Upload Failed: {err}")
#             logger.error(f"Failed to upload to S3: {err}")

#     except Exception as e:
#         print(f"❌ Error: {e}")
#         log_lines.append(f"Exception: {str(e)}")
#         logger.exception("Exception during heapdump process")

#     finally:
#         remote_log_content = '\n'.join(log_lines).replace('"', '\\"')
#         try:
#             ssh.exec_command(f'echo "{remote_log_content}" | sudo tee {log_file} > /dev/null')
#             print(f"📜 Logs saved to {log_file} on the remote server.")
#             logger.info(f"Logs written to remote: {log_file}")
#         except Exception as log_e:
#             logger.warning(f"Could not write remote log: {log_e}")
#         ssh.close()
#         logger.info("Heapdump script completed.")
#         input("Press Enter to return to the submenu...")



import paramiko
import time
import os
import logging

logger = logging.getLogger(__name__)

def run():
    ec2_ip = input("Enter the EC2 instance IP address: ").strip()
    ssh_user = input("Enter the SSH username for the EC2 instance: ").strip()
    ssh_key_path = input("Enter the path to the SSH private key file: ").strip()

    logger.info(f"Starting heapdump creation for EC2: {ec2_ip}")
    print(f"\n🔗 Connecting to EC2 instance {ec2_ip}...")

    log_lines = []
    log_file = "/tmp/heapdump_creation.log"
    heapdump_path = f"/tmp/heapdump_{int(time.time())}.hprof"

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ec2_ip, username=ssh_user, key_filename=ssh_key_path)
        print(f"✅ Successfully connected to EC2 instance {ec2_ip}")
        log_lines.append("Connected successfully to EC2 instance.")
        logger.info(f"Connected to EC2 {ec2_ip} as {ssh_user}")

        def exec_cmd(cmd, wait=True):
            stdin, stdout, stderr = ssh.exec_command(cmd)
            if wait:
                stdout.channel.recv_exit_status()
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            return out, err

        print("🔍 Searching for Java process (MemoryLeakDemo or Confluence)...")
        out, err = exec_cmd("ps -eo pid,cmd | grep -E 'MemoryLeakDemo|confluence' | grep -v grep")
        if not out:
            print("❌ Java process not found.")
            log_lines.append("No Java process found.")
            logger.warning("Java process not found on EC2.")
            return

        print(f"🔢 Raw process output:\n{out}")
        pid = out.strip().split()[0]
        print(f"✅ Java process running with PID: {pid}")
        log_lines.append(f"Target Java process PID: {pid}")
        logger.info(f"Found Java process with PID: {pid}")

        print(f"🧠 Creating heapdump at {heapdump_path}...")
        log_lines.append(f"Running: sudo jmap -dump:format=b,file={heapdump_path} {pid}")
        out, err = exec_cmd(f"sudo jmap -dump:format=b,file={heapdump_path} {pid}")

        if out:
            print(f"📤 STDOUT:\n{out}")
            log_lines.append(f"STDOUT:\n{out}")
        if err:
            print(f"⚠️ STDERR:\n{err}")
            log_lines.append(f"STDERR:\n{err}")

        verify_out, _ = exec_cmd(f"ls {heapdump_path}")
        if heapdump_path in verify_out:
            print(f"✅ Heapdump successfully created at: {heapdump_path}")
            log_lines.append(f"Heapdump created at {heapdump_path}")
            logger.info(f"Heapdump created at {heapdump_path}")
        else:
            print("❌ Heapdump creation failed.")
            log_lines.append("Heapdump creation failed.")
            logger.error("Heapdump creation failed.")
            return

        s3_bucket = input("Enter the S3 bucket name: ").strip()
        print(f"☁️ Uploading heapdump to S3 bucket: {s3_bucket} ...")
        upload_cmd = f"aws s3 cp {heapdump_path} s3://{s3_bucket}/"
        out, err = exec_cmd(upload_cmd)

        if "upload:" in out:
            print(f"✅ Successfully uploaded to S3: s3://{s3_bucket}/{os.path.basename(heapdump_path)}")
            log_lines.append(f"Heapdump uploaded to S3: s3://{s3_bucket}/{os.path.basename(heapdump_path)}")
            logger.info(f"Uploaded heapdump to s3://{s3_bucket}/{os.path.basename(heapdump_path)}")
        else:
            print(f"❌ Error uploading to S3: {err}")
            log_lines.append(f"S3 Upload Failed: {err}")
            logger.error(f"Failed to upload to S3: {err}")

    except Exception as e:
        print(f"❌ Error: {e}")
        log_lines.append(f"Exception: {str(e)}")
        logger.exception("Exception during heapdump process")

    finally:
        remote_log_content = '\n'.join(log_lines).replace('"', '\\"')
        try:
            ssh.exec_command(f'echo "{remote_log_content}" | sudo tee {log_file} > /dev/null')
            print(f"📜 Logs saved to {log_file} on the remote server.")
            logger.info(f"Logs written to remote: {log_file}")
        except Exception as log_e:
            logger.warning(f"Could not write remote log: {log_e}")
        ssh.close()
        logger.info("Heapdump script completed.")
        input("Press Enter to return to the submenu...")
