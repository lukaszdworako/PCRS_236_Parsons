#!/bin/python3
import subprocess
import sys
import os
import pwd
import secrets

PCRSPlugins = [["Python", "'problems_python': 'Python',"], ["C", "'problems_c': 'C',"], ["Java", "'problems_java': 'Java',"], ["SQL", "'problems_sql': 'SQL',"], ["Relational Algebra", "'problems_ra': 'Relational Algebra',"], ["Multiple Choice", "'problems_multiple_choice': '',"], ["Short Answer", "'problems_short_answer': '',"]]

if ("proc" not in sys.path[0] and "dev" not in sys.path[0]):
    os.chdir(sys.path[0])
else:
    pathing = input("Enter the path for the source files: ")
    try:
        os.chdir(pathing.replace("~", os.environ['HOME']))
        print(os.getcwd())
    except FileNotFoundError:
        print("An invalid folder was given. Halting.")
        sys.exit(1)

print("System Information\n")
#Print some general info, if they don't have lsb_release
#installed, its not a huge deal.
try:
    result = subprocess.Popen(["lsb_release", "-a"], stdout=subprocess.PIPE)
    out, err = result.communicate()
    print(bytes.decode(out, "UTF-8"))
except FileNotFoundError:
    pass

#Look into their python version...
if sys.version_info[0] == 3:
    if sys.version_info[1] == 6:
        print("Python Ver:\t3.6." + str(sys.version_info[2]))
    else:
        print("\nPython 3.6.X is required for this software.")
        sys.exit(1)
else:
    print("\nPython 3.6.X is required for this software.")
    sys.exit(1)

#Look into their postgres version
try:
    result = subprocess.Popen(["psql", "--version"], stdout=subprocess.PIPE)
    out, err = result.communicate()
    out = bytes.decode(out, "UTF-8")
    postgresVer = out.split(" ")[2].split(".")
    if postgresVer[0] == "9" and postgresVer[1] == "6":
        print("Postgres Ver:\t" + ".".join(postgresVer).rstrip("\n"))
    else:
        print("Postgres Ver:\t" + ".".join(postgresVer).rstrip("\n") + " (NOT TESTED)")
except FileNotFoundError:
    print("Postgres 9.6.X is required for this software.")
    sys.exit(1)

#GCC is next!
try:
    result = subprocess.Popen(["gcc", "--version"], stdout=subprocess.PIPE)
    out, err = result.communicate()
    out = bytes.decode(out, "UTF-8")
    GCCVer = out.split(" ")[2].split(".")
    if GCCVer[0] == "4" and GCCVer[1] == "9" and GCCVer[2] == "2":
        print("GCC Ver:\t" + ".".join(GCCVer))
    else:
        print("GCC Ver:\t" + ".".join(GCCVer) + " (NOT TESTED)")
except FileNotFoundError:
    print("GCC 4.9.2 is required for C PCRS.")

#A touch of java
try:
    #Because java prints this to stderr.....
    result = subprocess.Popen(["javac", "-version"], stderr=subprocess.PIPE)
    out, err = result.communicate()
    err = bytes.decode(err, "UTF-8")
    JavaVer = err.split(" ")[1].split(".")
    if JavaVer[0] == "1" and JavaVer[1] == "7":
        print("Java JDK Ver:\t" + ".".join(JavaVer).rstrip("\n"))
    else:
        print("Java JDK Ver:\t" + ".".join(JavaVer).rstrip("\n") + " (NOT TESTED)")
except FileNotFoundError:
    print("Java JDK is required for Java PCRS.")

#Now that we know some stuff about the enviroment,
#Lets start to customize the install.
wsgiUser = input("Enter the user which will run PCRS: ")
prefix = ""
print("\nHow would you like to install PCRS?")
print("1) Apache with mod_wsgi")
print("2) Django runserver (not recomended in production)")
while True:
    installType = input("Select an option: ")
    if installType != "1" and installType != "2":
        print("Not a valid selection.")
    else:
        break
if installType == "1":
    print("The server prefix is used to allow multiple PCRS instances to run on a single server.")
    prefix = input("Enter the server prefix: ")
    webDirectory = input("Enter the web directory PCRS is located in: ")
    wsgiGroup = input("Enter the group of the user which will run PCRS: ")
    #HTTPD Config
    file = open("PCRSHttpd.conf", "w")
    file.write("""Alias /""" + prefix + """/static """ + webDirectory + """
<Directory """ + webDirectory + """>
    Order deny,allow
    Allow from all
</Directory>

WSGIDaemonProcess pcrs_""" + prefix + """ user=""" + wsgiUser + """ group=""" + wsgiGroup + """ processes=5
WSGIScriptAlias /""" + prefix + """ """ + webDirectory + """/wsgi.py
<Directory """ + webDirectory + """>
    <Files wsgi.py>
        Order deny,allow
        Allow from all
    </Files>
</Directory>
""")
    file.close()
    file = open("PCRSwsgi.py", "w")
    file.write("""import os
import sys

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "pcrs.settings"
sys.path.append(\"""" + webDirectory + """\")
os.environ["DJANGO_SETTINGS_MODULE"] = "pcrs.settings"

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
    _application = get_wsgi_application()""")
    file.close()
    print("PCRSHttps.conf and PCRSwsgi.py have been created with your settings.")
    print("Location: " + os.getcwd())

clone = input("Clone git repo? (Y/n)")
if clone.lower() == "y" or clone == "":
    try:
        result = subprocess.Popen(["git clone https://bitbucket.org/utmandrew/pcrs.git && cd pcrs"], shell=True)
        result.wait()
        os.chdir("pcrs/pcrs")
    except FileNotFoundError:
        path("GIT is unavaliable.")
        sys.exit(1)
else:
    print("This might not work (Needs a definitive home first)")
    os.chdir("../pcrs")

virt = input("Setup virtual env? (Y/n): ")
if virt.lower() == "y" or virt=="":
    virtPath = input("Enter a path for the virtual enviroment: ")
    virtPath = virtPath.replace("~", os.environ['HOME'])
    tryAgain = True
    continueVirt = True
    while tryAgain:
        try:
            result = subprocess.Popen(["virtualenv", "-p", sys.executable, virtPath])
            result.wait()
            if result.returncode != 0:
                print("An error occured while creating the virtualenv")
                sys.exit(1)
            tryAgain = False
        except FileNotFoundError:
            print("virtualenv not found. Install the following packages: virtualenv virtualenvwrapper")
            print("a) Abort")
            print("r) Retry")
            print("s) Skip")
            abortInstall = input("Selection: ")
            if abortInstall.lower() == "a":
                print("Aborting.")
                sys.exit(2)
            elif abortInstall.lower() == "s":
                tryAgain = False
                continueVirt = False
    if continueVirt:
         try:
            print("Installing pip packages")
            result = os.system("source `which virtualenvwrapper.sh` && export WORKON_HOME=" + os.path.dirname(virtPath) + " && workon " + os.path.basename(virtPath) + " && sudo pip3 install -r requirements.txt")
            if result != 0:
                print("An error occured while configuring the virtual enviroment")
                sys.exit(1)
            tryAgain = False
         except FileNotFoundError:
             print("Prerequisite packages missing. Aborting.")
             sys.exit(1)

print("Preparing Config")
safeExecEnabled = False
sqlEnabled = False
rdbEnabled = False
userConfig = """INSTALLED_PROBLEM_APPS = {
"""
for plugin in PCRSPlugins:
    enable = input("Enable " + plugin[0] + "? (Y/n): ")
    if enable.lower() == "y" or enable == "":
        userConfig += plugin[1] + "\n"
        if plugin[0] == "C":
            safeExecEnabled = True
        elif plugin[0] == "SQL":
            rdbEnabled = sqlEnabled = True
        elif plugin[0] == "Relational Algebra":
            rdbEnabled = True
if rdbEnabled:
    userConfig += "'problems_rdb': ''\n"
userConfig += "}\n"
if safeExecEnabled:
    userConfig += """\nUSE_SAFEEXEC = True
SAFEEXEC_USERID = """ + str(pwd.getpwnam(wsgiUser).pw_uid) + """
SAFEEXEC_GROUPID = """ + str(pwd.getpwnam(wsgiUser).pw_gid) + """
"""

production = input("Enable production mode? Answering n will enable debugging messages. (Y/n): ")
if production.lower() == "n":
    userConfig += """
PRODUCTION = False
DEBUG = True
"""

if sqlEnabled:
    sqlDebug = input("Enable SQL debugging? (Y/n): ")
    if sqlDebug.lower() == "y" or sqlDebug == "":
        userConfig += """
SQL_DEBUG = True
"""
    studentDatabase = input("Enter the database for PCRS SQL: ")
    userConfig += """RDB_DATABASE = '""" + studentDatabase

print("Admin Information (Email Notifications)")
userConfig += "\nADMINS = ("
while True:
    adminName = input("Enter an Admin name (Blank to stop): ")
    if adminName == "":
        break
    adminEmail = input("Enter the Admin's email.")
    userConfig += "\n('" + adminName + "', '" + adminEmail + "'),"

userConfig += "\n)\nMANAGERS = ADMINS\n"

print("Database Information")
dbName = input("Enter the database name: ")
dbUser = input("Enter the database user: ")
dbPass = input("Enter the password for user " + dbUser + ": ")
dbHost = input("Enter the database host (Empty for localhost): ")
dbPort = input("Enter the database port (Empty for default): ")
userConfig += """
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '""" + dbName + """',
        'USER': '""" + dbUser + """',
        'PASSWORD': '""" + dbPass + """',
        'HOST': '""" + ("localhost" if dbHost == "" else dbHost) + """',
        'PORT': '""" + dbPort + """',
    }
}"""

#Site prefixing (We know this info already)
userConfig += """
\nSITE_PREFIX = '""" + prefix + """'
FORCE_SCRIPT_NAME = SITE_PREFIX
LOGIN_URL = SITE_PREFIX + '/login'"""

print("Select an authentication method:")
print("1) shibboleth")
print("2) pwauth")
print("3) pass")
print("4) none (*DANGEROUS*)")
authSelection = input("Selection: ")
authSelection = "shibboleth" if authSelection == "1" else "pwauth" if authSelection == "2" else "pass" if authSelection == "3" else "none"
userConfig += """
AUTH_TYPE = '""" + authSelection + """'
AUTOENROLL = False
"""

allowedHosts = []
print("Allowed hosts (Required in production)")
while True:
    host = input("Enter a host (Blank to stop): ")
    if host == "":
        break
    allowedHosts.append(host)

userConfig += """
ALLOWED_HOSTS = """ + repr(allowedHosts)

secretToken = secrets.token_urlsafe(37)
userConfig += """
SECRET_KEY = '""" + secretToken + """'

"""

print("Writing Config...")
file = open("pcrs/settings_local.py", "w")
file.write(userConfig)
file.close()
print("Config Generated!")
