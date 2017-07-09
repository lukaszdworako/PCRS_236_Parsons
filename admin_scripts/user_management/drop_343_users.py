import psycopg2

user_query = 'select username from users_pcrsuser where is_student=true;'
drop_user = 'drop role {0};'

db = psycopg2.connect(dbname='343')
cursor = db.cursor()

cursor.execute(user_query)
output = [user for row in cursor.fetchall() for user in row]

for user in output:
    print(drop_user.format(user))
