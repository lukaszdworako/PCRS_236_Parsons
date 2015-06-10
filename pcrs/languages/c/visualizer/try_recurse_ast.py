#NOTE: This is a small snippet of code that I will build into the visualizer once
#I'm sure it's working. It adds printf statements after each variable declaration 
#or assignment - right now it doesn't add anything useful, but once I figure out
#exactly what information we'll need from each variable, I will change it to add that.

#-------------------------------------------------------------------------------
# pycparser: using_gcc_E_libc.py
#
# Similar to the using_cpp_libc.py example, but uses 'gcc -E' instead
# of 'cpp'. The same can be achieved with Clang instead of gcc. If you have
# Clang installed, simply replace 'gcc' with 'clang' here.
#
# Copyright (C) 2008-2015, Eli Bendersky
# License: BSD
#-------------------------------------------------------------------------------
import sys
import pdb
# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
#
sys.path.extend(['.', '..'])

from pycparser import parse_file, c_ast, c_generator

#WILL CHANGE THIS TO BE VARIABLE SPECIFIC INSTEAD OF HELLO WORLD, ONCE WE FIGURE OUT WHAT WE NEED
def create_printf_node():
    add_id = c_ast.ID('printf')
    add_const = c_ast.Constant('string', '"12345"')
    add_exprList = c_ast.ExprList([add_const])
    new_node = c_ast.FuncCall(add_id, add_exprList)
    return new_node


def recurse_nodes(parent):
    print(parent)
    if parent.coord:
        print(parent.coord.line)
    for child in parent.children():
        print(child[0])
        recurse_nodes(child[1])

def new_recurse_nodes(index,parent):
    print("parent is:")
    print(parent)
    print("current child is:")
    print(parent[index])
    if parent[index].coord:
        print(parent[index].coord.line)
    amt_of_children = len(parent.children)
    for i in range(0, amt_of_children):
        #print(child[0])
        new_recurse_nodes(i, parent[index])

def check_if_added_printf(node):
    if isinstance(node, c_ast.FuncCall) and isinstance(node.args.exprs[0], c_ast.Constant) and (node.args.exprs[0].value =='"12345"'):
        return True
    else:
        return False

#Splits up the AST by function, continues to recurse if a node has a compound node
def recurse_by_function(ast):
    i = 0
    while i < len(ast.ext):
        recurse_by_compound(ast.ext, i)
        i+= 1

def recurse_by_compound(parent, index):
    #Note:ast.ext[0] gets the first function, .body gets the stuff under Compound, and block_items gets each group of elements under Compound
    #pdb.set_trace()

    #If node is a print statement we added, ignore it & return
    if parent[index].coord == None:
        return

    ast_function = parent[index]
    print(ast_function)
    print(ast_function.coord)
    handle_nodetypes(parent, index)
    try:
        compound_list = ast_function.body.block_items
    except AttributeError:
        try:
            compound_list = ast_function.stmt.block_items
        except AttributeError:
            try:
                compound_list = ast_function.iftrue.block_items
            except:
                try:
                    compound_list = ast_function.iffalse.block_items
                except:
                    return
    #total_len = len(compound_list)
    i = 0
    while i < len(compound_list):
        recurse_by_compound(compound_list, i)
        i += 1

#Takes a node, checks its type, and calls the appropriate function on it to add a print statement
def handle_nodetypes(parent, index):
    
    #pdb.set_trace()    

    #If there's a node after this one, check if it's a return statement: if so, add a print statement right before it
    #This handles every return except for if there's a function with no code prior to its return
    try:
        if isinstance(parent[index+1], c_ast.Return):
            handle_return(parent, index)
    except:
        pass



    #Now check for the current node's type and handle:

    #Case for variable declaration
    if isinstance(parent[index], c_ast.Decl):
        print_changed_vars(parent, index, True)
    
    #Case for variable assignment, if variable already exists
    elif isinstance(parent[index], c_ast.Assignment) or isinstance(parent[index], c_ast.UnaryOp):
        print_changed_vars(parent, index, False)
    
    #Cases for std out and error - FIX THIS, NOT WORKING!!
    elif isinstance(parent[index], c_ast.FuncCall):
        if parent[index].name.name == "printf":
            print_stdout(parent, index)
        elif parent[index].name.name == "fprintf":
            print_stderr(parent, index)
    elif isinstance(parent[index], c_ast.Return):
        if index == 0:
            handle_return(parent, index-1)


#NOTE: one way I can check if a FuncCall is calling another f'n in the program is to use the node type finder as provided by pycparser to find all FuncDecl
#nodes prior to recursing the tree and add the f'n names to a list, and then if I come across a FuncCall, check if it's calling a name from the list. 
#Will do this later

#NOTE x2: I will have to figure out how we can distinguish nodes we create vs. nodes we don't - checking the val of print statements, which
#I'm currently doing, is not enough, since to check the values of arrays and stuff we'll have to create some new vars and for loops.
        #IDEA: instead, ignore the node if the coord value is None

def handle_return(parent, index):
    print_node = create_printf_node()
    parent.insert(index+1, print_node)    

def print_changed_vars(parent, index, new):
    #If new, this was a Declaration. Handle diff. types of declarations differently
    if new:
        #Type declaration
        if isinstance(parent[index].children()[0][1], c_ast.TypeDecl):
            print_node = create_printf_node()
            parent.insert(index+1, print_node)

        #Pointer declaration
        elif isinstance(parent[index].children()[0][1], c_ast.PtrDecl):
            print_node = create_printf_node()
            parent.insert(index+1, print_node)

        #Array declaration
        elif isinstance(parent[index].children()[0][1], c_ast.ArrayDecl):
            print_node = create_printf_node()
            parent.insert(index+1, print_node)
    
    #Otherwise it was an assignment of an already declared var
    else:
        print_node = create_printf_node()
        parent.insert(index+1, print_node)

def print_stdout(parent, index):
    #Implement
    print_node = create_printf_node()
    parent.insert(index+1, print_node)

def print_sederr(parent, index):
    #Implement
    print_node = create_printf_node()
    parent.insert(index+1, print_node)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename  = sys.argv[1]
    else:
        filename = 'examples/c_files/year.c'

    ast = parse_file(filename, use_cpp=True,
            cpp_path='gcc',
            cpp_args=['-nostdinc','-E', r'-Iutils/fake_libc_include'])

    ast.show()
    print("-----------------------")
    #inserted_node = create_printf_node()
    #ast.ext[0].append(inserted_node)    
    #ast.show()
    #new_recurse_nodes(0, ast)
    recurse_by_function(ast)
    print("-----------------------")
    ast.show()
    print("-----------------------")
    generator = c_generator.CGenerator()
    print(generator.visit(ast))