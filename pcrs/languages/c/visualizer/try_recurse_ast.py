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

#func_list keeps track of all the function declaractions in our program
func_list = []

#Global hash variables, these are what we'll use to denote different parts of our added print statements

#print_wrapper will hold the pattern we'll use to identify where our print statements begin and end
print_wrapper = uuid.uuid4().hex

#item_delimiter will hold the pattern we'll use to identify where different items in a single print statement begin and end
item_delimiter = uuid.uuid4().hex

#stdout_wrapper will hold the pattern we'll print right before and after each stdout line
stdout_wrapper = uuid.uuid4().hex

#stderr_wrapper will hold the pattern we'll print right before and after each stderr line
stderr_wrapper = uuid.uuid4().hex

#var_type_dict will hold a dictionary of all the variables we've seen, and their types - used for return val printing
var_type_dict = {}

#amt_after keeps track of the amount of print nodes we just added after the current node, used for returns
amt_after = 0

#cur_par_index keeps track of the index we're at for the current parent. Important to be global in the case where we
#add nodes in front of our current node, we want to be able to increase this by more than 1
cur_par_index = 0

#WILL CHANGE THIS TO BE VARIABLE SPECIFIC INSTEAD OF HELLO WORLD, ONCE WE FIGURE OUT WHAT WE NEED
def old_create_printf_node():
    add_id = c_ast.ID('printf')
    add_const = c_ast.Constant('string', '"12345"')
    add_exprList = c_ast.ExprList([add_const])
    new_node = c_ast.FuncCall(add_id, add_exprList)
    return new_node

def create_printf_node(parent, index, func_name, onEntry, changedVar, onReturn):

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
    add_return_val = None
    line_no = (str)(item_delimiter) +"line:"+ (str)(parent[index].coord.line) + (str)(item_delimiter)
    function = (str)(item_delimiter) +"function:"+ (str)(func_name) + (str)(item_delimiter)
    on_entry = ""
    if onEntry:
        on_entry = (str)(item_delimiter) + "on_entry_point" + (str)(item_delimiter)

    on_return = ""
    if onReturn:
        #pdb.set_trace()
        #Case where we're returning a variable value
        if isinstance(parent[index].expr, c_ast.ID):
            return_var_name = (str)(parent[index].expr.name)
            return_type = (str)(var_type_dict.get(return_var_name))
            on_return = (str)(item_delimiter) + "return:" + primitive_types.get(return_type) + (str)(item_delimiter)
            add_return_val = c_ast.ID(return_var_name)
        #Otherwise we're returning a constant
        else:
            on_return = (str)(item_delimiter) + "return:" + (str)(parent[index].expr.value) + (str)(item_delimiter)

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

        var_dict_add = {(str)(var_name_val):(str)(type_of_var)}
        var_type_dict.update(var_dict_add)

    str_to_add = (str)(print_wrapper) + line_no + function + on_entry + var_info + on_return + (str)(print_wrapper) 
    add_const = c_ast.Constant('string', '"'+str_to_add+'"')
    if add_id_addr != None:
        add_exprList = c_ast.ExprList([add_const, add_id_addr, add_id_val, add_id_hex, add_id_size])
    else:
        if add_return_val != None:
            add_exprList = c_ast.ExprList([add_const, add_return_val])
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

#Finds all function declarations in the AST and puts them into our function list
def find_all_function_decl(ast):
    i = 0
    while i < len(ast.ext):
        if isinstance(ast.ext[i], c_ast.FuncDef):
            func_list.append((str)(ast.ext[i].decl.name))
        i+=1
    print(func_list)


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
    global cur_par_index
    cur_par_index = 0
    while cur_par_index < len(compound_list):
        recurse_by_compound(compound_list, cur_par_index, func_name)
        cur_par_index += 1

#Takes a node, checks its type, and calls the appropriate function on it to add a print statement
def handle_nodetypes(parent, index, func_name):
    global amt_after
    #reset amt_after
    amt_after = 0

    #pdb.set_trace()   

    #Check for the current node's type and handle:

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

        #Check if the function we're calling is declared in our program: if so, we want to add print statements
        #both before and after it. Otherwise, only add a print statement after
        elif get_funccall_funcname(parent[index]) in func_list:
            print_funccall_in_prog(parent, index, func_name)
        else:
            print_funccall_not_prog(parent, index, func_name)

    #Case for return
    elif isinstance(parent[index], c_ast.Return):
        if index == 0:
            handle_return(parent, index-1, func_name)

    #Case for start of a function: check if it has a body and insert a print statement at the beginning
    #of its body if so - otherwise, it's just a prototype, ignore
    elif isinstance(parent[index], c_ast.FuncDef):
        try:
            print_func_entry(parent[index].body.block_items, 0, func_name)
        except:
            pass

    #If there's a node after this one, check if it's a return statement amt_after nodes after the current one
    try:
        #pdb.set_trace()
        if isinstance(parent[index+amt_after+1], c_ast.Return):
            handle_return(parent, index, func_name)
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
    var_name_val = (str)(node.lvalue.name)
    type_of_var = (str)(var_type_dict.get(var_name_val)) 
    var_new_val = False
    is_uninit = False


#NOTE: TODO: add statements when making any funccall and returned from a FuncCall in our program
#I thnk there's only 3 cases when we make the call: declaration, assignment, and just straight-out call. Implememnt all 3

def handle_return(parent, index, func_name):
    #print_node = old_create_printf_node()
    global amt_after
    #pdb.set_trace()
    print_node = create_printf_node(parent, index+amt_after+1, func_name, False, False, True)
    parent.insert(index+amt_after+1, print_node)    
    amt_after+= 1

def print_changed_vars(parent, index, func_name, new):
    global amt_after
    #If new, this was a Declaration. Handle diff. types of declarations differently
    if new:
        #Type declaration
        if isinstance(get_decl_type(parent[index]), c_ast.TypeDecl):
            set_decl_vars(parent[index])
            print_node = create_printf_node(parent, index, func_name, False, True, False)
            parent.insert(index+1, print_node)
            amt_after += 1
            #If it's a function call declaration for a function in our program, 
            #ensure there's a print statement in front of it too
            #pdb.set_trace()
            if isinstance(parent[index].init, c_ast.FuncCall) and (get_funccall_funcname(parent[index].init) in func_list):
                global cur_par_index
                print_node = create_printf_node(parent, index, func_name, False, False, False)
                parent.insert(index, print_node)
                amt_after += 1
                cur_par_index += 1


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
        #Also need to get this working w/ vars assigned to function calls
        if isinstance(parent[index].lvalue, c_ast.ID):
            set_assign_vars(parent[index])
            #print_node = old_create_printf_node()
            print_node = create_printf_node(parent, index, func_name, False, True, False)
            parent.insert(index+1, print_node)
            amt_after += 1
            #If it's a function call assignment for a function in our program, 
            #ensure there's a print statement in front of it too
            if isinstance(parent[index].rvalue, c_ast.FuncCall) and (get_funccall_funcname(parent[index].rvalue) in func_list):
                global cur_par_index
                print_node = create_printf_node(parent, index, func_name, False, False, False)
                parent.insert(index, print_node)
                amt_after += 1
                cur_par_index += 1

def print_stdout(parent, index):
    #Implement
    global amt_after
    print_node = old_create_printf_node()
    parent.insert(index+1, print_node)
    amt_after += 1

def print_stderr(parent, index):
    #Implement
    global amt_after
    print_node = old_create_printf_node()
    parent.insert(index+1, print_node)
    amt_after += 1

#If calling a function declared in the program, add print statements before and after the function
#call, so that we can highlight this line twice, once when calling, and once when returning back
def print_funccall_in_prog(parent, index, func_name):
    global amt_after
    global cur_par_index
    print_node = create_printf_node(parent, index, func_name, False, False, False)
    parent.insert(index, print_node)
    parent.insert(index+2, print_node)
    cur_par_index += 1
    amt_after += 1

#If calling a function not declared in the progra, only add a print statement after the function call,
#only need to highlight this line once.
def print_funccall_not_prog(parent, index, func_name):
    global amt_after
    print_node = create_printf_node(parent, index, func_name, False, False, False)
    parent.insert(index+1, print_node)
    amt_after += 1

def print_func_entry(parent, index, func_name):
    global amt_after
    print_node = create_printf_node(parent, index, func_name, True, False, False)
    parent.insert(index, print_node)
    amt_after += 1

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
    find_all_function_decl(ast)
    recurse_by_function(ast)
    print("-----------------------")
    ast.show()
    print("-----------------------")
    generator = c_generator.CGenerator()
    print(generator.visit(ast))