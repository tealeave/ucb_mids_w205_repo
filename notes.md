## 1. Connecting to the VM

1. **Lock down your private key**

   ```bash
   chmod 400 UCB.pem
   ```

   Makes `UCB.pem` readable **only** by you (no write/execute for anyone).

2. **SSH into the instance**
- note that the public DNS changes everytime

   ```bash
   ssh -i "UCB.pem" w205@ec2-54-81-250-101.compute-1.amazonaws.com
   ```

   * `w205` is the AMI user Kevin configured
   * The hostname (`ec2-…amazonaws.com`) is your VM’s public DNS

3. **Copy a file from the VM**

   ```bash
   scp -i "UCB.pem" \
     w205@ec2-54-81-250-101.compute-1.amazonaws.com:/home/w205/user/certificates/ap_week_01_cert.txt \
     attendance/
   ```

   Adjust the remote path (`:/…`) and local folder (`attendance/`) as needed.

---

## 2. Managing the Docker Cluster

We’ll cover Docker in detail later—here are the essential commands to spin up our **Anaconda + Postgres** cluster.

1. **Navigate to the cluster directory**

   ```bash
   cd ~/docker/clusters/anaconda_postgres
   ```

2. **Check existing containers**

   ```bash
   docker ps -a
   ```

3. **Start the cluster**

   ```bash
   docker-compose up -d
   ```

   * Launches both the **Postgres** and **Anaconda/Jupyter** containers in detached mode.

4. **Verify it’s running**

   ```bash
   docker ps -a
   ```

5. **Shut down the cluster**
   Always stop your containers before terminating or stopping the VM:

   ```bash
   docker-compose down
   ```

   Confirm with:

   ```bash
   docker ps -a
   ```

---

## 3. Launching Jupyter Notebook

Inside the cluster, tell Jupyter to bind to **all interfaces** (`0.0.0.0`) so Docker’s port mapping works:

```bash
docker-compose exec anaconda \
  jupyter notebook \
    --notebook-dir=/user \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root
```

When it starts, you’ll see a URL with a token (changes everytime), e.g.:

```
http://127.0.0.1:8888/?token=755f90515a61e38c30e3a70bc33116977694e4c0c70bb647
```

1. **In your local browser**, replace `127.0.0.1` with your EC2’s public IP (changes everytime):

   ```
   http://<EC2_PUBLIC_IP>:8888/?token=…
   ```
2. **Enjoy your Jupyter environment** running on Python 3.x with direct access to Postgres.

---

## 4. Using an Elastic IP

After associating an Elastic IP with your instance, you can add your computer's public key (e.g., `id_ed25519_berkeley.pub`) to the `authorized_keys` file on the VM. This allows you to connect using a more user-friendly hostname configured in your SSH config file.

```bash
# Coonect to the instance
ssh mids-205-ec2

cd ~/

# Spin up the my app, conda, and postgres, note that Dockerfile and docker-compose.yml contains info are at the same folder ~/
docker-compose up -d --force-recreate  

# Check my app log for tunnel info, click on the link provided and use the pw to link github account to dev container app
# docker logs -f w205_app_1 to live steam the log
docker logs w205_app_1 

# Check the conda log (optional)
docker logs w205_anaconda_1

# Open a new window for VScode, remote-tunnel -> github -> choose the one that is "online"
# Open a notebook, offer http://anaconda:8888 as server

# After works are done
docker-compose down

# Turn off the EC2 VM

# Example for Downloading a file
scp mids-205-ec2:/home/w205/user/certificates/lab_week_04_cert.txt attendance/

# For UCI
ssh hpc3.rcic.uci.edu

# Submit job for VScode
sbatch --ntasks=4 /opt/rcic/scripts/vscode-sshd.sh
sbatch -p free-gpu --gres=gpu:V100:1 --ntasks=4  --mem=16G /opt/rcic/scripts/vscode-sshd.sh
sbatch -p free --cpus-per-task=4 /opt/rcic/scripts/vscode-sshd.sh
sbatch -p free-gpu --ntasks=4 --gres=gpu:V100:1 /opt/rcic/scripts/vscode-sshd.sh

# Request interactive resources and GPU node, work in progress
srun -p free-gpu --gres=gpu:V100:1 --pty /bin/bash -i
srun -p free --nodes=1 --ntasks=4 --mem=32G --pty /bin/bash -i
srun -p free-gpu --ntasks=4 --gres=gpu:V100:1 --pty /bin/bash -i

# Can get a 2 cpu GPU node
poetry run python hpc_automator.py create --gpu --mem 16G  

cat vscode-sshd-39185957.out

connect to Host -> add SSH host

# Edit the config

connect to the host hpc*

# Neo4j
htttps://{EC2_IP}:7473

# Working with code agent
Write Code: "As a seasoned programmer, write code in [programming language] to [perform action, e.g., sort a list]. Ensure it's efficient, well-structured, and follows best practices. Include testing and documentation for future reference."
Debug Code: "Analyze this code: [insert code]. It's throwing this error: [insert error]. List the error-causing lines, explain why, and provide a detailed fix."
Explain Code: "Explain this code: [insert code]. Describe its functionality, logic, and any potential improvements, making it clear for all programmer levels."
Optimize Code: "Optimize this code: [insert code] for [goal, e.g., speed]. Suggest refactoring or rewriting, and explain the changes."
Automate Task: "Write a script to automate [task description] in [environment, e.g., Linux]. Include error handling, comments, execution instructions, and dependencies."
Code Review: "Create a code review checklist for a [project type, e.g., web app] in [programming language], covering readability, maintainability, performance, and security. Include explanations for each item."
Generate Documentation: "Add detailed comments to this code: [insert code] in [programming language]. Include function purposes, parameters, return values, and follow commenting conventions."

```


