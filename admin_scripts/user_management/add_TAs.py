import sys

# Usage:
#   add <TAlist file> <section name>
# Globals:

sqlfile = open("TA.sql", "w")
with open(sys.argv[1]) as tafile:
    for TA in tafile:
        TA = TA.strip()
        sqlfile.write("insert into users_pcrsuser (last_login, username, section_id, code_style, is_student, is_ta, is_instructor, is_active, is_admin, is_staff) values (CURRENT_TIMESTAMP, '%s', '%s', 0, False, True, False, True, False, True);\n" % (TA, sys.argv[2]))

