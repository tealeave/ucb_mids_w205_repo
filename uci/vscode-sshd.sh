#!/bin/bash
#SBATCH --job-name=vscode-sshd
#SBATCH --output=%x-%j.out
#
# Set up a user-level sshd daemon. Publish port/hostname into $HOME/.vscode-sshd
STATEFILE=$HOME/.vscode-sshd
PORTLOW=6000
PORTHIGH=6050
HF=vscode-key
PF=sshd.pid
HKTMPDIR=$(mktemp -d)
PIDFILE=${HKTMPDIR}/${PF}
HOSTKEYFILE=${HKTMPDIR}/${HF}
AUTHORIZED_KEYS=${HOME}/.ssh/authorized_keys
LOGFILE=${HKTMPDIR}/sshd.log

cleanup () {
   if [ -d ${HKTMPDIR} ]; then
      if [ -f ${PIDFILE} ]; then
          kill $(cat ${PIDFILE})
      fi
      /bin/rm -rf ${HKTMPDIR}
   fi
}

HOST=$(hostname -s)
if [ ${HOST:0:4} != "hpc3" ]; then
   echo "can only run on a compute node"
   exit -1
fi

trap cleanup TERM INT

# create temporary host certificate
ssh-keygen -q -f ${HOSTKEYFILE} -t rsa -N ""
if [ ! -f ${HOSTKEYFILE} ]; then
    echo "ERROR: ssh-keygen did not create hostkey"
    exit -1
fi

# Attempt to start ssh-daemon
SUCCESS=0
for PORT in $(seq ${PORTLOW} ${PORTHIGH}); do
   /usr/sbin/sshd -o StrictModes=no -o AllowTcpForwarding=yes -o PermitRootLogin=no -o AuthorizedKeysFile=${AUTHORIZED_KEYS} -o PidFile=${PIDFILE} -o Subsystem="sftp internal-sftp" -h ${HOSTKEYFILE} -p ${PORT} -E ${LOGFILE} -f /dev/null
   sleep 1
   if [ -f ${PIDFILE} ]; then
       echo "-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i .ssh/id_rsa -p $PORT $(hostname)"
       echo "## VSCODE ssh host configuration ##"
       echo "## Cut and paste into your local vscode ssh configuration ##"
       echo "Host hpc3-*"
       echo "   HostName $(hostname -s)"
       echo "   Port $PORT"
       echo "   ProxyJump $(whoami)@hpc3.rcic.uci.edu"
       echo "   User $(whoami)"
       echo "   UserKnownHostsFile /dev/null"
       echo "   StrictHostKeyChecking no"
       echo " ################################## "
       SUCCESS=1
       break
   fi
done

if [ $SUCCESS -eq 1 ]; then
   echo "user mode sshd started on port $PORT"
      while [ -f ${PIDFILE} ]; do
          sleep 10
      done
else
   exit -1
fi
exit 0

