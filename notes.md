* **Set the PEM file permissions**

  Before connecting, ensure your private key file is only readable by you:

  ```bash
  chmod 400 UCB.pem
  ```

  This command makes `UCB.pem` readable by the owner only (no write or execute permissions for anyone).

* **SSH command**

  Use the following to connect to the VM. Here, `w205` is the username that Kevin configured in the AMI, and the part after `@` is your VM’s public DNS:

  ```bash
  ssh -i "UCB.pem" w205@ec2-54-81-250-101.compute-1.amazonaws.com
  ```

* **Download a file from the VM**

  To download a file from the VM to your local machine, use the `scp` command. Replace the path after the colon with the path to the file on the VM, and `attendance` with the desired local folder:

  ```bash
  scp -i "UCB.pem" w205@ec2-54-81-250-101.compute-1.amazonaws.com:/home/w205/user/certificates/ap_week_01_cert.txt attendance
  ```