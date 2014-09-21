#!/bin/bash
# The loader creates new instances of pcrs and configures postgres with syncdb

# $1 bitbucket_name
# $2 implementation_name
# ***run as pcrsadmin

# Usage: ./pcrsloader.sh bitbucket_name instance_name

FILEPATH='/home/pcrsadmin/www'
DATE=`date +%Y-%m-%d`

echo "Saving settings: settings.py, login.py, wsgi.py"
pushd ${FILEPATH}/$2/pcrs
mv pcrs/settings.py pcrs/settings.py.${DATE}.temp
mv pcrs/wsgi.py pcrs/wsgi.py.${DATE}.temp
mv login.py login.py.${DATE}.temp

echo "Updating code"
git remote set-url origin https://$1@bitbucket.org/utmandrew/pcrs.git

# Uncomment the below if you need a specific new branch
# git checkout <branch-name>

# Uncomment the below if there are changes to destroy
# git reset --hard

git pull

echo "Don't forget to check settings.py, wsgi.py, and login.py"
mv pcrs/settings.py pcrs/settings.py.${DATE}
mv pcrs/wsgi.py pcrs/wsgi.py.${DATE}
mv login.py login.py.${DATE}
mv pcrs/settings.py.${DATE}.temp pcrs/settings.py
mv pcrs/wsgi.py.${DATE}.temp pcrs/wsgi.py
mv login.py.${DATE}.temp login.py

echo "Syncing database"
python3.4 manage.py syncdb
echo "Collecting static"
python3.4 manage.py collectstatic

echo "Setting permissions"
find . -type d -exec chmod 750 {} \;
chmod 755 .
find . -type f -exec chmod 640 {} \;
find ../static -type d -exec chmod 775 {} \;
find ../static -type f -exec chmod 664 {} \;

# Hack to fix fonts issue
rm -f ../static/fonts
ln -s ../static/bootstrap-3.1.1/fonts ../static/fonts

popd
