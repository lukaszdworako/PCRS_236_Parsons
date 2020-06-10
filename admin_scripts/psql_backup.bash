#!/bin/bash

# Ignore commented lines. databases.txt is a link to ~/.pgpass
for line in `grep -v '^[[:space:]]*#' /home/pcrsadmin/backup/databases.txt`
do
    OIFS=$IFS; IFS=':'; read -a fields <<< "$line"; IFS=$OIFS
    pg_dump -U ${fields[3]} ${fields[2]} | gzip > /home/pcrsadmin/backup/${fields[2]}.$1.psql.gz
done

