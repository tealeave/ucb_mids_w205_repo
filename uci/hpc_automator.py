import paramiko
import os
import time
import re
import sys
import argparse
from contextlib import contextmanager

# --- Configuration ---
# The hostname for the HPC login node, which must match an entry in your ~/.ssh/config file.
HPC_HOSTNAME = 'hpc3.rcic.uci.edu'

# Base command to submit the Slurm job. The CPU count will be added dynamically.
SBATCH_SCRIPT_PATH = '/opt/rcic/scripts/vscode-sshd.sh'

# Time in seconds to wait between checking for the output file.
POLL_INTERVAL = 5

# Maximum time in seconds to wait for the output file before giving up.
MAX_WAIT_TIME = 300 # 5 minutes

# SSH connection timeout in seconds
SSH_TIMEOUT = 20

# Magic strings for job completion detection
JOB_COMPLETION_MARKER = "user mode sshd started"
OUTPUT_FILE_PREFIX = "vscode-sshd-"
OUTPUT_FILE_SUFFIX = ".out"

# Resource defaults
DEFAULT_GPU_TYPE = "V100"
DEFAULT_GPU_COUNT = 1
DEFAULT_GPU_PARTITION = "free-gpu"
DEFAULT_FREE_PARTITION = "free"
DEFAULT_ACCOUNT = "pkaiser_lab"

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

def validate_job_id(job_id):
    """
    Validates that a job ID is a positive integer.
    
    Args:
        job_id (str): The job ID to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    if not job_id or not job_id.isdigit():
        return False
    return int(job_id) > 0

def sanitize_resource_param(param, param_name):
    """
    Sanitizes resource parameters to prevent command injection.
    
    Args:
        param (str): The parameter value to sanitize.
        param_name (str): The name of the parameter for error messages.
        
    Returns:
        str: The sanitized parameter, or None if invalid.
    """
    if not param:
        return None
    
    # Remove any potentially dangerous characters
    if any(char in param for char in [';', '&', '|', '$', '`', '(', ')', '<', '>', '"', "'"]):
        print(f"[!] Invalid characters in {param_name}: {param}", file=sys.stderr)
        return None
    
    return param.strip()

def execute_ssh_command_with_retry(client, command, max_retries=MAX_RETRIES):
    """
    Executes an SSH command with retry logic.
    
    Args:
        client (paramiko.SSHClient): An active SSH client.
        command (str): The command to execute.
        max_retries (int): Maximum number of retry attempts.
        
    Returns:
        tuple: (stdin, stdout, stderr) from the command execution, or (None, None, None) on failure.
    """
    for attempt in range(max_retries + 1):
        try:
            stdin, stdout, stderr = client.exec_command(command)
            return stdin, stdout, stderr
        except Exception as e:
            if attempt < max_retries:
                print(f"[!] SSH command failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                print(f"    Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"[!] SSH command failed after {max_retries + 1} attempts: {e}", file=sys.stderr)
                return None, None, None

@contextmanager
def ssh_client_context(config):
    """
    Context manager for SSH client that ensures proper cleanup.
    
    Args:
        config (dict): SSH configuration dictionary.
        
    Yields:
        paramiko.SSHClient: An authenticated SSH client, or None if connection fails.
    """
    client = None
    try:
        client = get_ssh_client(config)
        yield client
    except Exception as e:
        print(f"[!] SSH context error: {e}", file=sys.stderr)
        yield None
    finally:
        if client:
            try:
                print("[*] Closing SSH connection.")
                client.close()
            except Exception as e:
                print(f"[!] Error closing SSH connection: {e}", file=sys.stderr)

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
        client.load_system_host_keys()
        client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        
        # Connect using the parameters from the SSH config file
        client.connect(
            hostname=hostname,
            username=username,
            key_filename=config.get('identityfile'),
            sock=paramiko.ProxyCommand(config.get('proxycommand')) if config.get('proxycommand') else None,
            timeout=SSH_TIMEOUT
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
        stdin, stdout, stderr = execute_ssh_command_with_retry(client, command)
        if not stdout:
            return None
        
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
    output_filename = f"{OUTPUT_FILE_PREFIX}{job_id}{OUTPUT_FILE_SUFFIX}"
    print(f"[*] Waiting for the complete output file '{output_filename}' to be created...")
    
    start_time = time.time()
    while time.time() - start_time < MAX_WAIT_TIME:
        check_command = f"ls {output_filename}"
        stdin, stdout, stderr = execute_ssh_command_with_retry(client, check_command)
        
        if stdout and stdout.channel.recv_exit_status() == 0:
            cat_command = f"cat {output_filename}"
            stdin, stdout, stderr = execute_ssh_command_with_retry(client, cat_command)
            
            if stdout.channel.recv_exit_status() == 0:
                content = stdout.read().decode()
                if JOB_COMPLETION_MARKER in content:
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
    stdin, stdout, stderr = execute_ssh_command_with_retry(client, command)
    if not stdout:
        print(f"[!] Failed to execute cancel command for job {job_id}.", file=sys.stderr)
        return
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

def check_jobs(client, username="ddlin"):
    """
    Checks current jobs for the user using squeue command.
    
    Args:
        client (paramiko.SSHClient): An active SSH client.
        username (str): Username to check jobs for.
    """
    command = f"squeue -u {username}"
    print(f"[*] Checking current jobs with command: '{command}'")
    
    stdin, stdout, stderr = execute_ssh_command_with_retry(client, command)
    if not stdout:
        print("[!] Failed to execute squeue command.", file=sys.stderr)
        return
    
    exit_status = stdout.channel.recv_exit_status()
    stdout_output = stdout.read().decode().strip()
    stderr_output = stderr.read().decode().strip()
    
    if exit_status != 0:
        print(f"[!] Error checking jobs. Exit Status: {exit_status}", file=sys.stderr)
        if stderr_output:
            print(f"    Stderr: {stderr_output}", file=sys.stderr)
        return
    
    if not stdout_output:
        print("[+] No jobs currently running.")
        return
    
    print("\n" + "="*50)
    print("🔍 Current HPC Jobs")
    print("="*50)
    print(stdout_output)
    print("="*50)

def parse_output_and_display(output_content, job_id, cpus, mem, gpu, pk_account):
    """
    Parses the job output to find the SSH config and prints it along with a cancel command.

    Args:
        output_content (str): The string content of the job output file.
        job_id (str): The ID of the submitted job.
        cpus (int or None): The number of CPUs requested for the job.
        mem (str or None): The amount of memory requested for the job.
        gpu (bool): Whether a GPU was requested for the job.
        pk_account (bool): Whether the job was submitted to the pkaiser_lab account.
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
            job_spec_message += f" with {resource_str}"
        
        if pk_account:
            job_spec_message += " under the 'pkaiser_lab' account"

        if not requested_resources and not pk_account:
            job_spec_message += " with default cluster resources"
        
        job_spec_message += "."
        
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
               "  # Request a server in the 'free' partition\n"
               "  poetry run python hpc_automator.py create --free\n\n"
               "  # Request a server under the 'pkaiser_lab' account\n"
               "  poetry run python hpc_automator.py create --cpus 4 --pk_account\n\n"
               "  # Check current jobs\n"
               "  poetry run python hpc_automator.py jobs\n\n"
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
    parser_create.add_argument(
        '--free',
        action='store_true',
        help='Request a job in the "free" partition. This will add "-p free" to the Slurm command. Mutually exclusive with --gpu.'
    )
    parser_create.add_argument(
        '--pk_account',
        action='store_true',
        help='Submit the job under the pkaiser_lab account via --account=pkaiser_lab.'
    )
    parser_create.add_argument(
        '--dry-run',
        action='store_true',
        help='Show the command that would be executed without actually running it.'
    )

    # Cancel command - stops a running job.
    parser_cancel = subparsers.add_parser(
        'cancel', 
        help='Stops a running VS Code server job on Slurm.',
        description='Cancels a specific, running Slurm job using its job ID.'
        )
    parser_cancel.add_argument('job_id', help='The numeric ID of the Slurm job to be cancelled.')
    
    # Jobs command - checks current jobs.
    parser_jobs = subparsers.add_parser(
        'jobs',
        help='Checks current HPC jobs using squeue.',
        description='Displays current jobs for the user using squeue command.'
    )
    
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

    # 2. Handle dry-run mode without SSH connection
    if args.command == 'create' and getattr(args, 'dry_run', False):
        # Build command for dry-run display
        sbatch_options = []
        if args.pk_account:
            sbatch_options.append(f'--account={DEFAULT_ACCOUNT}')
            
        if args.gpu:
            sbatch_options.append(f'-p {DEFAULT_GPU_PARTITION} --gres=gpu:{DEFAULT_GPU_TYPE}:{DEFAULT_GPU_COUNT}')
        elif args.free:
            sbatch_options.append(f'-p {DEFAULT_FREE_PARTITION}')
        
        if args.cpus:
            sbatch_options.append(f'--ntasks={args.cpus}')
        if args.mem:
            sbatch_options.append(f'--mem={args.mem}')
        
        sbatch_args_str = " ".join(sbatch_options)
        sbatch_command = f'sbatch {sbatch_args_str} {SBATCH_SCRIPT_PATH}'.strip()
        
        print("=== DRY RUN MODE ===")
        print(f"Would execute: {sbatch_command}")
        print("=== END DRY RUN ===")
        return
    
    # 3. Establish SSH connection with automatic cleanup
    with ssh_client_context(user_config) as client:
        if not client:
            return

        # --- Action-specific logic ---
        if args.command == 'create':
            # Validate mutual exclusivity of --gpu and --free
            if args.gpu and args.free:
                print("[!] Error: --gpu and --free options are mutually exclusive. Please choose one.", file=sys.stderr)
                return
            
            # Validate and sanitize resource parameters
            if args.mem:
                args.mem = sanitize_resource_param(args.mem, "memory")
                if not args.mem:
                    return
            
            if args.cpus and args.cpus <= 0:
                print("[!] Error: CPU count must be a positive integer.", file=sys.stderr)
                return

            # Build the sbatch command parts in the correct order
            sbatch_options = []
            if args.pk_account:
                sbatch_options.append(f'--account={DEFAULT_ACCOUNT}')
                
            if args.gpu:
                sbatch_options.append(f'-p {DEFAULT_GPU_PARTITION} --gres=gpu:{DEFAULT_GPU_TYPE}:{DEFAULT_GPU_COUNT}')
            elif args.free: # Only add -p free if --free is explicitly used
                sbatch_options.append(f'-p {DEFAULT_FREE_PARTITION}') 
            
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
                    parse_output_and_display(output_content, job_id, args.cpus, args.mem, args.gpu, args.pk_account)
                else:
                    print("[!] Failed to retrieve job output. Please log in manually to check the job status.")
                    print(f"    Check for a file named '{OUTPUT_FILE_PREFIX}{job_id}{OUTPUT_FILE_SUFFIX}' in your home directory.")
        
        elif args.command == 'cancel':
            if not validate_job_id(args.job_id):
                print(f"[!] Invalid job ID: {args.job_id}. Must be a positive integer.", file=sys.stderr)
                return
            cancel_job(client, args.job_id)
        
        elif args.command == 'jobs':
            check_jobs(client)

if __name__ == '__main__':
    # Before running, ensure you have the 'paramiko' library installed.
    # pip install paramiko
    main()