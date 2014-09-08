import sys
import csv

# Usage:
#   add <current_classlist> <past_classlist> 
# Globals:
dbname = "StG108"
section = "123"

past_users = []
with open(sys.argv[2]) as csvfile:
    past_cl = csv.reader(csvfile, delimiter=",")
    for row in past_cl:
        past_users.append(row[0])

new_users = []
with open(sys.argv[1]) as csvfile:
    curr_cl = csv.reader(csvfile, delimiter=",")
    for row in curr_cl:
        if row[0] not in past_users:
            new_users.append(row[0])
        else:
            past_users.remove(row[0])

# Any new_users need accounts.
# Any past_users have dropped and should become inactive.

with open(dbname + ".sql", "w") as sqlfile:

    sqlfile.write("COPY users_pcrsuser (last_login, username, section_id, code_style, is_student, is_ta, is_instructor, is_active, is_admin, is_staff) from STDIN;\n")
    for user in new_users:
        sqlfile.write("2013-09-10 12:00:00.000000-04\t%s\t%s\t0\tTrue\tFalse\tFalse\tTrue\tFalse\tFalse\n" % (user, section))
    sqlfile.write("\\.\n")

    for user in past_users:
        sqlfile.write("UPDATE users_pcrsuser SET is_active = False where username = '%s';\n" % (user))

