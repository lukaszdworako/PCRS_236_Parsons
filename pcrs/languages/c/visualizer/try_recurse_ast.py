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
import uuid

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
#
sys.path.extend(['.', '..'])

from pycparser import parse_file, c_ast, c_generator

#Global hash variables, these are what we'll use to denote different parts of our added print statements

#print_wrapper will hold the pattern we'll use to identify where our print statements begin and end
print_wrapper = uuid.uuid4().hex

#item_delimiter will hold the pattern we'll use to identify where different items in a single print statement begin and end
item_delimiter = uuid.uuid4().hex

#stdout_wrapper will hold the pattern we'll print right before and after each stdout line
stdout_wrapper = uuid.uuid4().hex

#stderr_wrapper will hold the pattern we'll print right before and after each stderr line
stderr_wrapper = uuid.uuid4().hex

#WILL CHANGE THIS TO BE VARIABLE SPECIFIC INSTEAD OF HELLO WORLD, ONCE WE FIGURE OUT WHAT WE NEED
def old_create_printf_node():
    add_id = c_ast.ID('printf')
    add_const = c_ast.Constant('string', '"12345"')
    add_exprList = c_ast.ExprList([add_const])
    new_node = c_ast.FuncCall(add_id, add_exprList)
    return new_node

def create_printf_node(parent, index, func_name, onEntry, changedVar):

    primitive_types = \
    {'char':'%c',
     'signed char':'%c',
     'unsigned char':'%c',
     'short':'%d',
     'short int': '%d',
     'signed short': '%d',
     'signed short int': '%c',
     'unsigned short': '%u',
     'unsigned short int': '%u',
     'int': '%d',
     'signed int': '%d',
     'unsigned': '%u',
     'unsigned int': '%u',
     'long': '%ld',
     'long int': '%ld',
     'signed long': '%ld',
     'signed long int': '%ld',
     'unsigned long': '%lu',
     'unsigned long int': '%lu',
     'long long': '%lld',
     'long long int': '%lld',
     'signed long long': '%lld',
     'signed long long int': '%lld',
     'unsigned long long': '%llu',
     'unsigned long long int': '%llu',
     'float': '%f',
     'double': '%f',
     'long double': '%lf',
     'void*': '%p',
     'void': 'no'}

    add_id = c_ast.ID('printf')
    add_id_addr = None
    add_id_val = None
    add_id_size = None
    line_no = (str)(item_delimiter) +"line:"+ (str)(parent[index].coord.line) + (str)(item_delimiter)
    function = (str)(item_delimiter) +"function:"+ (str)(func_name) + (str)(item_delimiter)
    on_entry = ""
    if onEntry:
        on_entry = (str)(item_delimiter) + "on_entry_point" + (str)(item_delimiter)

    var_info = ""
    #This block only gets executed if there's changed vars in the node
    if changedVar:
        #pdb.set_trace()

        var_name = (str)(item_delimiter) +"var_name:"+ (str)(var_name_val) + (str)(item_delimiter)
        var_addr = (str)(item_delimiter) +"addr:%p" + (str)(item_delimiter)
        var_type = (str)(item_delimiter) +"type:"+ (str)(type_of_var) + (str)(item_delimiter)
        var_new = (str)(item_delimiter) +"new:"+ (str)(var_new_val) + (str)(item_delimiter)
        var_size = (str)(item_delimiter) +"max_size:%zu" + (str)(item_delimiter)

        var_uninitialized = (str)(item_delimiter) +"uninitialized:" + (str)(is_uninit) + (str)(item_delimiter)

        var_val = (str)(item_delimiter) +"value:" + primitive_types.get(type_of_var)+ (str)(item_delimiter)

        #Will pad the hex value after we run the C program, since we don't know the size of the variable yet
        var_hex = (str)(item_delimiter) +"hex:%X" + (str)(item_delimiter)

        var_info = var_name + var_addr +var_type + var_new + var_val + var_hex + var_uninitialized + var_size

        add_id_addr = c_ast.ID('&' + var_name_val)
        add_id_val = c_ast.ID(var_name_val)
        add_id_hex = c_ast.ID(var_name_val)
        add_id_size = c_ast.ID('sizeof(' + var_name_val+')')

    str_to_add = (str)(print_wrapper) + line_no + function + on_entry + var_info +(str)(print_wrapper) 
    add_const = c_ast.Constant('string', '"'+str_to_add+'"')
    if add_id_addr != None:
        add_exprList = c_ast.ExprList([add_const, add_id_addr, add_id_val, add_id_hex, add_id_size])
    else:
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
        func_name = None
        if isinstance(ast.ext[i], c_ast.FuncDef):
            func_name = ast.ext[i].decl.name
        recurse_by_compound(ast.ext, i, func_name)
        i+= 1

def recurse_by_compound(parent, index, func_name):
    #pdb.set_trace()

    #If node is a node we added, ignore it & return TODO: add checking for hidden lines here too, don't include if hidden
    if parent[index].coord == None:
        return

    ast_function = parent[index]
    print(ast_function)
    print(ast_function.coord)
    handle_nodetypes(parent, index, func_name)
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
        recurse_by_compound(compound_list, i, func_name)
        i += 1

#Takes a node, checks its type, and calls the appropriate function on it to add a print statement
def handle_nodetypes(parent, index, func_name):
    
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
        print_changed_vars(parent, index, func_name, True)
    
    #Case for variable assignment, if variable already exists
    elif isinstance(parent[index], c_ast.Assignment) or isinstance(parent[index], c_ast.UnaryOp):
        print_changed_vars(parent, index, func_name, False)
    
    #Cases for std out and error - FIX THIS, NOT WORKING!!
    elif isinstance(parent[index], c_ast.FuncCall):
        if get_funccall_funcname(parent[index]) == "printf":
            print_stdout(parent, index)
        elif get_funccall_funcname(parent[index]) == "fprintf":
            #TODO: add a check to ensure it's getting directed to stderr, or stdout, otherwise ignore 
            print_stderr(parent, index)
    elif isinstance(parent[index], c_ast.Return):
        if index == 0:
            handle_return(parent, index-1)

    #Case for start of a function: check if it has a body and insert a print statement at the beginning
    #of its body if so - otherwise, it's just a prototype, ignore
    elif isinstance(parent[index], c_ast.FuncDef):
        try:
            print_func_entry(parent[index].body.block_items, 0, func_name)
        except:
            pass

def get_funccall_funcname(node):
    return node.name.name

#Gets the type of Declaration of a Decl node (ie. Array, Type, Pointer, etc) 
def get_decl_type(node):
    return node.children()[0][1]

#Set the variables to be used in the print statements for a declaration node
def set_decl_vars(node):
    global type_of_var
    global var_name_val
    global var_new_val
    global is_uninit

    type_of_var = node.type.type.names[0] 
    var_name_val = node.name
    var_new_val = True
    if node.init == None:
        is_uninit = True
    else:
        is_uninit = False

#Set the variables to be used in the print statements for an assignment node
def set_assign_vars(node):
    global type_of_var
    global var_name_val
    global var_new_val
    global is_uninit

    #pdb.set_trace()

    type_of_var = node.rvalue.type 
    var_name_val = node.lvalue.name
    var_new_val = False
    is_uninit = False


#NOTE: one way I can check if a FuncCall is calling another f'n in the program is to use the node type finder as provided by pycparser to find all FuncDecl
#nodes prior to recursing the tree and add the f'n names to a list, and then if I come across a FuncCall, check if it's calling a name from the list. 
#Will do this later

def handle_return(parent, index):
    print_node = old_create_printf_node()
    parent.insert(index+1, print_node)    

def print_changed_vars(parent, index, func_name, new):
    #If new, this was a Declaration. Handle diff. types of declarations differently
    if new:
        #Type declaration
        if isinstance(get_decl_type(parent[index]), c_ast.TypeDecl):
            set_decl_vars(parent[index])
            print_node = create_printf_node(parent, index, func_name, False, True)
            parent.insert(index+1, print_node)

        #Pointer declaration
        elif isinstance(get_decl_type(parent[index]), c_ast.PtrDecl):
            print_node = old_create_printf_node()
            parent.insert(index+1, print_node)

        #Array declaration
        elif isinstance(get_decl_type(parent[index]), c_ast.ArrayDecl):
            print_node = old_create_printf_node()
            parent.insert(index+1, print_node)
    
    #Otherwise it was an assignment of an already declared var
    else:
        #Case for regular (non-pointer or anything fancy) assignment 
        if isinstance(parent[index].lvalue, c_ast.ID):
            set_assign_vars(parent[index])
            #print_node = old_create_printf_node()
            print_node = create_printf_node(parent, index, func_name, False, True)
            parent.insert(index+1, print_node)

def print_stdout(parent, index):
    #Implement
    print_node = old_create_printf_node()
    parent.insert(index+1, print_node)

def print_stderr(parent, index):
    #Implement
    print_node = old_create_printf_node()
    parent.insert(index+1, print_node)

def print_func_entry(parent, index, func_name):
    print_node = create_printf_node(parent, index, func_name, True, False, False)
    parent.insert(index, print_node)

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