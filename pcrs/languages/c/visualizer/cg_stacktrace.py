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


class CVisualizer:

    def __init__(self, user, temp_path):
        self.user = user
        self.temp_path = temp_path
        self.date_time = str((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())

        #List if removed lines from the start of the c program, to be put back in later
        self.removed_lines = []
        #func_list keeps track of all the function declaractions in our program
        self.func_list = []

        #Global hash variables, these are what we'll use to denote different parts of our added print statements

        #print_wrapper will hold the pattern we'll use to identify where our print statements begin and end
        self.print_wrapper = uuid.uuid4().hex

        #item_delimiter will hold the pattern we'll use to identify where different items in a single print statement begin and end
        self.item_delimiter = uuid.uuid4().hex

        #stdout_wrapper will hold the pattern we'll print right before and after each stdout line
        self.stdout_wrapper_before = uuid.uuid4().hex
        self.stdout_wrapper_after = uuid.uuid4().hex

        #stderr_wrapper will hold the pattern we'll print right before and after each stderr line
        self.stderr_wrapper_before = uuid.uuid4().hex
        self.stderr_wrapper_after = uuid.uuid4().hex

        #var_type_dict will hold a dictionary of all the variables we've seen, and their types - used for return val printing
        self.var_type_dict = {}

        #amt_after keeps track of the amount of print nodes we just added after the current node, used for returns
        self.amt_after = 0

        #cur_par_index keeps track of the index we're at for the current parent. Important to be global in the case where we
        #add nodes in front of our current node, we want to be able to increase this by more than 1
        self.cur_par_index = 0

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


    def create_printf_node(self, parent, index, func_name, onEntry, changedVar, onReturn, onStdOut, onStdErr):

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
         'void': 'no',
         'string': '%s',
         'char *': '%s'}

        add_id = c_ast.ID('printf')
        add_id_addr = None
        add_id_val = None
        add_id_size = None
        add_return_val = None
        line_no = "line:"+ (str)(parent[index].coord.line)
        function = (str)(self.item_delimiter) +"function:"+ (str)(func_name)
        on_entry = ""
        if onEntry:
            on_entry = (str)(self.item_delimiter) + "on_entry_point:True"

        std_out = ""
        if onStdOut:
            std_out = (str)(self.item_delimiter) + "std_out:True"

        std_err = ""
        if onStdErr:
            std_err = (str)(self.item_delimiter) + "std_err:True"

        on_return = ""
        if onReturn:
            #pdb.set_trace()
            #Case where we're returning a variable value
            if isinstance(parent[index].expr, c_ast.ID):
                return_var_name = (str)(parent[index].expr.name)
                return_type = (str)(self.var_type_dict.get(return_var_name))
                on_return = (str)(self.item_delimiter) + "return:" + primitive_types.get(return_type)
                add_return_val = c_ast.ID(return_var_name)
            #Otherwise we're returning a constant
            else:
                on_return = (str)(self.item_delimiter) + "return:" + (str)(parent[index].expr.value)

        var_info = ""
        #This block only gets executed if there's changed vars in the node
        if changedVar:
            #pdb.set_trace()

            var_name = (str)(self.item_delimiter) +"var_name:"+ (str)(var_name_val)
            var_addr = (str)(self.item_delimiter) +"addr:%p"
            var_type = (str)(self.item_delimiter) +"type:"+ (str)(type_of_var)
            var_new = (str)(self.item_delimiter) +"new:"+ (str)(var_new_val)
            var_size = (str)(self.item_delimiter) +"max_size:%zu"
            var_location = (str)(self.item_delimiter) +"location:stack"

            var_uninitialized = (str)(self.item_delimiter) +"uninitialized:" + (str)(is_uninit)

            #Case where it's a pointer, not to a string: print the address it's storing
            if (primitive_types.get(type_of_var) == None) and (ptr_depth > 0):
                var_val = (str)(self.item_delimiter) +"value:%p"
            else:
                var_val = (str)(self.item_delimiter) +"value:" + primitive_types.get(type_of_var)

            #Will pad the hex value after we run the C program, since we don't know the size of the variable yet
            var_hex = (str)(self.item_delimiter) +"hex_value:%X"

            var_info = var_name + var_addr +var_type + var_new + var_val + var_hex + var_location +var_uninitialized + var_size

            add_id_addr = c_ast.ID('&' + var_name_val)
            add_id_val = c_ast.ID(var_name_val)
            add_id_hex = c_ast.ID(var_name_val)
            add_id_size = c_ast.ID('sizeof(' + var_name_val+')')

            var_dict_add = {(str)(var_name_val):(str)(type_of_var)}
            self.var_type_dict.update(var_dict_add)

        str_to_add = (str)(self.print_wrapper) + line_no + std_out + std_err +function + on_entry + var_info + on_return 
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


    #Creates a printf node that just contains the value of hash_val in it
    def create_printf_hash_node(self, hash_val):
        add_id = c_ast.ID('printf')
        add_const = c_ast.Constant('string', '"'+(str)(hash_val)+'"')
        add_exprList = c_ast.ExprList([add_const])
        new_node = c_ast.FuncCall(add_id, add_exprList)
        return new_node

    # def recurse_nodes(self, parent):
    #     print(parent)
    #     if parent.coord:
    #         print(parent.coord.line)
    #     for child in parent.children():
    #         print(child[0])
    #         self.recurse_nodes(child[1])

    # def new_recurse_nodes(self, index, parent):
    #     print("parent is:")
    #     print(parent)
    #     print("current child is:")
    #     print(parent[index])
    #     if parent[index].coord:
    #         print(parent[index].coord.line)
    #     amt_of_children = len(parent.children)
    #     for i in range(0, amt_of_children):
    #         #print(child[0])
    #         self.new_recurse_nodes(i, parent[index])

    #Finds all function declarations in the AST and puts them into our function list
    def find_all_function_decl(self, ast):
        i = 0
        while i < len(ast.ext):
            if isinstance(ast.ext[i], c_ast.FuncDef):
                self.func_list.append((str)(ast.ext[i].decl.name))
            i+=1
        print(self.func_list)


    #Splits up the AST by function, continues to recurse if a node has a compound node
    def recurse_by_function(self, ast):
        i = 0
        while i < len(ast.ext):
            func_name = None
            if isinstance(ast.ext[i], c_ast.FuncDef):
                func_name = ast.ext[i].decl.name
            self.recurse_by_compound(ast.ext, i, func_name)
            i+= 1

    def recurse_by_compound(self, parent, index, func_name):
        #pdb.set_trace()

        #If node is a node we added, ignore it & return TODO: add checking for hidden lines here too, don't include if hidden
        if parent[index].coord == None:
            return

        ast_function = parent[index]
        print(ast_function)
        print(ast_function.coord)
        self.handle_nodetypes(parent, index, func_name)
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
        #global cur_par_index
        self.cur_par_index = 0
        while self.cur_par_index < len(compound_list):
            self.recurse_by_compound(compound_list, self.cur_par_index, func_name)
            self.cur_par_index += 1

    #Takes a node, checks its type, and calls the appropriate function on it to add a print statement
    def handle_nodetypes(self, parent, index, func_name):
        #global amt_after
        #reset amt_after
        self.amt_after = 0

        #pdb.set_trace()   

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
                self.print_stderr(parent, index, func_name)

            #Check if the function we're calling is declared in our program: if so, we want to add print statements
            #both before and after it. Otherwise, only add a print statement after
            elif self.get_funccall_funcname(parent[index]) in self.func_list:
                self.print_funccall_in_prog(parent, index, func_name)
            else:
                self.print_funccall_not_prog(parent, index, func_name)

        #Case for return
        elif isinstance(parent[index], c_ast.Return):
            if index == 0:
                self.handle_return(parent, index-1, func_name)

        #Case for start of a function: check if it has a body and insert a print statement at the beginning
        #of its body if so - otherwise, it's just a prototype, ignore
        elif isinstance(parent[index], c_ast.FuncDef):
            try:
                if parent[index].body.block_items != None:
                    #pdb.set_trace()
                    self.print_func_entry(parent, index, func_name)
            except:
                pass

        #If there's a node after this one, check if it's a return statement amt_after nodes after the current one
        try:
            #pdb.set_trace()
            if isinstance(parent[index+self.amt_after+1], c_ast.Return):
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

        ptr_depth = 0
        type_of_var = node.type.type.names[0] 
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

        #pdb.set_trace()
        ptr_depth = 0
        var_name_val = (str)(node.lvalue.name)
        type_of_var = (str)(self.var_type_dict.get(var_name_val)) 
        var_new_val = False
        is_uninit = False

    #Set the variables to be used in the print statements for a pointer declaration node
    def set_decl_ptr_vars(self, node):
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global ptr_depth
        #pdb.set_trace()

        #Check how many levels of pointer this is
        ptr_depth = 0
        temp_node = node
        while isinstance(temp_node.type, c_ast.PtrDecl):
            ptr_depth += 1
            temp_node = temp_node.type

        print("ptr depth is "+(str)(ptr_depth))
        type_of_var = (str)(temp_node.type.type.names[0]) + ' ' + '*'*ptr_depth 
        var_name_val = node.name
        var_new_val = True
        if node.init == None:
            is_uninit = True
        else:
            is_uninit = False

    #NOTE: TODO: add statements when making any funccall and returned from a FuncCall in our program
    #I thnk there's only 3 cases when we make the call: declaration, assignment, and just straight-out call. Implememnt all 3

    def handle_return(self, parent, index, func_name):
        #print_node = old_create_printf_node()
        #global amt_after
        #pdb.set_trace()
        print_node = self.create_printf_node(parent, index+self.amt_after+1, func_name, False, False, True, False, False)
        parent.insert(index+self.amt_after+1, print_node)    
        self.amt_after+= 1

    def add_before_fn(self, parent, index, func_name):
        #global cur_par_index
        #global amt_after
        print_node = self.create_printf_node(parent, index, func_name, False, False, False, False, False)
        parent.insert(index, print_node)
        self.amt_after += 1
        self.cur_par_index += 1

    def print_changed_vars(self, parent, index, func_name, new):
        #global amt_after
        #If new, this was a Declaration. Handle diff. types of declarations differently
        if new:
            #Type declaration
            if isinstance(self.get_decl_type(parent[index]), c_ast.TypeDecl):
                self.set_decl_vars(parent[index])
                print_node = self.create_printf_node(parent, index, func_name, False, True, False, False, False)
                parent.insert(index+1, print_node)
                self.amt_after += 1
                #If it's a function call declaration for a function in our program, 
                #ensure there's a print statement in front of it too
                #pdb.set_trace()
                if isinstance(parent[index].init, c_ast.FuncCall) and (self.get_funccall_funcname(parent[index].init) in self.func_list):
                    self.add_before_fn(parent, index, func_name)

            #Pointer declaration
            elif isinstance(self.get_decl_type(parent[index]), c_ast.PtrDecl):
                #pdb.set_trace()
                self.set_decl_ptr_vars(parent[index])
                print_node = self.create_printf_node(parent, index, func_name, False, True, False, False, False)
                parent.insert(index+1, print_node)
                self.amt_after += 1
                if isinstance(parent[index].init, c_ast.FuncCall) and (self.get_funccall_funcname(parent[index].init) in self.func_list):
                    self.add_before_fn(parent, index, func_name)

            #Array declaration
            elif isinstance(self.get_decl_type(parent[index]), c_ast.ArrayDecl):
                print_node = self.old_create_printf_node()
                parent.insert(index+1, print_node)
                self.amt_after += 1

        #Otherwise it was an assignment of an already declared var
        else:
            #Case for regular (non-pointer or anything fancy) assignment 
            #Also need to get this working w/ vars assigned to function calls
            if isinstance(parent[index].lvalue, c_ast.ID):
                self.set_assign_vars(parent[index])
                #print_node = old_create_printf_node()
                print_node = self.create_printf_node(parent, index, func_name, False, True, False, False, False)
                parent.insert(index+1, print_node)
                self.amt_after += 1
                #If it's a function call assignment for a function in our program, 
                #ensure there's a print statement in front of it too
                if isinstance(parent[index].rvalue, c_ast.FuncCall) and (self.get_funccall_funcname(parent[index].rvalue) in self.func_list):
                    self.add_before_fn(parent, index, func_name)

    def print_stdout(self, parent, index, func_name):
        #Implement
        #pdb.set_trace()
        print_node = self.create_printf_hash_node(self.stdout_wrapper_before)
        parent.insert(index, print_node)
        print_node = self.create_printf_hash_node(self.stdout_wrapper_after)
        parent.insert(index+2, print_node)
        print_node = self.create_printf_node(parent, index+1, func_name, False, False, False, True, False)
        parent.insert(index, print_node)
        self.cur_par_index += 3
        self.amt_after += 3

    def print_stderr(self, parent, index, func_name):
        #Implement
        print_node = self.create_printf_hash_node(self.stderr_wrapper_before)
        parent.insert(index, print_node)
        print_node = self.create_printf_hash_node(self.stderr_wrapper_after)
        parent.insert(index+2, print_node)
        print_node = self.create_printf_node(parent, index+1, func_name, False, False, False, False, True)
        parent.insert(index, print_node)
        self.cur_par_index += 3
        self.amt_after += 3

    #If calling a function declared in the program, add print statements before and after the function
    #call, so that we can highlight this line twice, once when calling, and once when returning back
    def print_funccall_in_prog(self, parent, index, func_name):
        #global amt_after
        #global cur_par_index
        print_node = self.create_printf_node(parent, index, func_name, False, False, False, False, False)
        parent.insert(index, print_node)
        parent.insert(index+2, print_node)
        self.cur_par_index += 2
        self.amt_after += 2

    #If calling a function not declared in the progra, only add a print statement after the function call,
    #only need to highlight this line once.
    def print_funccall_not_prog(self, parent, index, func_name):
        #global amt_after
        print_node = self.create_printf_node(parent, index, func_name, False, False, False, False, False)
        parent.insert(index+1, print_node)
        self.amt_after += 1

    def print_func_entry(self, parent, index, func_name):
        #global amt_after
        print_node = self.create_printf_node(parent, index, func_name, True, False, False, False, False)
        parent[index].body.block_items.insert(0, print_node)
        self.amt_after += 1


    def add_printf(self, user_script):

        stripped_user_script = self.remove_preprocessor_directives(user_script)
        print("STRIPPED USER SCRIPT IS -------")
        print(stripped_user_script)

        #Need to save user_script in a temp file so that we can run it
        temp_c_file = self.temp_path + self.user + self.date_time + ".c"
        try:
            # Creating the C file, and create the temp directory if it doesn't exist
            try:
                f = open(temp_c_file, 'w')
            except OSError:
                # Create temp directory if it doesn't exist
                os.makedirs(os.path.dirname(temp_c_file))
                f = open(temp_c_file, 'w')

            f.write(stripped_user_script)
            f.close()

        except Exception as e:
            print("ERROR with user file pre-processing")
            return

        ast = parse_file(temp_c_file, use_cpp=True,
        cpp_path='gcc',
        cpp_args=['-nostdinc','-E', r'-Iutils/fake_libc_include'])
        
        try:
            os.remove(temp_c_file)
        except OSError:
            pass

        ast.show()

        #print("-----------------------")
        self.find_all_function_decl(ast)
        self.recurse_by_function(ast)
        # print("-----------------------")
        ast.show()
        # print("-----------------------")
        generator = c_generator.CGenerator()
        print(generator.visit(ast))
        return generator.visit(ast)