# Quickly test the functionality of the array value parsing in the CSpecifics() class in c_language.py
# Run with "cat pvtest.py | python manage.py shell"

from problems_c.c_language import *
from pprint import pprint

c = CSpecifics('gooby', None)
current_var = {
    'value': ['1', '2', '3'],
    'hex_value': ['0x01','0x02', '0x03'] ,
    'type': 'int[]',
    'addr': '0x1111222233334444',
    'location': 'stack'
}
sizes_by_level = [3,2]

current_var['value'] = c.parse_value(current_var, sizes_by_level)
print() ; print() ; pprint(current_var) ; print()
