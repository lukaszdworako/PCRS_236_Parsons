import gv
import re
import sys

def createGraph(topicDict):
	''' Builds, renders and lays out a graph based on prerequisite information from topicArray. '''
	graph = gv.strictdigraph("Challenge Dependency Graph")
	processChallenges(topicDict, graph)
	initializeGraph(graph)
	return renderAndLayoutGraph(graph)

def processChallenges(l, graph):
	''' Processes list l with a root node l[0], and all subsequent indices as child nodes. 
		Note: GraphViz will read in identical text as identical nodes. 
		      Only one node will be initialized, even if gv.node() is called multiple times 
		      with the same string contents.
	'''
	if len(l) == 0:
		return
	keys = l.keys()
	for i in range(0, len(l)):
		label = addNewlines(l[keys[i]]['name'])
		root = gv.node(graph, str(keys[i]))
		initializeNode(root, label)
		gv.setv(root, "id", str(keys[i]))
		for li in l[keys[i]]['prerequisites']:
			label = addNewlines(l[li]['name'])
			node = gv.node(graph, str(li))
			gv.setv(node, "id", str(li))
			initializeNode(node, label)
			edge = gv.edge(node, root)

def addNewlines(text):
	''' Adds newlines to text in order to decrease node size. '''
	if len(text) > 8:
		spaces = list(re.finditer(" ", text))
		words = text.split()
		sys.stderr.write(str(words))
		text = ""
		wordCounter = 0
		for word in words:
			wordCounter += 1
			if len(word) > 5 or wordCounter >= 2:
				wordCounter = 0
				text = text + str(word) + "\n"
			else:
				text = text + str(word) + " "
	return text;

def initializeNode(node, label):
	''' Initializes the GraphViz node attributes '''
	gv.setv(node, "shape", "rect")
	gv.setv(node, "height", ".4")
	gv.setv(node, "width", "1")
	gv.setv(node, "margin", "0.5, 0.05")
	gv.setv(node, "label", label)

def initializeGraph(graph):
	''' Initializes the GraphViz graph attributes '''
	gv.setv(graph, "splines", "ortho")
	gv.setv(graph, "concentrate", "true")
	gv.setv(graph, "rank", "same")
	gv.setv(graph, "center", "true")
	gv.setv(graph, "mode", "ipsep")
	gv.setv(graph, "overlap", "false")      
	gv.setv(graph, "rankdir", "LR")
	gv.setv(graph, "height", "10")
	gv.setv(graph, "width", "10")
	gv.setv(graph, "nodesep", ".5")

def renderAndLayoutGraph(graph):
	''' Renders and lays out graph.'''
	gv.layout(graph, "dot")
	output = gv.renderdata(graph, "svg")
	return output