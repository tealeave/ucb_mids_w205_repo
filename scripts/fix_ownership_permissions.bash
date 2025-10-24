#!/usr/bin/bash

#######################################
# Fix ownership and permission issues
#######################################

#######################################
# ownership
#######################################

# Most files should be owned by user w205 group mids

# EXCEPT some of the directory trees that will be 
# mounted to Docker containers

# Some of those are required to be owned by 
# users created in the containers

# We will have to selectively change ownership

sudo chown w205:mids /home/w205/*

sudo chown -R w205:mids /home/w205/backups

sudo chown w205:mids /home/w205/docker
sudo chown -R w205:mids /home/w205/docker/clusters
sudo chown -R w205:mids /home/w205/docker/images
sudo chown w205:mids /home/w205/docker/mounts
sudo chown w205:mids /home/w205/docker/mounts/*

sudo chown -R w205:mids /home/w205/scripts

sudo chown -R w205:mids /home/w205/user

#######################################
# permissions
#######################################

# Add r and w to user and group 
# for all directories and files

# Needed because Docker containers
# need to read and write files

# In Docker containers we often make the
# Docker user part of the MIDS group

sudo chmod -R ug+rw /home/w205

# SSH requires special permissions
# or it will refuse the key!

sudo chmod 700 /home/w205
sudo chmod 700 /home/w205/.ssh
sudo chmod 600 /home/w205/.ssh/authorized_keys














