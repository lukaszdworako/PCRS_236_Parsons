import sys
import csv

# Usage:
#   add <current_classlist> <past_classlist> 
# Globals:
dbname = "UTM108"

past_users = []
user_section = {}
with open(sys.argv[2]) as csvfile:
    past_cl = csv.reader(csvfile, delimiter=",")
    for row in past_cl:
        past_users.append(row[0])
        user_section[row[0]] = row[3]

sqlfile = open(dbname + ".sql", "w")
with open(sys.argv[1]) as csvfile:
    curr_cl = csv.reader(csvfile, delimiter=",")
    for row in curr_cl:
        if "0102" in row[3]:    # Online
            section = "123"
        else:
            section = "Lecture"

        if row[0] not in past_users:
            sqlfile.write("insert into users_pcrsuser (last_login, username, section_id, code_style, is_student, is_ta, is_instructor, is_active, is_admin, is_staff) values (CURRENT_TIMESTAMP, '%s', '%s', 0, True, False, False, True, False, False);\n" % (row[0], section))
        else:
            past_users.remove(row[0])
            if row[3] != user_section[row[0]]:
                sqlfile.write("UPDATE users_pcrsuser SET section_id = '%s' where username = '%s';\n" % (section, row[0]))

# Any past_users have dropped and should become inactive.
for user in past_users:
    sqlfile.write("UPDATE users_pcrsuser SET is_active = False where username = '%s';\n" % (user))