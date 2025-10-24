#!/usr/bin/bash

##############################
# Run a partial backup 
##############################

# Warnings:

# This is only a partial backup 
# to save space

# Start:

# Create a variable for the partial directory

PARTIAL=/home/w205/backups/partial

# Create a directory based on 
# year, month, day, hour, minute

DATE_TIME=$(date +"%Y_%m_%d_%H_%M")

BACK=$PARTIAL/$DATE_TIME

mkdir $BACK

cd $BACK

# Selectively copy in the files 

sudo cp /home/w205/* $BACK 2>/dev/null
sudo cp /home/w205/.* $BACK 2>/dev/null

sudo cp -R /home/w205/docker $BACK
sudo cp -R /home/w205/scripts $BACK
sudo cp -R /home/w205/user $BACK

# Change the ownership of the entire backups tree
# (it doesn't hurt - just in case)

sudo chown -R w205:mids /home/w205/backups

# Selectively remove the larger files

sudo rm -r $BACK/docker/mounts
sudo rm -r $BACK/user/how_to_guides/sales_database/data
sudo rm -r $BACK/user/labs/week_02/geojson_data

# Development servers have instructor directories on them
# This may not apply to your server if your not 
# an instructor nor TA

sudo rm -r $BACK/user/.instructor 2>/dev/null

# Create a tar file in the PARTIAL directory

sudo tar -czf $PARTIAL/w205_$DATE_TIME.tgz .

# Now that they tar file is made, 
# remove the copied files

sudo rm -r $BACK/*

# Move tar file

sudo mv $PARTIAL/w205_$DATE_TIME.tgz $BACK

# Change the ownership of the entire backups tree
# (it doesn't hurt - just in case)

sudo chown -R w205:mids /home/w205/backups 


