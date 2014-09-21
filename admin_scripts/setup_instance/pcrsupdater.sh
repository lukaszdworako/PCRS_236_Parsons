#!/bin/bash
# The loader creates new instances of pcrs and configures postgres with syncdb

# $1 bitbucket_name
# $2 implementation_name
# ***run as pcrsadmin

# Usage: ./pcrsloader.sh bitbucket_name instance_name

FILEPATH='/home/pcrsadmin/www'
DATE=`date +%Y-%m-%d`

echo "Saving settings: settings.py, login.py, wsgi.py"
pushd ${FILEPATH}/$2
mv pcrs/pcrs/settings.py ${FILEPATH}/pcrsloader/backup/settings.py.${DATE}.$2
mv pcrs/pcrs/wsgi.py ${FILEPATH}/pcrsloader/backup/pcrs/wsgi.py.${DATE}.$2
mv pcrs/login.py ${FILEPATH}/pcrsloader/backup/login.py.${DATE}.$2

echo "Updating code"
git remote set-url origin https://$1@bitbucket.org/utmandrew/pcrs.git

# Uncomment the below if you need a specific new branch
# git checkout <branch-name>

# Uncomment the below if there are changes to destroy
# git reset --hard

git pull

echo "Don't forget to check settings.py, wsgi.py, and login.py"
mv pcrs/pcrs/settings.py pcrs/pcrs/settings.py.${DATE}
mv pcrs/pcrs/wsgi.py pcrs/pcrs/wsgi.py.${DATE}
mv pcrs/login.py pcrs/login.py.${DATE}
cp ${FILEPATH}/pcrsloader/backup/settings.py.${DATE}.$2 pcrs/pcrs/settings.py
cp ${FILEPATH}/pcrsloader/backup/wsgi.py.${DATE}.$2 pcrs/pcrs/wsgi.py
cp ${FILEPATH}/pcrsloader/backup/login.py.${DATE}.$2 pcrs/login.py

echo "Syncing database"
pushd pcrs
python3.4 manage.py syncdb
echo "Collecting static"
python3.4 manage.py collectstatic

echo "Setting permissions"
find . -type d -exec chmod 750 {} \;
chmod 755 .
find . -type f -exec chmod 640 {} \;
popd

find static -type d -exec chmod 775 {} \;
find static -type f -exec chmod 664 {} \;

# Hack to fix fonts issue
rm -f static/fonts
ln -s static/bootstrap-3.1.1/fonts static/fonts

popd
