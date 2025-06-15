import paramiko
import os
import time
import re
import sys
import argparse

# --- Configuration ---
# The hostname for the HPC login node, which must match an entry in your ~/.ssh/config file.
HPC_HOSTNAME = 'hpc3.rcic.uci.edu'

# Base command to submit the Slurm job. The CPU count will be added dynamically.
SBATCH_SCRIPT_PATH = '/opt/rcic/scripts/vscode-sshd.sh'

# Time in seconds to wait between checking for the output file.
POLL_INTERVAL = 5

# Maximum time in seconds to wait for the output file before giving up.
MAX_WAIT_TIME = 300 # 5 minutes

def get_ssh_client(config):
    """
    Creates and returns an authenticated SSH client using a parsed config.
    
    Args:
        config (dict): A dictionary-like object from paramiko.SSHConfig().lookup().

    Returns:
        paramiko.SSHClient: An active and authenticated SSH client object,
                            or None if the connection fails.
    """
    hostname = config['hostname']
    username = config.get('user')
    
    if not username:
        print(f"[!] 'User' not specified in your SSH config for host '{HPC_HOSTNAME}'.", file=sys.stderr)
        return None

    try:
        print(f"[*] Connecting to {hostname} as {username} using your SSH config...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect using the parameters from the SSH config file
        client.connect(
            hostname=hostname,
            username=username,
            key_filename=config.get('identityfile'),
            sock=paramiko.ProxyCommand(config.get('proxycommand')) if config.get('proxycommand') else None,
            timeout=20
        )
        print("[+] Connection successful!")
        return client
    except Exception as e:
        print(f"[!] Connection failed: {e}", file=sys.stderr)
        print("[!] Please ensure your SSH key is added to your ssh-agent or is not passphrase protected.", file=sys.stderr)
        return None

def submit_job(client, command):
    """
    Executes the sbatch command to submit the job and extracts the job ID.
    
    Args:
        client (paramiko.SSHClient): An active SSH client.
        command (str): The sbatch command to execute.

    Returns:
        str: The extracted job ID, or None if submission fails.
    """
    try:
        print(f"[*] Submitting job with command: '{command}'")
        stdin, stdout, stderr = client.exec_command(command)
        
        exit_status = stdout.channel.recv_exit_status()
        stdout_output = stdout.read().decode().strip()
        stderr_output = stderr.read().decode().strip()

        if exit_status != 0:
            print(f"[!] Error submitting job. Exit Status: {exit_status}", file=sys.stderr)
            print(f"    Stderr: {stderr_output}", file=sys.stderr)
            return None

        print(f"[+] Server response: {stdout_output}")
        match = re.search(r'(\d+)', stdout_output)
        if match:
            job_id = match.group(1)
            print(f"[+] Successfully submitted job. Job ID: {job_id}")
            return job_id
        else:
            print("[!] Could not parse job ID from sbatch output.", file=sys.stderr)
            return None
            
    except Exception as e:
        print(f"[!] Failed to execute sbatch command: {e}", file=sys.stderr)
        return None

def get_job_output(client, job_id):
    """
    Polls for the job output file, waits for it to be complete, and returns its content.
    The file is considered complete when it contains the string "user mode sshd started".

    Args:
        client (paramiko.SSHClient): An active SSH client.
        job_id (str): The Slurm job ID.

    Returns:
        str: The content of the output file, or None on failure or timeout.
    """
    output_filename = f"vscode-sshd-{job_id}.out"
    print(f"[*] Waiting for the complete output file '{output_filename}' to be created...")
    
    start_time = time.time()
    while time.time() - start_time < MAX_WAIT_TIME:
        check_command = f"ls {output_filename}"
        stdin, stdout, stderr = client.exec_command(check_command)
        
        if stdout.channel.recv_exit_status() == 0:
            cat_command = f"cat {output_filename}"
            stdin, stdout, stderr = client.exec_command(cat_command)
            
            if stdout.channel.recv_exit_status() == 0:
                content = stdout.read().decode()
                if "user mode sshd started" in content:
                    print("[+] Complete output file found!")
                    return content
        
        print(f"    ...still waiting for complete file (elapsed: {int(time.time() - start_time)}s)")
        time.sleep(POLL_INTERVAL)

    print(f"[!] Timed out after {MAX_WAIT_TIME} seconds. Job may have failed to start or write output.", file=sys.stderr)
    return None

def cancel_job(client, job_id):
    """
    Executes the scancel command to cancel a running Slurm job.

    Args:
        client (paramiko.SSHClient): An active SSH client.
        job_id (str): The ID of the job to cancel.
    """
    command = f"scancel {job_id}"
    print(f"[*] Attempting to cancel job {job_id} with command: '{command}'")
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    stderr_output = stderr.read().decode().strip()

    if exit_status == 0:
        print(f"[+] Successfully cancelled job {job_id}.")
    else:
        print(f"[!] Failed to cancel job {job_id}.", file=sys.stderr)
        if stderr_output:
            print(f"    Server error: {stderr_output}", file=sys.stderr)
        else:
            print("    Unknown error. The job may have already finished or the ID is invalid.", file=sys.stderr)

def parse_output_and_display(output_content, job_id, cpus, mem, gpu):
    """
    Parses the job output to find the SSH config and prints it along with a cancel command.

    Args:
        output_content (str): The string content of the job output file.
        job_id (str): The ID of the submitted job.
        cpus (int or None): The number of CPUs requested for the job.
        mem (str or None): The amount of memory requested for the job.
        gpu (bool): Whether a GPU was requested for the job.
    """
    if not output_content:
        print("[!] Cannot parse empty output content.", file=sys.stderr)
        return

    config_block_match = re.search(r"(Host hpc3-\*.*?StrictHostKeyChecking no)", output_content, re.DOTALL)
    
    if config_block_match:
        config_block = config_block_match.group(1).strip()
        print("\n" + "="*50)
        print("🎉 VS Code SSH Configuration Ready! 🎉")
        print("="*50)
        print("\nCopy the following block into your local SSH config file.")
        print("In VS Code, you can access this via 'Remote-SSH: Open Configuration File...'\n")
        print("-" * 50)
        print(config_block)
        print("-" * 50)
        print("\nAfter adding it, use 'Remote-SSH: Connect to Host...' and select 'hpc3-*'.")
        
        print("\n" + "="*50)
        
        # Build the job specification message dynamically
        job_spec_message = f"✅ Job {job_id} is running"
        requested_resources = []
        if gpu:
            requested_resources.append("1 V100 GPU")
        if cpus:
            requested_resources.append(f"{cpus} CPU(s)")
        if mem:
            requested_resources.append(f"{mem} of memory")

        if requested_resources:
            # Natural language join for the list of resources
            if len(requested_resources) > 2:
                resource_str = ", ".join(requested_resources[:-1]) + f", and {requested_resources[-1]}"
            else:
                resource_str = " and ".join(requested_resources)
            job_spec_message += f" with {resource_str}."
        else:
            job_spec_message += " with default cluster resources."
        
        print(job_spec_message)

        print(f"To stop this server later, run:")
        print(f"poetry run python {os.path.basename(sys.argv[0])} cancel {job_id}")
        print("="*50)

    else:
        print("\n[!] Could not find the SSH configuration block in the job output.")
        print("    Please check the full job output below for errors:\n")
        print("-" * 50)
        print(output_content)
        print("-" * 50)

def main():
    """ Main function to parse arguments and run the automation script. """
    parser = argparse.ArgumentParser(
        description="A script to automate starting and stopping VS Code servers on the UCI HPC cluster via Slurm.",
        epilog="Example usage:\n"
               "  # Request a server with specific resources\n"
               "  poetry run python hpc_automator.py create --cpus 8 --mem 32G\n\n"
               "  # Request a server with a GPU (and default CPU/mem)\n"
               "  poetry run python hpc_automator.py create --gpu\n\n"
               "  # Request a GPU with specific CPU/mem\n"
               "  poetry run python hpc_automator.py create --gpu --cpus 4 --mem 16G\n\n"
               "  # Cancel a running server\n"
               "  poetry run python hpc_automator.py cancel 123456",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available actions')

    # Create command - starts a new job with resource options.
    parser_create = subparsers.add_parser(
        'create', 
        help='Submits a new Slurm job to start a VS Code server.',
        description='Creates a new VS Code server job, waits for it to start, and provides the necessary SSH configuration.'
    )
    parser_create.add_argument(
        '--cpus', 
        type=int,
        # No default value
        help='Number of CPUs to request for the job (e.g., 4). If not set, uses cluster default.'
    )
    parser_create.add_argument(
        '--mem', 
        type=str,
        # No default value
        help='Amount of memory to request (e.g., "16G"). If not set, uses cluster default.'
    )
    parser_create.add_argument(
        '--gpu',
        action='store_true',
        help='Request a V100 GPU for the job. This will add "-p free-gpu --gres=gpu:V100:1" to the Slurm command.'
    )

    # Cancel command - stops a running job.
    parser_cancel = subparsers.add_parser(
        'cancel', 
        help='Stops a running VS Code server job on Slurm.',
        description='Cancels a specific, running Slurm job using its job ID.'
        )
    parser_cancel.add_argument('job_id', help='The numeric ID of the Slurm job to be cancelled.')
    
    args = parser.parse_args()

    # --- Common setup for all actions ---
    print("--- UCI HPC VS Code Automation Script ---")

    # 1. Load SSH configuration from file
    ssh_config_path = os.path.expanduser('~/.ssh/config')
    try:
        with open(ssh_config_path) as f:
            ssh_config = paramiko.SSHConfig()
            ssh_config.parse(f)
    except FileNotFoundError:
        print(f"[!] SSH config file not found at '{ssh_config_path}'", file=sys.stderr)
        return
    
    user_config = ssh_config.lookup(HPC_HOSTNAME)
    if not user_config or 'hostname' not in user_config:
        print(f"[!] No configuration for host '{HPC_HOSTNAME}' found in '{ssh_config_path}'.", file=sys.stderr)
        return

    # 2. Establish SSH connection
    client = get_ssh_client(user_config)
    if not client:
        return

    # --- Action-specific logic ---
    if args.command == 'create':
        # Build the sbatch command parts in the correct order
        sbatch_options = []
        if args.gpu:
            sbatch_options.append('-p free-gpu --gres=gpu:V100:1')
        if args.cpus:
            sbatch_options.append(f'--ntasks={args.cpus}')
        if args.mem:
            sbatch_options.append(f'--mem={args.mem}')
        
        # Join options with spaces, if any exist
        sbatch_args_str = " ".join(sbatch_options)
        
        # Construct the full command
        sbatch_command = f'sbatch {sbatch_args_str} {SBATCH_SCRIPT_PATH}'.strip()
        
        job_id = submit_job(client, sbatch_command)
        if job_id:
            output_content = get_job_output(client, job_id)
            if output_content:
                parse_output_and_display(output_content, job_id, args.cpus, args.mem, args.gpu)
            else:
                print("[!] Failed to retrieve job output. Please log in manually to check the job status.")
                print(f"    Check for a file named 'vscode-sshd-{job_id}.out' in your home directory.")
    
    elif args.command == 'cancel':
        cancel_job(client, args.job_id)
        
    # Clean up the SSH connection
    print("[*] Closing SSH connection.")
    client.close()

if __name__ == '__main__':
    # Before running, ensure you have the 'paramiko' library installed.
    # pip install paramiko
    main()