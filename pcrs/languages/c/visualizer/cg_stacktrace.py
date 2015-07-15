from languages.c.visualizer.cg_stacktrace_functions import *
import problems_c.models
import logging
import pdb
import uuid
import sys
import os
import datetime
sys.path.extend(['.', '..'])
from pycparser import parse_file, c_ast, c_generator

#to_add_index will contain any extra amount we need to add to the index from node insertions in front of the current node, added by
#other functions
to_add_index= 0

class CVisualizer:

    def __init__(self, user, temp_path):
        self.primitive_types = \
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
         'int *': '%p',
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
         'void *': '%p',
         'void': 'no',
         'string': '%s',
         'char *': '%s'}

        self.user = user
        self.temp_path = temp_path
        self.date_time = str((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())

        #List if removed lines from the start of the c program, to be put back in later
        self.removed_lines = []
        #func_list keeps track of all the function declaractions in our program and their type
        self.func_list = {}

        #Global hash variables, these are what we'll use to denote different parts of our added print statements

        #print_wrapper will hold the pattern we'll use to identify where our print statements begin and end
        self.print_wrapper = uuid.uuid4().hex

        #item_delimiter will hold the pattern we'll use to identify where different items in a single print statement begin and end
        self.item_delimiter = uuid.uuid4().hex

        #var_type_dict will hold a dictionary of all the variables we've seen, and their types - used for return val printing
        self.var_type_dict = {}

        #ptr_dict will hold a dictionary of all the pointer names we've seen, and the amt of levels of pointers
        #ie: int **ptr_name would be {ptr_name:2}
        self.ptr_dict = {}

        #amt_after keeps track of the amount of print nodes we just added after the current node, used for returns
        self.amt_after = 0

        #cur_par_index keeps track of the index we're at for the current parent. Important to be global in the case where we
        #add nodes in front of our current node, we want to be able to increase this by more than 1
        #self.cur_par_index = 0

        #malloc_size_var_name is the name of the variable we'll be using to keep track of the size of any mallocs in the c code
        #We will just declare it as global to start
        self.malloc_size_var_name = "malloc_size"+(str)(uuid.uuid4().hex)

        #global_print_nodes will contain a list of ast print nodes that we must insert at the beginning of the main function. We come
        #across these through global declarations, but can only insert them in main
        self.global_print_nodes = []

        #array_dict will hold the name as the key, with type, size nodes of each level, temporary int vars to be used in for loops,and depth as values in a list
        #{array_name:[type, [size node1, size node2], [temp for var 1, temp for var 2],depth]}
        #int x[3][4]; would show up as:  {x:[int, [node with constant 3, node with constant 4], [temp for var 1, temp for var 2],2]} 
        self.array_dict = {}

        #handled_returns is a list of return nodes that have already been handled - used to check if we've handled a return or not
        self.handled_returns = []

        #WILL CHANGE THIS TO BE VARIABLE SPECIFIC INSTEAD OF HELLO WORLD, ONCE WE FIGURE OUT WHAT WE NEED
    def old_create_printf_node(self):
        add_id = c_ast.ID('printf')
        add_const = c_ast.Constant('string', '"12345"')
        add_exprList = c_ast.ExprList([add_const])
        new_node = c_ast.FuncCall(add_id, add_exprList)
        return new_node



    '''
    Replace preprocessor directives with empty lines to allow pycparser to parse the file correctly
    '''
    def remove_preprocessor_directives(self, user_script):
        lines = user_script.split('\n')
        new_lines = [self.clear_directive_line(l) for l in lines]
        new_user_script = '\n'.join(new_lines)

        return new_user_script


    def clear_directive_line(self, line):
        if ('_Generic' in line) or ('#include' in line):
            self.removed_lines.append(line)
            return '\r'
        else:
            return line

    #RetFnCall means it just returned from a previous function call
    def create_printf_node(self, parent, index, func_name, onEntry, changedVar, onReturn, onRetFnCall, onStdOut, onStdErr, isPtr, onHeap, isArray, isElse):

        add_id = c_ast.ID('printf')
        add_id_addr = None
        add_id_val = None
        add_id_size = None
        add_return_val = None
        add_id_ptr_size = None
        #pdb.set_trace()
        line_to_add = parent[index].coord.line
        if isElse:
            line_to_add -= 1
        line_no = "line:"+ (str)(line_to_add)
        function = (str)(self.item_delimiter) +"function:"+ (str)(func_name)

        on_entry = ""
        if onEntry:
            on_entry = (str)(self.item_delimiter) + "on_entry_point:True"

        std_out = ""
        if onStdOut:
            std_out = (str)(self.item_delimiter) + "std_out:"

        std_err = ""
        if onStdErr:
            std_err = (str)(self.item_delimiter) + "std_err:"

        on_return = ""
        if onReturn:
            #return_type contains function's return type (ie, int main(); would be int) 
            #Only execute this if return_node_name not none, which means it's not just an empty return statement
            if return_node_name != None:
                return_type = self.func_list.get(func_name)
                on_return = (str)(self.item_delimiter) + "return:" + (str)(self.primitive_types.get(return_type))
                add_return_val = c_ast.ID((str)(return_node_name));
            
            #Otherwise not returning anything on return
            else:
                on_return = (str)(self.item_delimiter) + "return:"

        returning_func = ""
        if onRetFnCall:
            returning_func = (str)(self.item_delimiter) + "returned_fn_call:" + (str)(returning_from)

        var_info = ""
        #This block only gets executed if there's changed vars in the node
        if changedVar:

            var_name = (str)(self.item_delimiter) +"var_name:"+ (str)(var_name_val)
            var_addr = (str)(self.item_delimiter) +"addr:%p"
            var_type = (str)(self.item_delimiter) +"type:"+ (str)(type_of_var)
            var_new = (str)(self.item_delimiter) +"new:"+ (str)(var_new_val)
            var_size = (str)(self.item_delimiter) +"max_size:%lu"

            #If on the stack, size is just the sizeof the variable name and location is stack
            location_info = "stack"
            add_id_size = c_ast.ID('(unsigned long)(sizeof(' + var_name_val+'))')
            #If on the heap, need to save the size of the thing we malloced in a separate variable since we can't do sizeof on heap
            if onHeap:
                location_info = "heap"
                add_id_size = c_ast.ID(self.malloc_size_var_name)

            is_global = ""
            if func_name == None:
                location_info = "data"
                is_global = (str)(self.item_delimiter) +"global:True"

            var_location = (str)(self.item_delimiter) +"location:"+location_info

            var_uninitialized = (str)(self.item_delimiter) +"uninitialized:" + (str)(is_uninit)

            value_type_set = "" 
            if not isArray:
                value_type_set = (str)(var_typerep)
            var_val = (str)(self.item_delimiter) +"value:" + value_type_set

            #Will pad the hex value after we run the C program, since we don't know the size of the variable yet
            var_hex = (str)(self.item_delimiter) +"hex_value:%lX"

            var_is_ptr = ""
            var_ptr_size = ""
            if isPtr:
                var_is_ptr = (str)(self.item_delimiter) + "is_ptr:name"
                var_ptr_size = (str)(self.item_delimiter) + "ptr_size:%lu"
                add_id_ptr_size = c_ast.ID('(unsigned long)(sizeof(' + pointing_to_type +'))')

            var_info = var_name + var_addr +var_type + var_new + var_hex + is_global +var_location +var_uninitialized + var_size + var_is_ptr + var_ptr_size + var_val

            add_id_addr = c_ast.ID('&(' + var_name_val+')')
            add_id_val = c_ast.ID(var_name_val)
            add_id_hex = c_ast.ID(var_name_val)

            var_dict_add = {(str)(var_name_val):(str)(type_of_var)}
            self.var_type_dict.update(var_dict_add)

        #Finished changed variable block
        str_to_add = (str)(self.print_wrapper) + line_no + function + returning_func + on_entry + on_return + var_info + std_out + std_err
        add_const = c_ast.Constant('string', '"'+str_to_add+'"')
        if add_id_addr != None:
            if add_id_ptr_size != None:
                add_exprList = c_ast.ExprList([add_const, add_id_addr, add_id_hex, add_id_size, add_id_ptr_size, add_id_val])
            else:
                add_exprList = c_ast.ExprList([add_const, add_id_addr, add_id_hex, add_id_size, add_id_val])
        else:
            if add_return_val != None:
                add_exprList = c_ast.ExprList([add_const, add_return_val])
            else:
                add_exprList = c_ast.ExprList([add_const])
        new_node = c_ast.FuncCall(add_id, add_exprList)
        return new_node


    #Creates a printf node that just contains the value of hash_val in it
    def create_printf_hash_node(self, hash_val):
        add_id = c_ast.ID('printf')
        add_const = c_ast.Constant('string', '"'+(  str)(hash_val)+'"')
        add_exprList = c_ast.ExprList([add_const])
        new_node = c_ast.FuncCall(add_id, add_exprList)
        return new_node

    #Finds all function declarations in the AST and puts them into our function list
    def find_all_function_decl(self, ast):
        i = 0
        while i < len(ast.ext):
            if isinstance(ast.ext[i], c_ast.FuncDef):
                if isinstance(ast.ext[i].decl.type.type, c_ast.PtrDecl):
                    tname = ast.ext[i].decl.type.type.type.type.names[0] + " *"
                else:
                    tname = ast.ext[i].decl.type.type.type.names[0]
                var_dict_add = {(str)(ast.ext[i].decl.name):tname}
                self.func_list.update(var_dict_add)
            i+=1


    #Splits up the AST by function, continues to recurse if a node has a compound node
    def recurse_by_function(self, ast):
        i = 0
        #pdb.set_trace()
        while i < len(ast.ext):
            func_name = None
            if isinstance(ast.ext[i], c_ast.FuncDef):
                func_name = ast.ext[i].decl.name

                #Add the list of global print nodes to the beginning of the main function before we continue
                if func_name == "main":
                    for node_num in range(0, len(self.global_print_nodes)):
                        (ast.ext)[i].body.block_items.insert(node_num, self.global_print_nodes[node_num])

            self.recurse_by_compound(ast.ext, i, func_name)
            i+= 1

    def recurse_by_compound(self, parent, index, func_name):

        global to_add_index

        #If node is a node we added, ignore it & return TODO: add checking for hidden lines here too, don't include if hidden
        if parent[index].coord == None:
            return

        ast_function = parent[index]
        #print(ast_function)
        #print(ast_function.coord)
        #pdb.set_trace()
        self.handle_nodetypes(parent, index, func_name)
        try:
            compound_list = ast_function.body.block_items
        except AttributeError:
            try:
                compound_list = ast_function.stmt.block_items
            except AttributeError:
                try:
                    if_compound_list = [ast_function.iftrue.block_items]
                    #pdb.set_trace()
                    compound_list = []
                    #Append any "if false" part of the if statement if exists
                    try:
                        if_compound_list.append(ast_function.iffalse.block_items)
                    #Case where there's another "if" inside this one
                    except AttributeError:
                        try:
                            if_compound_list.append([ast_function.iffalse])
                        except:
                            pass
                except:
                    return
        #total_len = len(compound_list)
        #global cur_par_index
        #Case for if statements: need to do both left and right side of "if"
        if len(compound_list) == 0 and len(if_compound_list) > 0:
            for each_compound in if_compound_list:
                compound_list = each_compound
                cur_par_index = 0
                while cur_par_index < len(compound_list):
                    self.recurse_by_compound(compound_list, cur_par_index, func_name)
                    cur_par_index += 1+to_add_index
                    to_add_index = 0
            if_compound_list = []
        
        #Case for non if statements
        else:
            cur_par_index = 0
            while cur_par_index < len(compound_list):
                self.recurse_by_compound(compound_list, cur_par_index, func_name)
                cur_par_index += 1+to_add_index
                to_add_index = 0

    #Takes a node, checks its type, and calls the appropriate function on it to add a print statement
    def handle_nodetypes(self, parent, index, func_name):
        #global amt_after
        #reset amt_after
        self.amt_after = 0

        print(parent[index])
        #Check for the current node's type and handle:

        #Case for variable declaration
        if isinstance(parent[index], c_ast.Decl):
            self.print_changed_vars(parent, index, func_name, True)

        #Case for variable assignment, if variable already exists
        elif isinstance(parent[index], c_ast.Assignment) or isinstance(parent[index], c_ast.UnaryOp):
            self.print_changed_vars(parent, index, func_name, False)

        #Cases for std out and error - FIX THIS, NOT WORKING!!
        elif isinstance(parent[index], c_ast.FuncCall):
            if self.get_funccall_funcname(parent[index]) == "printf":
                self.print_stdout(parent, index, func_name)
            elif self.get_funccall_funcname(parent[index]) == "fprintf":
                #TODO: add a check to ensure it's getting directed to stderr, or stdout, otherwise ignore
                self.print_stderr(parent, index)

            #Check if the function we're calling is declared in our program: if so, we want to add print statements
            #both before and after it. Otherwise, only add a print statement after
            elif (str)(self.get_funccall_funcname(parent[index])) in self.func_list:
                self.print_funccall_in_prog(parent, index, func_name, self.get_funccall_funcname(parent[index]))
            else:
                self.print_funccall_not_prog(parent, index, func_name)

        #Case for return
        #Will only go into this case if the return hasn't already been handled, as indicated in the handled_returns list
        elif isinstance(parent[index], c_ast.Return):
            if parent[index] not in self.handled_returns:
                self.handle_return(parent, index-1, func_name)

        #Case for start of a function: check if it has a body and insert a print statement at the beginning
        #of its body if so - otherwise, it's just a prototype, ignore
        elif isinstance(parent[index], c_ast.FuncDef):
            try:
                if parent[index].body.block_items != None:
                    self.print_func_entry(parent, index, func_name)
            except:
                pass

        #Case for an "if" statement: insert a print statement at the beginning of its iftrue and iffalse bodies
        elif isinstance(parent[index], c_ast.If):
            self.print_if_entry(parent, index, func_name)

        #If there's a node after this one, check if it's a return statement amt_after nodes after the current one
        try:
            if isinstance(parent[index+self.amt_after+1], c_ast.Return):
                print("RETURN CASE")
                self.handle_return(parent, index, func_name)
        except:
            pass


    def get_funccall_funcname(self, node):
        return node.name.name

    #Gets the type of Declaration of a Decl node (ie. Array, Type, Pointer, etc)
    def get_decl_type(self, node):
        return node.children()[0][1]

    #Set the variables to be used in the print statements for a declaration node
    def set_decl_vars(self, node):
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global ptr_depth
        global var_typerep

        ptr_depth = 0
        type_of_var = node.type.type.names[0]
        var_typerep = self.primitive_types.get(type_of_var)
        var_name_val = node.name
        var_new_val = True
        if node.init == None:
            is_uninit = True
        else:
            is_uninit = False

    #Set the variables to be used in the print statements for an assignment node
    def set_assign_vars(self, node):
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global ptr_depth
        global var_typerep

        ptr_depth = 0
        var_name_val = (str)(node.lvalue.name)
        type_of_var = (str)(self.var_type_dict.get(var_name_val))
        var_typerep = self.primitive_types.get(type_of_var)
        #This should only happen if it's a pointer and we can't find its type
        if var_typerep == None:
            var_typerep = '%p'
        var_new_val = False
        is_uninit = False

    #Set the variables to be used in the print statements for a pointer declaration node
    def set_decl_ptr_vars(self, node):
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global ptr_depth
        global var_typerep
        global pointing_to_type

        #Check how many levels of pointer this is
        ptr_depth = 0
        temp_node = node
        while isinstance(temp_node.type, c_ast.PtrDecl):
            ptr_depth += 1
            temp_node = temp_node.type

        #print("ptr depth is "+(str)(ptr_depth))
        type_of_var = (str)(temp_node.type.type.names[0]) + ' ' + '*'*ptr_depth
        pointing_to_type = (str)(temp_node.type.type.names[0]) + ' ' + '*'*(ptr_depth-1)
        var_typerep = "%p"
        var_name_val = node.name

        ptr_dict_add = {(str)(var_name_val):(int)(ptr_depth)}
        self.ptr_dict.update(ptr_dict_add)

        var_new_val = True
        if node.init == None:
            is_uninit = True
        else:
            is_uninit = False

    def set_assign_ptr_vars(self, node):
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global ptr_depth
        global var_typerep
        global pointing_to_type

        ptr_depth = 0
        temp_node = node.lvalue
        while isinstance(temp_node, c_ast.UnaryOp):
            ptr_depth += 1
            temp_node = temp_node.expr

        var_name_val = '*'*ptr_depth+(str)(temp_node.name)
        #ie, int ** if that's what this pointer is
        unstripped_vartype = (str)(self.var_type_dict.get(temp_node.name))

        #ie, int if that's what this pointer is pointing to at the end
        stripped_vartype = unstripped_vartype.replace("*", "").strip()

        pointing_to_type = stripped_vartype + ' ' + '*'*(ptr_depth-1)

        #Check if we're on the last level of the pointer, otherwise the thing it's pointing to is also a pointer
        if ptr_depth == self.ptr_dict.get(temp_node.name):
            var_typerep = self.primitive_types.get(stripped_vartype)
        else:
            var_typerep = '%p'

        type_of_var = unstripped_vartype.replace("*", "", ptr_depth)

        var_new_val = False
        is_uninit = False


    #node is the assign or decl
    def set_heap_vars(self, parent, index, node_name, malloc_node):
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global var_typerep

        #pdb.set_trace()

        #TODO: change this to work for both assign and decl vars, both have FuncCall under them which contains the malloc
        #then add to the size variable what the exprlist under the malloc funccall is.

        ptr_depth = self.ptr_dict.get((str)(node_name))

        type_of_var = (str)(self.var_type_dict.get((str)(node_name)))
        stripped_vartype = type_of_var.replace("*", "").strip()
        var_typerep = self.primitive_types.get(stripped_vartype)
        var_name_val = '*'*ptr_depth+(str)(node_name)

        self.set_malloc_size_var(parent, index, malloc_node)

        var_new_val = True
        is_uninit = True

    def set_decl_array(self, parent, index):
        #Adding the array info to the array_dict
        size_nodes = []

        temp_array = parent[index]
        array_name = temp_array.name
        array_depth = 0
        #pdb.set_trace()
        while isinstance(temp_array.type, c_ast.ArrayDecl):
            array_depth += 1
            temp_array = temp_array.type

            var_dict_add = {(str)(var_name_val):(str)(type_of_var)}
            self.var_type_dict.update(var_dict_add)

            level_size = self.create_new_var_node('int', temp_array.dim)
        #print("in set decl array")

    #Insert an assignment node, assigning the malloc size var to be the size that was malloced
    def set_malloc_size_var(self, parent, index, malloc_node):
        global to_add_index

        malloc_name_ID = c_ast.ID(self.malloc_size_var_name)
        malloc_exprlist = c_ast.ExprList(malloc_node.args.exprs)
        malloc_size_assign = c_ast.Assignment('=', malloc_name_ID, malloc_exprlist)
        parent.insert(index, malloc_size_assign)
        to_add_index += 1
        self.amt_after += 1

    #Pass in the function call node and get the ID to see the name of the function we're calling
    def set_fn_returning_from(self, func_ret_name):
        global returning_from
        returning_from = (str)(func_ret_name)

    def create_return_val_node(self, parent, index, func_name):
        global return_node_name
        add_return_val = parent[index].expr;
        return_type = self.func_list.get(func_name)
        return_node = self.create_new_var_node(return_type, add_return_val)
        return_node_name = return_node.name
        parent.insert(index, return_node)
        self.amt_after += 1

    #Creates a new variable node and sets it equal to whatever value is
    def create_new_var_node(self, val_type, value_node, var_name=None):
        #Have the option to pass in a specific variable name - otherwise we name it something random ourselves
        if var_name == None:
            var_name = "temp_var" + (str)(uuid.uuid4().hex)
        new_ID_type = c_ast.IdentifierType([val_type])
        new_type_node = c_ast.TypeDecl(var_name, [], new_ID_type)
        new_var_node = c_ast.Decl(var_name, [], [], [], new_type_node, value_node, None)
        return new_var_node

    #NOTE: TODO: add statements when making any funccall and returned from a FuncCall in our program
    #I thnk there's only 3 cases when we make the call: declaration, assignment, and just straight-out call. Implememnt all 3

    def handle_return(self, parent, index, func_name):
        global return_node_name
        #First create a new variable above the return statement which contains the return value
        #pdb.set_trace()
        #If we aren't actually returning anything, just set return_node_name to None, so we won't look for a value in create_printf_node
        if parent[index+self.amt_after+1].expr == None:
            return_node_name = None
        else:
            self.create_return_val_node(parent, index+self.amt_after+1, func_name) 

        self.handled_returns.append(parent[index+self.amt_after+1])
        print_node = self.create_printf_node(parent, index+self.amt_after+1, func_name, False, False, True, False, False, False, False, False, False, False)
        parent.insert(index+self.amt_after+1, print_node)
        self.amt_after+= 1

    def add_before_fn(self, parent, index, func_name):
        global to_add_index
        #global cur_par_index
        #global amt_after
        print_node = self.create_printf_node(parent, index, func_name, False, False, False, False, False, False, False, False, False, False)
        parent.insert(index, print_node)
        self.amt_after += 1
        to_add_index += 1

    def add_after_node(self, parent, index, func_name, isReturning, isPtr, isHeap):
        print_node = self.create_printf_node(parent, index, func_name, False, True, False, isReturning, False, False, isPtr, isHeap, False, False)
        #Case for global variables
        if func_name == None:
            self.global_print_nodes.append(print_node)
        else:
            parent.insert(index+1, print_node)
            self.amt_after += 1

    def print_changed_vars(self, parent, index, func_name, new):
        #global amt_after
        #If new, this was a Declaration. Handle diff. types of declarations differently
        if new:
            #Type declaration
            if isinstance(self.get_decl_type(parent[index]), c_ast.TypeDecl):
                self.set_decl_vars(parent[index])
                #If it's a function call declaration for a function in our program,
                #ensure there's a print statement in front of it too
                if isinstance(parent[index].init, c_ast.FuncCall) and ((str)(self.get_funccall_funcname(parent[index].init)) in self.func_list):
                    self.set_fn_returning_from(self.get_funccall_funcname(parent[index].init))
                    self.add_after_node(parent, index, func_name, True, False, False)
                    self.add_before_fn(parent, index, func_name)
                else:
                    self.add_after_node(parent, index, func_name, False, False, False)

            #Pointer declaration
            elif isinstance(self.get_decl_type(parent[index]), c_ast.PtrDecl):
                self.set_decl_ptr_vars(parent[index])
                if isinstance(parent[index].init, c_ast.FuncCall) and ((str)(self.get_funccall_funcname(parent[index].init)) in self.func_list):
                    self.set_fn_returning_from(self.get_funccall_funcname(parent[index].init))
                    self.add_after_node(parent, index, func_name, True, True, False)
                    self.add_before_fn(parent, index, func_name)

                else:
                    self.add_after_node(parent, index, func_name, False, True, False)

                    #Case for malloc, won't be mallocing inside a function header
                    try:
                        if parent[index].init.name.name == 'malloc':
                            #pdb.set_trace()
                            self.set_heap_vars(parent, index, parent[index].name, parent[index].init)

                            print_node = self.create_printf_node(parent, index+1, func_name, False, True, False, False, False, False, False, True, False, False)
                            parent.insert(index+1+self.amt_after, print_node)  
                            self.amt_after += 1
                    except:
                        pass

            #Array declaration
            elif isinstance(self.get_decl_type(parent[index]), c_ast.ArrayDecl):
                self.set_decl_array(parent, index)
                print_node = self.old_create_printf_node()
                parent.insert(index+1, print_node)
                self.amt_after += 1

        #Otherwise it was an assignment of an already declared var
        else:
            #pdb.set_trace()
            #Case for regular (non-pointer or anything fancy) assignment
            #Also need to get this working w/ vars assigned to function calls
            if isinstance(parent[index].lvalue, c_ast.ID):
                self.set_assign_vars(parent[index])
                #If it's a function call assignment for a function in our program,
                #ensure there's a print statement in front of it too
                if parent[index].lvalue.name in self.ptr_dict:
                    ptr_assign = True
                else:
                    ptr_assign = False
                if isinstance(parent[index].rvalue, c_ast.FuncCall) and ((str)(self.get_funccall_funcname(parent[index].rvalue)) in self.func_list):
                    self.set_fn_returning_from(self.get_funccall_funcname(parent[index].rvalue))
                    self.add_after_node(parent, index, func_name, True, ptr_assign, False)
                    self.add_before_fn(parent, index, func_name)
                else:
                    self.add_after_node(parent, index, func_name, False, ptr_assign, False)

                    #pdb.set_trace()
                     #Case for malloc, won't be mallocing inside a function header
                    try:
                        if parent[index].rvalue.name.name == 'malloc':
                            #pdb.set_trace()
                            self.set_heap_vars(parent, index, parent[index].lvalue.name, parent[index].rvalue)
                            print_node = self.create_printf_node(parent, index+1, func_name, False, True, False, False, False, False, False, True, False, False)
                            parent.insert(index+1+self.amt_after, print_node)  
                            self.amt_after += 1
                    except:
                        pass

            #Case for pointer assignment with stars in front, ie. *ptr = 3
            elif isinstance(parent[index].lvalue, c_ast.UnaryOp):
                self.set_assign_ptr_vars(parent[index])
                self.add_after_node(parent, index, func_name, False, True, False)

    def print_stdout(self, parent, index, func_name):
        global to_add_index

        print_node = self.create_printf_node(parent, index, func_name, False, False, False, False, True, False, False, False, False, False)
        parent.insert(index, print_node)
        to_add_index += 1
        self.amt_after += 1

    def print_stderr(self, parent, index, func_name):
        global to_add_index

        print_node = self.create_printf_node(parent, index, func_name, False, False, False, False, False, True, False, False, False, False)
        parent.insert(index, print_node)
        to_add_index += 1
        self.amt_after += 1

    #If calling a function declared in the program, add print statements before and after the function
    #call, so that we can highlight this line twice, once when calling, and once when returning back
    def print_funccall_in_prog(self, parent, index, func_name, func_ret_from):
        global to_add_index
        #global amt_after
        #global cur_par_index
        print_node = self.create_printf_node(parent, index, func_name, False, False, False, False, False, False, False, False, False, False)
        parent.insert(index, print_node)
        self.set_fn_returning_from(func_ret_from)
        print_node = self.create_printf_node(parent, index+1, func_name, False, False, False, True, False, False, False, False, False, False)
        parent.insert(index+2, print_node)
        to_add_index += 2
        self.amt_after += 2

    #If calling a function not declared in the progra, only add a print statement after the function call,
    #only need to highlight this line once.
    def print_funccall_not_prog(self, parent, index, func_name):
        print_node = self.create_printf_node(parent, index, func_name, False, False, False, False, False, False, False, False, False, False)
        parent.insert(index+1, print_node)
        self.amt_after += 1

    def print_if_entry(self, parent, index, func_name):
        print_node = self.create_printf_node(parent, index, func_name, False, False, False, False, False, False, False, False, False, False)
        try:
            parent[index].iftrue.block_items.insert(0, print_node)
            self.amt_after += 1
        except:
            pass

        try:
            print_node = self.create_printf_node(parent[index].iffalse.block_items, 0, func_name, False, False, False, False, False, False, False, False, False, True)
            parent[index].iffalse.block_items.insert(0, print_node)
            self.amt_after += 1
        except:
            pass

    def print_func_entry(self, parent, index, func_name):
        is_void = False
        try:
            if parent[index].decl.type.args.params[0].type.type.names[0] == 'void':
                is_void = True
        except:
            pass
        #pdb.set_trace()
        #Check if the node contains a param list: if so, add the params as changed (declared) vars
        if isinstance(parent[index].decl.type.args, c_ast.ParamList) and not(is_void):
            #Loop through all the variables in the header, each of them will be handled as a declaration node
            header_vars = parent[index].decl.type.args.params
            for i in range(0, len(header_vars)):
                if isinstance(self.get_decl_type(header_vars[i]), c_ast.PtrDecl):
                    self.set_decl_ptr_vars(header_vars[i])
                    header_var_ptr = True
                else:
                    self.set_decl_vars(header_vars[i])

                    header_var_ptr = False 
                print_node = self.create_printf_node(parent, index, func_name, True, True, False, False, False, False, header_var_ptr, False, False, False)
                parent[index].body.block_items.insert(0, print_node)
                self.amt_after += 1

        #Otherwise just set a print node with no changed vars
        else: 
            print_node = self.create_printf_node(parent, index, func_name, True, False, False, False, False, False, False, False, False, False)
            parent[index].body.block_items.insert(0, print_node)
            self.amt_after += 1


    def add_printf(self, user_script):

        stripped_user_script = self.remove_preprocessor_directives(user_script)
        #print("STRIPPED USER SCRIPT IS -------")
        #print(stripped_user_script)

        #Need to save user_script in a temp file so that we can run it
        temp_c_file = self.temp_path + self.user + self.date_time + ".c"
        print("TEMP PATH IS -------"+(str)(self.temp_path))
        try:
            # Creating the C file, and create the temp directory if it doesn't exist
            try:
                f = open(temp_c_file, 'w')
            except OSError:
                # Create temp directory if it doesn't exist
                os.makedirs(os.path.dirname(self.temp_path))
                f = open(temp_c_file, 'w')

            f.write(stripped_user_script)
            f.close()

        except Exception as e:
            print("ERROR with user file pre-processing: {0}".format(e))
            return

        ast = parse_file(temp_c_file, use_cpp=True,
        cpp_path='gcc',
        cpp_args=['-nostdinc','-E', r'-Iutils/fake_libc_include'])

        try:
            os.remove(temp_c_file)
        except OSError:
            pass

        ast.show()
        print("-----------------------")

        #Finding all functions in the program so we can save them in a list
        self.find_all_function_decl(ast)

        #Initializing a malloc size variable in the code
        malloc_size_var = self.create_new_var_node("int", None, self.malloc_size_var_name)
        ast.ext.insert(0, malloc_size_var)

        #Going through each function and adding all the print statements
        self.recurse_by_function(ast)

        print("-----------------------")
        ast.show()
        print("-----------------------")

        #Turning the new ast back into C code
        generator = c_generator.CGenerator()

        return generator.visit(ast)
