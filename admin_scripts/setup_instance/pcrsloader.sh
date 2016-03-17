#!/bin/bash
# The loader creates new instances of pcrs and configures postgres with syncdb

# $1 bitbucket_name
# $2 implementation_name
# ***run as pcrsadmin

# Usage: ./pcrsloader.sh bitbucket_name instance_name

FILEPATH='/home/pcrsadmin/www'
DATE=`date +%Y-%m-%d`

# clone pcrs master branch
echo "Attempting to clone master PCRS branch"
#git clone https://$1@bitbucket.org/utmandrew/pcrs.git ${FILEPATH}/$2
git clone https://$1@bitbucket.org/olessika/pcrs.git ${FILEPATH}/$2

# replace settings.py with correctly formatted one
echo "Replacing settings.py"
mv ${FILEPATH}/$2/pcrs/pcrs/settings.py ${FILEPATH}/$2/pcrs/pcrs/settings.py.${DATE}
sed "s/%(server_name)s/$2/g" settings.py.template > ${FILEPATH}/$2/pcrs/pcrs/settings.py

# replace login.py with correctly formatted one
echo "Replacing login.py"
mv ${FILEPATH}/$2/pcrs/login.py ${FILEPATH}/$2/pcrs/login.py.${DATE}
cp login.py.template ${FILEPATH}/$2/pcrs/login.py

# replace wsgi.py
echo "Replacing wsgi.py"
mv ${FILEPATH}/$2/pcrs/pcrs/wsgi.py ${FILEPATH}/$2/pcrs/pcrs/wsgi.py.${DATE}
sed "s/%(server_name)s/$2/g" wsgi.py.template > ${FILEPATH}/$2/pcrs/pcrs/wsgi.py

# create database for the instance
echo "Creating database"
createdb $2

# Configure database
echo "Syncing database"
python3.4 ${FILEPATH}/$2/pcrs/manage.py syncdb
echo "Collecting static"
python3.4 ${FILEPATH}/$2/pcrs/manage.py collectstatic

# Permissions
echo "Setting permissions"
find ${FILEPATH}/$2/pcrs -type d -exec chmod 750 {} \;
chmod 755 ${FILEPATH}/$2/pcrs
find ${FILEPATH}/$2/pcrs -type f -exec chmod 640 {} \;
find ${FILEPATH}/$2/static -type d -exec chmod 775 {} \;
find ${FILEPATH}/$2/static -type f -exec chmod 664 {} \;

# Hack to fix fonts issue
ln -s ${FILEPATH}/$2/bootstrap-3.1.1/fonts ${FILEPATH}/$2/fonts

# Set up node server for your application
# TODO

# Create the apache config text to copy paste into /etc/apache2/httpd.conf
echo "========================================================================="
echo "The following is the apache configuration for this instance of pcrs:"
echo "(Saved to ${FILEPATH}/$2/$2.apacheconfig)"
echo "    Alias /$2/static /home/pcrsadmin/www/$2/static
    <Directory /home/pcrsadmin/www/$2/static/>
        Order deny,allow
        Allow from all
    </Directory>

    WSGIDaemonProcess pcrs_$2 user=pcrsadmin group=pcrsadmin processes=1 threads=5
    WSGIScriptAlias /$2 /home/pcrsadmin/www/$2/pcrs/pcrs/wsgi.py
    <Directory /home/pcrsadmin/www/$2/pcrs/pcrs>
        <Files wsgi.py>
            Order deny,allow
            Allow from all
        </Files>
    </Directory>" > ${FILEPATH}/$2/$2.apacheconfig
chmod 600 ${FILEPATH}/$2/$2.apacheconfig
cat ${FILEPATH}/$2/$2.apacheconfig
