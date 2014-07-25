import challenge_graph as chgraph
import gv
import re
import sys
from bs4 import BeautifulSoup
import urllib2
import json
import random

def  manipulateSoup(soup):
	''' Removes all svg polygon elements and replaces 
		them with svg rect elements.'''
	for g in soup.findAll('g', { "class" : "node" }):
		for poly in g.findAll('polygon'):
			coords = poly['points'].split()
	        xRect = float(coords[1].split(",")[0]);
	        yRect = float(coords[0].split(",")[1]);
	        width = abs(float(coords[2].split(",")[0]) - float(coords[0].split(",")[0]))
	        height = abs(float(coords[2].split(",")[1]) - float(coords[0].split(",")[1]))
	        rect =  createRect(xRect, yRect, width, height)
	        g.insert(1, rect.rect)
	        poly.extract()

def createRect(xRect, yRect, rectWidth, rectHeight):
	''' Creates an svg rect with x = xRect, y = yRect, 
		width = rectWidth and height = rectHeight. '''
	rect = BeautifulSoup("<rect rx='20' ry='20' class='rect' x='" 
						+ str(xRect)
						+ "' y='" 
						+ str(yRect) 
						+ "' width='" 
						+ str(rectWidth) 
						+ "' height='" 
						+ str(rectHeight) 
						+ "'></rect>")
	return rect

def customizeQuests(soup, topicDict):
	keys = topicDict.keys()
	quests = {}
	for g in soup.findAll("g", { "class" : "node" }):
		text = []
		for t in g.findAll("text"):
			text.append(t.string)

		# As the nodes are split up, they need to be joined together
		text = "".join(text)

		# As the nodes have newlines and spaces inserted into them, they need to be taken out for comparison
		# against the string from the graph input.
		text = text.replace(" ", "")
		text = text.replace("\n", "")
		for i in range(0, len(topicDict)):
			comparisonText = topicDict[keys[i]]['name']
			comparisonText = comparisonText.replace(" ", "")
			comparisonText = comparisonText.replace("\n", "")
			if text == comparisonText:
				if not topicDict[keys[i]]['quest'] in quests:
					r = lambda: random.randint(0,255)
					colour = '#%02X%02X%02X' % (r(), r(), r())
					quests[topicDict[keys[i]]['quest']] = colour
				g.rect["stroke"] = quests[topicDict[keys[i]]['quest']]

def getJSON():
	# graphContent = urllib2.urlopen("").read()
	# dictContent = json.loads(graphContent)
	# Must import ast for next line to work
	# ast.literal_eval(graphContent)
	dictContent = {34530: {'name' : 'Python as a Calculator', 'prerequisites' : [],'quest' : '0'},
	123452: {'name' : 'Python and Computer Memory','prerequisites' : [34530],'quest' : '1'}, 
	23453422: {'name' : 'Ian','prerequisites' : [34530],'quest' : '1123'},
	34543543: {'name' : 'Curly!','prerequisites' : [23453422],'quest' : '1'},
	34534534: {'name' : 'Moe!','prerequisites' : [34543543],'quest' : '132123'},
	23432234: {'name' : 'Moe','prerequisites' : [34534534],'quest' : '1'},
	43543434: {'name' : 'Moe2','prerequisites' : [34534534],'quest' : '1'},
	345343345: {'name' : 'Moe3','prerequisites' : [34534534],'quest' : '132123'},
	28545640: {'name' : 'Curly','prerequisites' : [23432234],'quest' : '1'},
	234322342: {'name' : 'Curly2','prerequisites' : [23432234],'quest' : '132123'},
	76745560: {'name' : 'Larry','prerequisites' : [28545640],'quest' : '1'},
	54345634: {'name' : 'Tom','prerequisites' : [76745560],'quest' : '1'},
	34554332: {'name' : 'Jerry','prerequisites' : [54345634],'quest' : '1'},
	34554343: {'name' : 'Zoro','prerequisites' : [34554332],'quest' : '1'},
	34543355: {'name' : 'Valerie','prerequisites' : [34554343],'quest' : '132123'},
	32342333: {'name' : 'Valerie2','prerequisites' : [34554343],'quest' : '1'},
	43223444: {'name' : 'Valerie3','prerequisites' : [34554343],'quest' : '1'},
	23432233: {'name' : 'Valerie34','prerequisites' : [43223444],'quest' : '1'},
	34543243: {'name' : 'Maria', 'prerequisites' : [34543355],'quest' : '1'},
	23432344: {'name' : 'Stanley', 'prerequisites' : [34543243],'quest' : '1'},
	23442323: {'name' : 'Davidov', 'prerequisites' : [23432344],'quest' : '1'},
	23443223: {'name' : 'Gerald', 'prerequisites' : [23442323],'quest' : '1'},
	43233342: {'name' : 'Harold', 'prerequisites' : [23443223],'quest' : '1'},

	}
	return dictContent

def outputGraph():
	dictContent = getJSON()
	graphData = chgraph.createGraph(dictContent)
	soup = BeautifulSoup(''.join(graphData))

	# Since graphViz doesn't provide the defs we want, we need to append them
	soupDefs = BeautifulSoup("<defs></defs>")
	soupDefs.defs.append(BeautifulSoup("<pattern id='play-image' width='15' height='15'><image xlink:href='./video.png' x='-1.35' y='-1.35' width='23' height='23' /></pattern>").pattern)
	soupDefs.defs.append(BeautifulSoup("<pattern id='active-image' width='10' height='10'><image xlink:href='./check.ico' x='3' y='3' width='14' height='14' /></pattern>").pattern)
	soup.svg.insert(0, soupDefs.defs)
	manipulateSoup(soup)

	# Remove title elements created by GraphViz
	titles = soup.findAll("title")
	for title in titles:
		title.extract()
	customizeQuests(soup, dictContent)
	f = open("../ui/graph_gen.svg", "w")
	f.write(soup.svg.prettify().encode('utf-8'))
	f.close()

if __name__ == "__main__":
	# # Week 1
	# w_1_t_1 = "Python as a Calculator"
	# w_1_t_2 = "Python and Computer Memory"
	# w_1_t_3 = "Variables"
	# w_1_t_4 = "Visualizing Assignment Statements"
	# w_1_t_5 = "Built-in Functions"
	# w_1_t_6 = "Defining Functions"

	# # Week 2
	# w_2_t_1 = "Type str"
	# w_2_t_2 = "Input/Output and str Formatting"
	# w_2_t_3 = "Docstrings and Function help"
	# w_2_t_4 = "Function Design Recipe"
	# w_2_t_5 = "Function Reuse"
	# w_2_t_6 = "Visualizing Function Calls"

	# # Week 3
	# w_3_t_1 = "Functions, Variables and the Call Stack"
	# w_3_t_2 = "Type bool"
	# w_3_t_3 = "Converting between int, str, and float"
	# w_3_t_4 = "if statements"
	# w_3_t_5 = "No if required"
	# w_3_t_6 = "Structuring if statements"

	# # Week 4
	# w_4_t_1 = "Import: Using Non-Built-in Functions"
	# w_4_t_2 = "More str operators"
	# w_4_t_3 = "str: indexing and slicing"
	# w_4_t_4 = "str Methods: Functions Inside of Objects"
	# w_4_t_5 = "for loop over str"
	# w_4_t_6 = "Wing's debugger"
	# w_4_t_7 = "while loops"

	# # Week 5
	# w_5_t_1 = "Comments"
	# w_5_t_2 = "Type list"
	# w_5_t_3 = "list methods"
	# w_5_t_4 = "for loops over indicies"
	# w_5_t_5 = "range"
	# w_5_t_6 = "Mutability and Aliasing"

	# # Week 6
	# w_6_t_1 = "Parallel Lists and Strings"
	# w_6_t_2 = "Nested List"
	# w_6_t_3 = "Writing Files"
	# w_6_t_4 = "Nested Loops"
	# w_6_t_5 = "Reading Files"
	# w_6_t_6 = "Developing a program"

	# # Week 7
	# w_7_t_1 = "Tuples"
	# w_7_t_2 = "Type Dict"
	# w_7_t_3 = "Inverting a Dictionary"
	# w_7_t_4 = "Populating a Dictionary"

	# # Week 8
	# w_8_t_1 = "Palindrome: Approaching the Problem"
	# w_8_t_2 = "Palindrome: Algorithm 1"
	# w_8_t_3 = "Palindrome: Algorithm 2"
	# w_8_t_4 = "Palindrome: Algorithm 3"
	# w_8_t_5 = "Restaurant Recommendations Problem"
	# w_8_t_6 = "Restaurant Recommendations: Representing the Data"
	# w_8_t_7 = "Restaurant Recommendations: Planning the Program"

	# # Week 9
	# w_9_t_1 = "Testing Automatically Using doctest"
	# w_9_t_2 = "Writing a '__main___' program"
	# w_9_t_3 = "Creating Your Own Types"
	# w_9_t_4 = "Testing Automatically Using unittest"
	# w_9_t_5 = "Choosing Test Cases"
	# w_9_t_6 = "Testing Functions that Mutate Values"

	# # Week 10
	# w_10_t_1 = "Analyzing Algorithms"
	# w_10_t_2 = "Linear Search"
	# w_10_t_3 = "Binary Search"
	# w_10_t_4 = "Comparing Search Algorithms"
	# w_10_t_5 = "Bubble Sort"
	# w_10_t_6 = "Selection Sort"
	# w_10_t_7 = "Insertion sort"

	# # Week 11
	# w_11_t_1 = "Creating a New Type"
	# w_11_t_2 = "Creating a New Type"
	# w_11_t_3 = "Writing Special Method __str__"
	# w_11_t_4 = "Writing Classes that Interact"

	# # Week 12
	# w_12_t_1 = "Passing Functions as Arguments"
	# w_12_t_2 = "Assigning Parameters Default Values"
	# w_12_t_3 = "Dealing with Exceptional Situations"

	# # Initialize prerequisites for each node
	# w_1_t_1_prereqs = [w_1_t_1, w_1_t_3, w_1_t_5]
	# w_1_t_2_prereqs = [w_1_t_2, w_1_t_4]
	# w_1_t_3_prereqs = [w_1_t_3, w_1_t_2]
	# w_1_t_4_prereqs = [w_1_t_4, w_1_t_6, w_2_t_1, w_3_t_2]
	# w_1_t_5_prereqs = [w_1_t_5, w_1_t_6] # Built-in Functions
	# w_1_t_6_prereqs = [w_1_t_6, w_8_t_5, w_2_t_3, w_2_t_2] # Defining Functions

	# # Week 2
	# w_2_t_1_prereqs = [w_2_t_1, w_2_t_2] # Type str
	# w_2_t_2_prereqs = [w_2_t_2, w_2_t_3, w_3_t_3, w_4_t_2] # Input/Output and str Formatting
	# w_2_t_3_prereqs = [w_2_t_3, w_2_t_4] # Docstrings and Function help
	# w_2_t_4_prereqs = [w_2_t_4, w_2_t_6, w_2_t_5, w_3_t_4, w_4_t_1, w_8_t_1] # Function Design Recipe
	# w_2_t_5_prereqs = [w_2_t_5] # Function Reuse
	# w_2_t_6_prereqs = [w_2_t_5, w_3_t_1, w_3_t_6] # Visualizing Function Calls

	# # Week 3
	# w_3_t_1_prereqs = [w_3_t_1, w_4_t_6] # Functions, Variables and the Call Stack
	# w_3_t_2_prereqs = [] # Type bool
	# w_3_t_3_prereqs = [] # Converting between int, str, and float
	# w_3_t_4_prereqs = [] # if statements
	# w_3_t_5_prereqs = [] # No if required
	# w_3_t_6_prereqs = [] # Structuring if statements

	# # Week 4
	# w_4_t_1_prereqs = [] # Import: Using Non-Built-in Functions
	# w_4_t_2_prereqs = [] # More str operators
	# w_4_t_3_prereqs = [] # str: indexing and slicing
	# w_4_t_4_prereqs = [] # str Methods: Functions Inside of Objects
	# w_4_t_5_prereqs = [] # for loop over str
	# w_4_t_6_prereqs = [] # Wing's debugger
	# w_4_t_7_prereqs = [] # while loops

	# # Week 5
	# w_5_t_1_prereqs = [] # Comments
	# w_5_t_2_prereqs = [] # Type list
	# w_5_t_3_prereqs = [] # list methods
	# w_5_t_4_prereqs = [] # for loops over indicies
	# w_5_t_5_prereqs = [] # range
	# w_5_t_6_prereqs = [] # Mutability and Aliasing

	# # Week 6
	# w_6_t_1_prereqs = [] # Parallel Lists and Strings
	# w_6_t_2_prereqs = [] # Nested List
	# w_6_t_3_prereqs = [] # Writing Files
	# w_6_t_4_prereqs = [] # Nested Loops
	# w_6_t_5_prereqs = [] # Reading Files
	# w_6_t_6_prereqs = [] # Developing a program

	# # Week 7
	# w_7_t_1_prereqs = [] # Tuples
	# w_7_t_2_prereqs = [] # Type Dict
	# w_7_t_3_prereqs = [] # Inverting a Dictionary
	# w_7_t_4_prereqs = [] # Populating a Dictionary

	# # Week 8
	# w_8_t_1_prereqs = [] # Palindrome: Approaching the Problem
	# w_8_t_2_prereqs = [] # Palindrome: Algorithm 1
	# w_8_t_3_prereqs = [] # Palindrome: Algorithm 2
	# w_8_t_4_prereqs = [] # Palindrome: Algorithm 3
	# w_8_t_5_prereqs = [] # Restaurant Recommendations Problem
	# w_8_t_6_prereqs = [] # Restaurant Recommendations: Representing the Data
	# w_8_t_7_prereqs = [] # Restaurant Recommendations: Planning the Program

	# # Week 9
	# w_9_t_1_prereqs = [] # Testing Automatically Using doctest
	# w_9_t_2_prereqs = [] # Writing a '__main___' program
	# w_9_t_3_prereqs = [] # Creating Your Own Types
	# w_9_t_4_prereqs = [] # Testing Automatically Using unittest
	# w_9_t_5_prereqs = [] # Choosing Test Cases
	# w_9_t_6_prereqs = [] # Testing Functions that Mutate Values

	# # Week 10
	# w_10_t_1_prereqs = [] # Analyzing Algorithms
	# w_10_t_2_prereqs = [] # Linear Search
	# w_10_t_3_prereqs = [] # Binary Search
	# w_10_t_4_prereqs = [] # Comparing Search Algorithms
	# w_10_t_5_prereqs = [] # Bubble Sort
	# w_10_t_6_prereqs = [] # Selection Sort
	# w_10_t_7_prereqs = [] # Insertion sort

	# # Week 11
	# w_11_t_1_prereqs = [] # Creating a New Type
	# w_11_t_2_prereqs = [] # Creating a New Type
	# w_11_t_3_prereqs = [] # Writing Special Method __str__
	# w_11_t_4_prereqs = [] # Writing Classes that Interact

	# # Week 12
	# w_12_t_1_prereqs = [] # Passing Functions as Arguments
	# w_12_t_2_prereqs = [] # Assigning Parameters Default Values
	# w_12_t_3_prereqs = [] # Dealing with Exceptional Situations

	# # Initialize topic array (list of node prereq lists)
	# prereqs = [w_1_t_1_prereqs, w_1_t_2_prereqs, w_1_t_3_prereqs, w_1_t_4_prereqs, w_1_t_5_prereqs, w_1_t_6_prereqs, w_2_t_1_prereqs, w_2_t_2_prereqs, w_2_t_3_prereqs, w_2_t_4_prereqs, w_2_t_5_prereqs, w_2_t_6_prereqs]


	# Initialize graph
	
	outputGraph()