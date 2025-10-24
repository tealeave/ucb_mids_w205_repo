#!/usr/bin/bash

DIR=/home/w205/.ssh

FILE=$DIR/authorized_keys

if [ ! -d $DIR ]; then
  mkdir $DIR
fi

chmod 700 $DIR

if [ ! -f $FILE ]; then
  touch $FILE
fi

chmod 600 $FILE

if [ ! -s $FILE ]; then
  sudo cat /home/ec2-user/.ssh/authorized_keys >>$FILE 
  sudo cat /home/ec2-user/instructor_keys/ucb_mids_w205_instructor_public_key.pub >>$FILE
fi 


