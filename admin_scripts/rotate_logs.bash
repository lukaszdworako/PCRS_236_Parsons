#!/bin/bash

today=`date +%Y-%m-%d`

# Ignore commented lines. databases.txt is a link to ~/.pgpass
# ignore _data, since those are not instances
for line in `grep -v '^[[:space:]]*#' /home/pcrsadmin/backup/databases.txt | grep -v _data`:
do
    OIFS=$IFS; IFS=':'; read -a fields <<< "$line"; IFS=$OIFS;
    mv /home/pcrsadmin/logs/${fields[2]}.log /home/pcrsadmin/logs/${fields[2]}.log.${today};
    touch /home/pcrsadmin/logs/${fields[2]}.log;
done

