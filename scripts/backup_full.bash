#!/usr/bin/bash

##############################
# Run a full backup 
##############################

# Warnings:

# Be sure and shutdown all Docker clusters 
# as active files will not be recoverable

# The resulting tar.gz file can be quite large
# Only keep a few full backups

# Always copy your full backups to another 
# location such as your laptop or desktop
# so you have a backup in another location

# This will backup everything,
# EXCEPT the ~/backups directory
# (backups of backups cause issues)

# Start:

# Create a directory based on 
# year, month, day, hour, minute

DATE_TIME=$(date +"%Y_%m_%d_%H_%M")

BACK=/home/w205/backups/full/$DATE_TIME

mkdir $BACK

# Move to the home directory for w205

cd /home/w205

# Create a tar file of the entire tree
# EXCEPT the backups directory
# MUST be run as sudo because some 
# Docker mounts have permission issues

sudo tar -cz --exclude='backups' -f ${BACK}/w205_$DATE_TIME.tgz .

# Change the ownership of the entire backups tree
# (it doesn't hurt - just in case)

sudo chown -R w205:mids /home/w205/backups

