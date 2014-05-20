import sys

def help_msg():
    print("add_users.py <start_id> <instructor|ta|student> <input_file>")
    sys.exit()

def b2s(cond):
    if cond:
        return "t"
    return "f"

if len(sys.argv) != 4:
    help_msg()

id = int(sys.argv[1])
is_student = sys.argv[2] == "student"
is_admin =sys.argv[2] == "instructor"
is_instructor = is_admin or sys.argv[2] == "ta"
if not (is_student or is_instructor):
    help_msg()
is_student = b2s(is_student)
is_admin = b2s(is_admin)
is_instructor = b2s(is_instructor)

f = open(sys.argv[3], "r")
print("COPY instructor_pcrsuser (id, last_login, username, section_id, is_student, is_instructor, is_active, is_admin, is_staff) FROM stdin;")
for utorid in f:
    next_line = [str(id), "2013-09-10 12:00:00.000000-04", utorid.strip(), "\\N", is_student, is_instructor, "t", is_admin, is_instructor]
    print("\t".join(next_line))
    id = id + 1

print("\\.\nSELECT pg_catalog.setval('instructor_pcrsuser_id_seq', %d, true);" % id)
