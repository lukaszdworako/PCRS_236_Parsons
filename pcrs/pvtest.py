# Quickly test the functionality of the array value parsing in the CSpecifics() class in c_language.py
# Run with "cat pvtest.py | python manage.py shell"

from problems_c.c_language import *
from pprint import pprint

c = CSpecifics('gooby', None)
current_var = {
    'value': [ ['0x11','0x12'], ['0x13','0x14'], ['0x15','0x16'] ],
    'hex_value': [ ['0x0001','0x0002'], ['0x0003', '0x0004'], ['0x0005','0x0006'] ] ,
    'type': 'int*[][]',
    'addr': '0x1111222233334444',
    'location': 'stack'
}
sizes_by_level = [3,2,2]

result = c.parse_value(current_var, sizes_by_level)
print() ; print() ; pprint(result) ; print()
