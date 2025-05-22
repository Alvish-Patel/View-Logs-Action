import paramiko
import logging

def connect_via_jump(jump_host, jump_user, private_ip, private_user, pem_path, command):
    try:
        logging.info(f"Connecting to jump host {jump_host} as {jump_user}...")
        jump_key = paramiko.RSAKey.from_private_key_file(pem_path)

        # Connect to jump host
        jump_client = paramiko.SSHClient()
        jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        jump_client.connect(jump_host, username=jump_user, pkey=jump_key)

        # Open channel from jump host to private instance
        jump_transport = jump_client.get_transport()
        channel = jump_transport.open_channel(
            "direct-tcpip", (private_ip, 22), (jump_host, 22)
        )

        # Connect to private EC2
        private_client = paramiko.SSHClient()
        private_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_client.connect(private_ip, username=private_user, pkey=jump_key, sock=channel)

        # Run command on private EC2
        stdin, stdout, stderr = private_client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        private_client.close()
        jump_client.close()

        return output, error

    except Exception as e:
        return "", str(e)
