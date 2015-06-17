import sys
import string 

def split_by_delim(str_to_split, delim1, delim2):

	newlist = string.split(str_to_split, delim1)
	#print(newlist)
	for thingy in newlist:
		newlist2 =string.split(thingy, delim2)
		newlist2 = filter(None, newlist2) # fastest
		print(newlist2) 