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

Here’s a detailed, step-by-step breakdown of the eight “pro tricks” from the video, with every key command you’ll need:

---

## 1. Embed Your “claude.md” Rules File

**Why:** Forces Claude Code to think in tiny, verifiable tasks and keeps your code bug-free.
**How:**

1. Create a file named `claude.md` at the root of your project.
2. Copy in your personal “rules” (e.g. “Break every prompt into tasks; ask for approval before coding each task; log every task to its own folder,” etc.).
3. Save—Claude Code will automatically load and enforce these rules on every prompt.

---

## 2. Always Enter **Plan Mode** Before Coding

**Why:** Guarantees you get exactly what you asked for, every time.
**Commands:**

* **Enter plan mode:**

  ```
  Shift + Tab, Shift + Tab  
  ```
* **Specify model for planning:**

  ```
  /mod opus  
  ```

  *(Opus is optimized for outlining; generates better plans.)*
* **Example flow:**

  1. Shift+Tab × 2 → describe “Build a to-do list feature”
  2. Hit Enter → get back a step-by-step plan
  3. When you’re ready to code, switch model:

     ```
     /model sonnet  
     ```

  *(Sonnet is cheaper and perfect for execution.)*

---

## 3. Use GitHub as Your “Checkpoint” System

**Why:** Claude Code lacks rewind/checkpoints; Git commits fill that gap.
**Workflow:**

1. **After every successful micro-step:**

   ```bash
   git add .
   git commit -m "feat: completed [feature/task]"
   ```
2. **If Claude messes up:**

   ```bash
   git reset --hard HEAD^
   ```

   Then re-invoke Claude Code on that step.

---

## 4. Drag-and-Drop Screenshots for UI Inspiration & Bug-Fixing

**Why:** Claude can “see” your screenshots and generate/fix UI accordingly.
**How to Capture & Send:**

* **On macOS:**

  ```
  Cmd + Shift + 4  
  ```
* **In the chat:**

  1. Drag your `.png` into Claude Code
  2. Prompt:

     > “Build the UI seen in the screenshot I just sent.”
  3. Or for bugs:

     > “Fix the error shown in the screenshot.”

---

## 5. Clear Context Frequently with `/clear`

**Why:** Reduces hallucinations and token costs by wiping old context.
**When to `/clear`:**

* Immediately after Claude finishes each sizable task or feature.
* Before starting a brand-new micro-step.
  **Command:**

```
/clear
```

---

## 6. Run Security Checks on Every Feature

**Why:** Prevents shipping insecure code (exposed API keys, vulnerabilities).
**Workflow:**

1. After Claude completes a feature, send:

   > “Please check through all the code you just wrote and make sure it follows security best practices: no sensitive info in front end, no vulnerabilities exploitable by attackers.”
2. Review and approve Claude’s fixes before merging.

---

## 7. Learn What Claude Builds (“Explain Mode”)

**Why:** Even non-coders need to grasp data flow and logic to prompt better.
**Prompt:**

> “Please explain the functionality and code you just built out in detail. Walk me through what you changed and how it works, as if you’re a senior engineer teaching me.”

Use this **after** your security check to deepen your understanding.

---

## 8. Use Claude for “Idle-Time” Brainstorming

**Why:** Turns long code-generation waits into productive idea sessions.
**Setup Prompt (once):**

> “When I’m coding with AI, there are long breaks during which I usually doom-scroll. Instead, let’s use that time to chat: I’ll tell you what you’re building and what I’m thinking about, and you’ll help me brainstorm new ideas and next steps.”
> **During Waits:**

* Simply type “Hello, Claude” (or whatever your session name is) and start discussing business ideas, prompting improvements, etc., instead of grabbing your phone.

---

### Putting It All Together

1. **claude.md** → your seven golden rules
2. **Plan Mode** (`Shift + Tab × 2` → `/mod opus`)
3. **Execute** (`/model sonnet`)
4. **Git Commits** after each micro-step
5. **Drag + Drop** screenshots for UI/bug help
6. **/clear** often
7. **Security-check Prompt**
8. **Explain-mode Prompt**
9. **Idle-time Brainstorming Prompt**

Follow these in order for each new feature or bug-fix, and you’ll code faster, safer, and smarter with Claude Code.


```


