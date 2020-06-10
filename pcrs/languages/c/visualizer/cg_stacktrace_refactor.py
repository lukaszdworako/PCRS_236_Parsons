from languages.c.visualizer.cg_stacktrace_functions import *
import problems_c.models
import logging
import pdb
import uuid
import sys
import os
import datetime
sys.path.extend(['.', '..'])
from pycparser import parse_file, c_ast, c_generator, plyparser

#to_add_index will contain any extra amount we need to add to the index from node insertions in front of the current node, added by
#other functions
to_add_index= 0

class CVisualizerRefactor:

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
        #{array_name:[type, [size node1, size node2], [temp for var 1, temp for var 2],depth, ptr_depth]}
        #int x[3][4]; would show up as:  {x:[int, [node with constant 3, node with constant 4], [temp for var 1, temp for var 2],2, 0]}
        self.array_dict = {}

        #handled_returns is a list of return nodes that have already been handled - used to check if we've handled a return or not
        self.handled_returns = []

        #Delimiter to keep track of where array hex value begins
        self.array_hex_delim = uuid.uuid4().hex

        #Dictionary of all structs and the things within them: if a struct within a struct, both will show up as keys
        #Format is: {struct_name: [declaration1, declaration2, ...]}
        self.struct_dict = {}

        #Dictionary of all of the typedefs that point to types, including structs
        #Format is: {typedef_name: actual_type_name}
        self.typedef_dict = {}

        #extra_adder is used to keep track of any additional space we should add between our current node and where to insert it,
        #used in the add_after_node function
        self.extra_adder = 0

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
        try:
            if parent[index].coord == None:
                return
        except:
            return

        ast_function = parent[index]

        self.handle_nodetypes(parent, index, func_name)
        try:
            compound_list = ast_function.body.block_items
        except AttributeError:
            try:
                compound_list = ast_function.stmt.block_items
            except AttributeError:
                try:
                    if_compound_list = [ast_function.iftrue.block_items]
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




    def add_to_struct_dict(self, node):
        struct_dict_add = {(str)(node.type.name):node.type.decls}
        self.struct_dict.update(struct_dict_add)

        print(self.struct_dict)

    def add_to_typedef_dict(self, node):
        #pdb.set_trace()
        #If it's a struct typedef, add struct name and also add to struct dict
        if isinstance(node.type.type, c_ast.Struct):
            self.add_to_struct_dict(node.type)
            actual_type = node.type.type.name
        #Other cases
        else:
            actual_type = node.type.type.names[0]

        typedef_dict_add = {(str)(node.name):actual_type}
        self.typedef_dict.update(typedef_dict_add)

        print(self.typedef_dict)

    def get_funccall_funcname(self, node):
        return node.name.name

    #Gets the type of Declaration of a Decl node (ie. Array, Type, Pointer, etc)
    def get_decl_type(self, node):
        return node.children()[0][1]

    #Set the variables to be used in the print statements for a declaration node
    def set_decl_vars(self, node, struct_name_val):
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global ptr_depth
        global var_typerep

        ptr_depth = 0
        type_of_var = node.type.type.names[0]
        actual_type = self.typedef_dict.get(type_of_var)
        if actual_type != None:
            type_of_var = actual_type
        var_typerep = self.primitive_types.get(type_of_var)
        var_name_val = struct_name_val + node.name
        var_new_val = True
        if node.init == None:
            is_uninit = True
        else:
            is_uninit = False

    #Set the variables to be used in the print statements for an assignment node
    def set_assign_vars(self, node, isUnary):
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global ptr_depth
        global var_typerep
        global str_lit

        #pdb.set_trace()
        ptr_depth = 0
        if isUnary:
            temp_name_val = node.expr.name
        elif isinstance(node.lvalue, c_ast.StructRef):
            temp_generator = c_generator.CGenerator()
            temp_name_val = (str)(temp_generator.visit(node.lvalue))
        else:
            temp_name_val = node.lvalue.name

        var_name_val = (str)(temp_name_val)
        type_of_var = (str)(self.var_type_dict.get(var_name_val))
        actual_type = self.typedef_dict.get(type_of_var)
        if actual_type != None:
            type_of_var = actual_type
        var_typerep = self.primitive_types.get(type_of_var)

        if type_of_var == "char *":
            str_lit = True

        #This should only happen if it's a pointer and we can't find its type, char* finds string so including that too
        if var_typerep == None or var_typerep == '%s':
            var_typerep = '%p'
        var_new_val = False
        is_uninit = False

    def set_struct_vars(self, parent, index, node, struct_type_name, func_name, struct_full_name=""):
        
        #pdb.set_trace()

        cur_struct = self.struct_dict.get(struct_type_name)

        struct_full_name += node.name + "."
        
        #Loop through all the declaration nodes saved in the current struct
        for declaration in cur_struct:
            self.extra_adder = self.amt_after
            self.print_changed_vars(parent, index+to_add_index, func_name, True, declaration, struct_full_name)

    #Set the variables to be used in the print statements for a pointer declaration node
    def set_decl_ptr_vars(self, node, struct_name_val):
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global ptr_depth
        global var_typerep
        global pointing_to_type
        global str_lit
        #pdb.set_trace()
        #Check how many levels of pointer this is
        ptr_depth = 0
        is_struct = False
        temp_node = node
        while isinstance(temp_node.type, c_ast.PtrDecl):
            ptr_depth += 1
            temp_node = temp_node.type

        #print("ptr depth is "+(str)(ptr_depth))
        try:
            clean_type = temp_node.type.type.names[0]
        except:
            clean_type = "struct "+temp_node.type.type.name
            is_struct = True
        #if it's a struct pointer
            
        type_of_var = (str)(clean_type) + ' ' + '*'*ptr_depth
        
        actual_type = self.typedef_dict.get(type_of_var)
        if actual_type != None:
            type_of_var = actual_type

        pointing_to_type = (str)(clean_type) + ' ' + '*'*(ptr_depth-1)
        if type_of_var == "char *":
            str_lit = True

        var_typerep = "%p"
        var_name_val = struct_name_val + node.name

        ptr_dict_add = {(str)(var_name_val):(int)(ptr_depth)}
        self.ptr_dict.update(ptr_dict_add)

        var_new_val = True
        if node.init == None:
            is_uninit = True
        else:
            is_uninit = False

        return is_struct

    def set_assign_ptr_vars(self, node, isUnary):
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global ptr_depth
        global var_typerep
        global pointing_to_type

        array_access = ""
        array_depth = 0
        ptr_depth = 0
        if isUnary:
            temp_node = node.expr
        else:
            temp_node = node.lvalue
        while isinstance(temp_node, c_ast.UnaryOp):
            ptr_depth += 1
            temp_node = temp_node.expr

        #pdb.set_trace()
        while isinstance(temp_node, c_ast.ArrayRef):
            array_depth += 1
            temp_generator = c_generator.CGenerator()
            array_access = "["+ (str)(temp_generator.visit(temp_node.subscript)) +"]"+array_access
            temp_node = temp_node.name

        #Case where it's a binary op, like *(ptr + 1) = something
        if isinstance(temp_node, c_ast.BinaryOp):
            #add in case for *(ptr + var) = something, currently only for constant
            var_name_val = '*'*ptr_depth+'('+(str)(temp_node.left.name)+array_access+(str)(temp_node.op)+(str)(temp_node.right.value)+')'
            node_name = temp_node.left.name
        else:
            var_name_val = '*'*ptr_depth+(str)(temp_node.name)+array_access
            node_name = temp_node.name
        #ie, int ** if that's what this pointer is
        unstripped_vartype = (str)(self.var_type_dict.get(node_name))

        #ie, int if that's what this pointer is pointing to at the end
        stripped_vartype = unstripped_vartype.replace("*", "").replace("[]", "").strip()

        pointing_to_type = stripped_vartype + ' ' + '*'*(ptr_depth-1)

        #pdb.set_trace()
        #Check if we're on the last level of the pointer, otherwise the thing it's pointing to is also a pointer

        array_dict_entry = self.array_dict.get(node_name)
        if array_dict_entry == None:
            dict_ptr_depth = self.ptr_dict.get(node_name)
            dict_array_depth = 0
        else: 
            dict_ptr_depth = array_dict_entry[4]
            dict_array_depth = array_dict_entry[3]
        if ptr_depth+array_depth == dict_ptr_depth + dict_array_depth:
            var_typerep = self.primitive_types.get(stripped_vartype)
            #it can't be pointing to a full string, only a character - this is the case for string lits
            # if var_typerep == '%s':
            #     var_typerep = '%p'
        else:
            var_typerep = '%p'

        type_of_var = unstripped_vartype.replace("*", "", ptr_depth).replace("[]", "")

        actual_type = self.typedef_dict.get(type_of_var)
        if actual_type != None:
            type_of_var = actual_type

        var_new_val = False
        is_uninit = False


    #node is the assign or decl
    def set_heap_vars(self, parent, index, node_name, malloc_node, struct_name_val):
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global var_typerep


        #TODO: change this to work for both assign and decl vars, both have FuncCall under them which contains the malloc
        #then add to the size variable what the exprlist under the malloc funccall is.
        #pdb.set_trace()
        clean_name = struct_name_val + (str)(node_name.split('[', 1)[0])
        ptr_depth = self.ptr_dict.get(clean_name)

        parent_type = (str)(self.var_type_dict.get(clean_name))
        type_of_var = parent_type.replace("*", "").replace("[]", "").strip()
        actual_type = self.typedef_dict.get(type_of_var)
        if actual_type != None:
            type_of_var = actual_type
        var_typerep = self.primitive_types.get(type_of_var)

        in_struct_list = self.struct_dict.get(actual_type)
        if in_struct_list != None:
            type_of_var = "struct "+ actual_type
        var_name_val = '*'*ptr_depth+ struct_name_val+(str)(node_name)

        self.set_malloc_size_var(parent, index, malloc_node)

        var_new_val = True
        is_uninit = True

    #node is the assign or decl
    def set_heap_struct_vars(self, parent, index, func_name ,node_name, malloc_node, struct_name_val):

        # cur_struct = self.struct_dict.get(struct_type_name)

        # struct_full_name += node.name + "."
        
        # #Loop through all the declaration nodes saved in the current struct
        # for declaration in cur_struct:
        #     self.extra_adder = self.amt_after
        #     self.print_changed_vars(parent, index+to_add_index, func_name, True, declaration, struct_full_name)


        #TODO: change this to work for both assign and decl vars, both have FuncCall under them which contains the malloc
        #then add to the size variable what the exprlist under the malloc funccall is.
        clean_name = struct_name_val + (str)(node_name.split('[', 1)[0])
        ptr_depth = self.ptr_dict.get(clean_name)

        parent_type = (str)(self.var_type_dict.get(clean_name))
        type_of_var = parent_type.replace("*", "").replace("[]", "").strip()
        actual_type = self.typedef_dict.get(type_of_var)
        if actual_type != None:
            type_of_var = actual_type
        var_typerep = self.primitive_types.get(type_of_var)

        in_struct_list = self.struct_dict.get(type_of_var)
        if in_struct_list == None:
            return False
        else:
            #Loop through each declaration node, create a temporary assignment node for each and run it through print_changed_vars
            for declaration in in_struct_list:

                #lvalue will be the node's name
                structname_id = c_ast.ID(clean_name)
                structval_id = c_ast.ID(declaration.name)
                new_lvalue = c_ast.StructRef(structname_id, '->', structval_id)
                #rvalue will be the value, a funccall with malloc as ID and the current node as the exprlist
                rval_name = c_ast.ID("malloc")
                idtype = declaration.type.type
                unarytype = c_ast.TypeDecl(None, [], idtype)
                unaryexpr = c_ast.Typename(None, [], unarytype)
                rval_unary = c_ast.UnaryOp("sizeof", unaryexpr)
                rval_args = c_ast.ExprList([rval_unary])
                new_rvalue = c_ast.FuncCall(rval_name, rval_args)
                
                new_assign_node = c_ast.Assignment("=", new_lvalue, new_rvalue)
                pdb.set_trace()
                #Assign its line number to be the same as the current malloc node
                new_assign_node.coord = plyparser.Coord("", malloc_node.coord.line)

                self.extra_adder = self.amt_after

                self.print_changed_vars(parent, index+to_add_index, func_name, False, new_assign_node, struct_name_val)                

            return True            
        # if in_struct_list != None:
        #     type_of_var = "struct "+ actual_type
        # var_name_val = '*'*ptr_depth+ struct_name_val+(str)(node_name)

        # self.set_malloc_size_var(parent, index, malloc_node)

        # var_new_val = True    
        # is_uninit = True


    def set_decl_array(self, parent, index, node, struct_name_val):
        #Adding the array info to the array_dict

        global to_add_index
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global ptr_depth
        global var_typerep
        global pointing_to_type

        ptr_depth = 0
        #size_nodes contains nodes of int variables which hold the size of each level of the array
        size_nodes = []
        #temp_var_nodes will hold temporary int variable nodes that are initialized the first time we see the array,
        #to be used every time we loop through this particular array
        temp_var_nodes = []

        temp_array = node
        array_name = temp_array.name
        array_depth = 0
        #Loop through the depth of the array (ie. int x[][] is depth 2)
        while isinstance(temp_array.type, c_ast.ArrayDecl):
            array_depth += 1
            temp_array = temp_array.type

            #Adding a variable to hold the size of this array level, and keeping it in size_nodes array

            #Case where size wasn't specified, check for initlist to determine the size
            if temp_array.dim == None:
                #pdb.set_trace()
                try:
                    outer_len = len(node.init.children())
                    #Case for strings
                    if outer_len == 0:
                        outer_len = len(node.init.value)-2
                    temp_len_val = c_ast.Constant('int', (str)(outer_len))
                    level_size = self.create_new_var_node('int', temp_len_val)
                #case where there's no size specified and no initlist - will deal more with this later
                except:
                    pass
            else:
                level_size = self.create_new_var_node('int', temp_array.dim)

            size_nodes.append(level_size)

            #Adding a variable to hold the temporary size variables, will actually insert them into the parent after
            temp_var_val = c_ast.Constant('int', '0')
            temp_var_to_add = self.create_new_var_node('int', temp_var_val)
            temp_var_nodes.append(temp_var_to_add)

        #keep looping through in case it's a pointer array until we get to the bottom level
        while isinstance(temp_array.type, c_ast.PtrDecl):
            ptr_depth += 1
            temp_array = temp_array.type


        #Initializing all the normal things like type and name, just like in other declarations
        try:
            clean_array_type = (str)(temp_array.type.type.names[0])
        except:
            clean_array_type = "struct "+(str)(temp_array.type.type.name)
        type_of_var = clean_array_type + ' ' +'*'*ptr_depth + ' ' + '[]'*array_depth

        actual_type = self.typedef_dict.get(type_of_var)
        if actual_type != None:
            type_of_var = actual_type

        if ptr_depth > 0:
            pointing_to_type = clean_array_type + ' ' + '*'*(ptr_depth-1)

        #Need to decide on if I need this or not
        var_typerep = "%p"

        var_name_val = struct_name_val+node.name

        var_new_val = True
        if node.init == None:
            is_uninit = True
        else:
            is_uninit = False

        array_dict_add = {(str)(var_name_val):[(str)(clean_array_type), size_nodes, temp_var_nodes, array_depth, ptr_depth]}
        self.array_dict.update(array_dict_add)
        ptr_dict_add = {(str)(var_name_val):(int)(ptr_depth)}
        self.ptr_dict.update(ptr_dict_add)
        #Now we're done adding it to the dictionary
        print(self.array_dict)

        #Initialize the temporary variables which will store size in later for loops
        #Put them before the array decl node
        for temp_var_node in temp_var_nodes:
            parent.insert(index, temp_var_node)
            to_add_index+=1

        #Initialize the size variables as well
        for size_node in size_nodes:
            parent.insert(index, size_node)
            to_add_index+=1

        print(self.array_dict)

        if ptr_depth >0:
            return True
        else:
            return False

    def set_assign_array(self, parent, index, isUnary, node):
        #Adding the array info to the array_dict

        global to_add_index
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global ptr_depth
        global var_typerep

        ptr_depth = 0
        if isUnary:
            temp_val = node.lvalue.expr.name
        else:
            temp_val = node.lvalue.name

        #Loop until we get to the ID element
        while isinstance(temp_val, c_ast.ArrayRef):
            temp_val = temp_val.name

        var_name_val = (str)(temp_val.name)

        cur_array_dict = self.array_dict.get(var_name_val)

        #If it wasn't originally declared as an array but is now being referenced
        #like an array
        if cur_array_dict == None:
            return {"is_ptr": True, "in_arr_dict":False}

        ptr_depth = cur_array_dict[4]
        if ptr_depth > 0:
            pointing_to_type = cur_array_dict[0] + ' ' + '*'*(ptr_depth-1)

        array_depth = cur_array_dict[3]
        type_of_var = cur_array_dict[0] +' ' + '*'*(ptr_depth) + ' '+'[]'*(array_depth)

        actual_type = self.typedef_dict.get(type_of_var)
        if actual_type != None:
            type_of_var = actual_type

        var_typerep = '%p'
        var_new_val = False
        is_uninit = False

        if ptr_depth >0:
            return {"is_ptr": True, "in_arr_dict":True}
        else:
            return {"is_ptr": False, "in_arr_dict":True}

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
        #If we aren't actually returning anything, just set return_node_name to None, so we won't look for a value in create_printf_node
        if parent[index+self.amt_after+1].expr == None:
            return_node_name = None
        else:
            self.create_return_val_node(parent, index+self.amt_after+1, func_name)

        self.handled_returns.append(parent[index+self.amt_after+1])
        node_to_send = parent[index+self.amt_after+1]
        print_node = self.create_printf_node(node_to_send, func_name, False, False, True, False, False, False, False, False, False, False, False, False)
        parent.insert(index+self.amt_after+1, print_node)
        self.amt_after+= 1

    def add_before_fn(self, parent, index, func_name):
        global to_add_index
        #global cur_par_index
        #global amt_after
        print_node = self.create_printf_node(parent[index], func_name, False, False, False, False, False, False, False, False, False, False, False, False)
        parent.insert(index, print_node)
        self.amt_after += 1
        to_add_index += 1

    #node is the actual node we're looking at, mostly for the coord. Parent and index is where we're adding it
    def add_after_node(self, parent, index, func_name, isReturning, isPtr, isHeap, isArray):
        print_node = self.create_printf_node(parent[index], func_name, False, True, False, isReturning, False, False, isPtr, isHeap, isArray, False, False, False)
        #Case for global variables
        if func_name == None:
            self.global_print_nodes.append(print_node)
        else:
            parent.insert(index+1+self.extra_adder, print_node)
            self.amt_after += 1

    def add_after_all_nodes(self, parent, index, func_name, isReturning, isPtr, isHeap, isArray):
        print_node = self.create_printf_node(parent[index], func_name, False, True, False, isReturning, False, False, isPtr, isHeap, isArray, False, False, False)
        parent.insert(index+self.amt_after+1, print_node)
        self.amt_after += 1

    #index here will be where we should start inserting nodes
    #prints value, hex, and size arrays by adding for loop nodes
    def print_array_extra_nodes(self, parent, index):
        #Loop through and create foor loops nodes for each depth of the array
        cur_array_dict = self.array_dict.get(var_name_val)
        array_depth = cur_array_dict[3]
        for_counter_nodes = cur_array_dict[2]
        size_nodes = cur_array_dict[1]

        open_bracket = self.create_printf_string('"["')
        closed_bracket = self.create_printf_string('"]"')


        new_val_node = self.for_node_recurse(for_counter_nodes, size_nodes, "val", cur_array_dict)
        parent.insert(index, open_bracket)
        parent.insert(index+1, new_val_node)
        parent.insert(index+2, closed_bracket)

        hex_intro_node = self.create_printf_string('"'+self.item_delimiter + 'hex_value:["')
        parent.insert(index+3, hex_intro_node)

        new_hex_node = self.for_node_recurse(for_counter_nodes, size_nodes, "hex", cur_array_dict)
        parent.insert(index+4, new_hex_node)
        parent.insert(index+5, closed_bracket)

        self.amt_after += 6

        #just calls a function that prints the values of size_nodes in a for loop
        #pass it any for counter node since it's just a temp node we'll use for the for loop
        self.print_size_nodes(size_nodes, parent, index+3)


    def print_size_nodes(self, size_nodes, parent, index):
    #insert a single for loop to go through the size node array
        size_print = self.create_printf_string('"'+self.item_delimiter + 'arr_dims:["')
        parent.insert(index, size_print)
        #just straight add a print statement to the c code parent for each size node,
        #no need to make a c for loop here
        added_size = 1
        for size_node in size_nodes:
            #Don't add a comma after unless it's the last element in the list
            if size_node == size_nodes[-1]:
                size_print = self.create_printf_string('"%d"')
            else:
                size_print = self.create_printf_string('"%d,"')
            cur_node_id = c_ast.ID(size_node.name)
            size_print.args.exprs.append(cur_node_id)
            parent.insert(index+added_size, size_print)
            added_size += 1

        size_print = self.create_printf_string('"]"')
        parent.insert(index+added_size, size_print)

        self.amt_after += added_size+1

    #print_type refers to whether we're printing a value, hex, or size
    def for_node_recurse(self, for_counter_nodes, size_nodes, print_type, cur_array_dict):
        if len(for_counter_nodes) > 0:
            cur_depth_counter = for_counter_nodes[0]
            cur_depth_size = size_nodes[0]
        else:
            print_node = self.create_printf_arr_val(cur_array_dict, print_type)
            return print_node

        #the init part of the for loop
        for_ID = c_ast.ID(cur_depth_counter.name)
        for_exprlist = cur_depth_counter.init
        node_to_init = c_ast.Assignment('=', for_ID, for_exprlist)

        #the condition part of the for loop
        end_ID = c_ast.ID(cur_depth_size.name)
        for_cond = c_ast.BinaryOp('<', for_ID, end_ID)

        #the next part of the for loop
        for_next = c_ast.UnaryOp('p++', for_ID)

        if len(for_counter_nodes)>1:
            #the stment part of the for loop
            open_bracket = self.create_printf_string('"["')

            #Adding an if statement to decide if we need a comma or not after closed bracket: only if we are not at last number in for loop
            iftrue = self.create_printf_string('"]"')
            iffalse = self.create_printf_string('"],"')

            closed_bracket = self.check_if_last_for(for_ID, end_ID, iftrue, iffalse)

            for_statement = c_ast.Compound([open_bracket, self.for_node_recurse(for_counter_nodes[1:], size_nodes[1:], print_type, cur_array_dict), closed_bracket])
        else:
            for_statement = c_ast.Compound([self.for_node_recurse(for_counter_nodes[1:], size_nodes[1:], print_type, cur_array_dict)])

        new_for_node = c_ast.For(node_to_init, for_cond, for_next, for_statement)

        return new_for_node

    #Creates an if node to check if we're on the last iteration of a for loop in c - if so, does iftrue, otherwise, iffalse
    def check_if_last_for(self, for_ID, end_ID, iftrue, iffalse):
        num_1 = c_ast.Constant('int', '1')
        count_subtract = c_ast.BinaryOp('-', end_ID, num_1)
        if_cond = c_ast.BinaryOp('==', for_ID, count_subtract)
        if_iftrue = iftrue
        if_iffalse = iffalse

        return c_ast.If(if_cond, if_iftrue, if_iffalse)


    #this function creates a simple printf node with a string value as specified in its arguments
    def create_printf_string(self, str_value):
        add_id = c_ast.ID('printf')
        add_const = c_ast.Constant('string', (str)(str_value))
        add_exprList = c_ast.ExprList([add_const])
        new_node = c_ast.FuncCall(add_id, add_exprList)
        return new_node

    #this function creates a printf node of an array value, either regular or hex
    def create_printf_arr_val(self, cur_array_dict, print_type):
        #if printing the regular values, print them based on the array's initialized type
        if print_type == "val":
            arr_type = cur_array_dict[0]
            if cur_array_dict[4] > 0:
                print_notation = '"\'%p\',"'
            else:
                print_notation = '"\''+(str)(self.primitive_types.get(arr_type))+'\',"'
        #otherwise if printing hex values, print them in hex format
        elif print_type == "hex":
            print_notation = '"\'%lX\',"'

        add_id = c_ast.ID('printf')
        add_const = c_ast.Constant('string', (str)(print_notation))

        #Call a function to recursively add array refs, passing in the temp for loop nodes
        all_array_refs = self.add_array_refs(cur_array_dict[2])

        add_exprList = c_ast.ExprList([add_const, all_array_refs])
        new_node = c_ast.FuncCall(add_id, add_exprList)
        return new_node

    #recursively adds the array ref nodes to be used in the print statement formed above.
    #ie: to print x[temp1][temp2] in a for loop, we need to recursively add temp1 and temp2 "arrayref" nodes
    def add_array_refs(self, temp_for_nodes):
        if len(temp_for_nodes)<1:
            return c_ast.ID(var_name_val)

        ref_name = self.add_array_refs(temp_for_nodes[:-1])
        ref_script = c_ast.ID(temp_for_nodes[-1].name)

        return c_ast.ArrayRef(ref_name, ref_script)

    #This creates a string lit array for the node at parent, index
    #const_node is only passed in if it's part of an array declaration, otherwise ignore
    def handle_str_lit_array(self, parent, index, node,const_node_name=None, const_node=None):

        global to_add_index
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global ptr_depth
        global var_typerep

        ptr_depth = 0
        #size_nodes contains nodes of int variables which hold the size of each level of the array
        size_nodes = []
        #temp_var_nodes will hold temporary int variable nodes that are initialized the first time we see the array,
        #to be used every time we loop through this particular array
        temp_var_nodes = []

        if const_node == None:
            str_lit_ptr = node
            try:
                array_name = str_lit_ptr.name
                array_len = len((str)(node.init.value))-2
            except:
                array_name = str_lit_ptr.lvalue.name
                array_len = len((str)(node.rvalue.value))-2
        else:
            array_name = const_node_name
            array_len = len(const_node.value) - 2

        array_depth = 1
        #Adding a variable to hold the size of this array level, and keeping it in size_nodes array
        
        temp_len_val = c_ast.Constant('int', (str)(array_len))
        level_size = self.create_new_var_node('int', temp_len_val)
        size_nodes.append(level_size)

        #Adding a variable to hold the temporary size variables, will actually insert them into the parent after
        temp_var_val = c_ast.Constant('int', '0')
        temp_var_to_add = self.create_new_var_node('int', temp_var_val)
        temp_var_nodes.append(temp_var_to_add)

        #Initializing all the normal things like type and name, just like in other declarations
        type_of_var = "char"

        #Need to decide on if I need this or not
        var_typerep = "%p"

        var_name_val = array_name

        var_new_val = True
        is_uninit = False

        array_dict_add = {(str)(var_name_val):[(str)(type_of_var), size_nodes, temp_var_nodes, array_depth, ptr_depth]}
        self.array_dict.update(array_dict_add)

        #Now we're done adding it to the dictionary
        print(self.array_dict)

        #Initialize the temporary variables which will store size in later for loops
        #Put them before the array decl node
        for temp_var_node in temp_var_nodes:
            parent.insert(index+self.amt_after+1, temp_var_node)
            to_add_index+=1
            self.amt_after+= 1

        #Initialize the size variables as well
        for size_node in size_nodes:
            parent.insert(index+self.amt_after+1, size_node)
            to_add_index+=1
            self.amt_after+= 1

        print(self.array_dict)

        return False

    #This function is distinct from the above, as above creates a string lit array for any str lit types, while
    #this one particularly handles cases where someone declares an array and its contents are str lits.
    def handle_array_decl_str_lit(self, parent, index, func_name):
        global to_add_index
        node = parent[index+to_add_index]
        node_array_dict = self.array_dict.get(node.name)

        if node_array_dict == None:
            return

        #If it's not a char* (ie. type is char and ptr depth is 1) or wasn't initialized to anything then just return
        if not(node_array_dict[0] == "char" and node_array_dict[4] == 1 and node.init != None):
            return

        #Recurse through the initList and insert str lit printf array nodes for each init item 
        self.initList_recurse(node.init, -1, parent, index, node.name, func_name)

    #In this case, init_parent is the initList and init_index is the index in the initList.
    def initList_recurse(self, init_parent, init_index, parent, index, array_name, func_name):
        #global to_add_index

        if init_index < 0:
            cur_node = init_parent
        else:
            cur_node = init_parent[init_index]

        #Got to the string constant, handle
        if not(isinstance(cur_node, c_ast.InitList)):
            print(array_name)
            self.handle_str_lit_array(parent, index, array_name,cur_node)
            print_node = self.create_printf_node(init_parent[init_index], func_name, False, True, False, False, False, False, False, False, True, False, False, True)
            parent.insert(index+self.amt_after+1, print_node)
            self.amt_after += 1
            self.print_array_extra_nodes(parent, index+self.amt_after+1)

        else:
            for i in range(0, len(cur_node.exprs)):
                nodes_name = array_name + '[' + (str)(i) + ']'
                self.initList_recurse(cur_node.exprs, i, parent, index, nodes_name, func_name)

    #If node is given, we're going to use that instead to tell the function which node we're adding info on, yet we're adding to parent and index
    #Node should only be given if it's a struct decl
    def print_changed_vars(self, parent, index, func_name, new, node=None, struct_name_val=""):
        global str_lit
        str_lit  = False
    
        if node != None:
            node_to_consider = node
        else:
            node_to_consider = parent[index]

        #If new, this was a Declaration. Handle diff. types of declarations differently
        if new:

            #Type declaration
            if isinstance(self.get_decl_type(node_to_consider), c_ast.TypeDecl):
                
                #Check if it's a struct - if so, handle it differently than plain decl
                try:
                    #This will pass as long as node_to_consider.type.type is an IdentifierType node
                    cur_type = node_to_consider.type.type.names[0]
                except:
                    #This will generally happen only when it is a struct that has already been declared, inside another struct
                    cur_type = node_to_consider.type.type.name

                struct_entry = self.struct_dict.get(cur_type)
                typedef_entry = self.typedef_dict.get(cur_type)
                    
                if struct_entry or typedef_entry != None:
                    #Get the name of the actual struct
                    if typedef_entry != None:
                        struct_name = typedef_entry
                    else:
                        struct_name = cur_type

                    self.set_struct_vars(parent, index, node_to_consider, struct_name, func_name, struct_name_val)

                else:
                    self.set_decl_vars(node_to_consider, struct_name_val)
                    #If it's a function call declaration for a function in our program,
                    #ensure there's a print statement in front of it too
                    if isinstance(node_to_consider.init, c_ast.FuncCall) and ((str)(self.get_funccall_funcname(node_to_consider.init)) in self.func_list):
                        self.set_fn_returning_from(self.get_funccall_funcname(node_to_consider.init))
                        self.add_after_node(parent, index, func_name, True, False, False, False)
                        self.add_before_fn(parent, index, func_name)
                    else:
                        self.add_after_node(parent, index, func_name, False, False, False, False)

            #Pointer declaration
            elif isinstance(self.get_decl_type(node_to_consider), c_ast.PtrDecl):
                self.set_decl_ptr_vars(node_to_consider, struct_name_val)

                if isinstance(node_to_consider.init, c_ast.FuncCall) and ((str)(self.get_funccall_funcname(node_to_consider.init)) in self.func_list):
                    self.set_fn_returning_from(self.get_funccall_funcname(node_to_consider.init))
                    self.add_after_node(parent, index, func_name, True, True, False, False)
                    self.add_before_fn(parent, index, func_name)

                else:
                    self.add_after_node(parent, index, func_name, False, True, False, False)

                    #Case for malloc, won't be mallocing inside a function header
                    try:
                        if node_to_consider.init.name.name == 'malloc':
                            #See if it's a struct getting put on heap: if so, handle differently than single var on heap, since we have to loop
                            #through all the vars in struct and get their heap vals
                            is_struct = self.set_heap_struct_vars(parent, index, func_name,node_to_consider.name, node_to_consider.init, struct_name_val)
                            if not is_struct:
                                self.set_heap_vars(parent, index, node_to_consider.name, node_to_consider.init, struct_name_val)
                                #pdb.set_trace()
                                print_node = self.create_printf_node(parent[index+1], func_name, False, True, False, False, False, False, False, True, False, False, False, False)
                                parent.insert(index+1+self.amt_after, print_node)
                                self.amt_after += 1
                    except:
                        pass
                #Case for string literal, add an array val on data
                #Only execute this if it's being set to a constant that's a string: otherwise, if pointing to a var, leave it
                #pdb.set_trace()
                if str_lit and node_to_consider.init != None and isinstance(node_to_consider.init, c_ast.Constant):
                    self.call_funcs_for_str_lit(parent, index, func_name, node_to_consider)

            #Array declaration
            elif isinstance(self.get_decl_type(node_to_consider), c_ast.ArrayDecl):
                isPtr = self.set_decl_array(parent, index, node_to_consider, struct_name_val)
                self.add_after_node(parent, index+to_add_index, func_name, False, isPtr, False, True)
                self.print_array_extra_nodes(parent, index+to_add_index+self.amt_after+1)
                self.handle_array_decl_str_lit(parent, index, func_name)
        
        #Otherwise it was an assignment of an already declared var
        else:
            #unaryop case, such as x++
            if isinstance(node_to_consider, c_ast.UnaryOp):
                #Case for pointers such as *x++
                if isinstance(node_to_consider.expr, c_ast.UnaryOp):
                    self.set_assign_ptr_vars(node_to_consider, True)
                    self.add_after_node(parent, index, func_name, False, True, False, False)
                #Non-pointer unaryops
                else:
                    self.set_assign_vars(node_to_consider, True)
                    self.add_after_node(parent, index, func_name, False, False, False, False)

            #Case for regular (non-pointer or anything fancy) assignment
            elif isinstance(node_to_consider.lvalue, c_ast.ID) or isinstance(node_to_consider.lvalue, c_ast.StructRef):
                self.set_assign_vars(node_to_consider, False)

                if node_to_consider.lvalue.name in self.ptr_dict:
                    ptr_assign = True

                    #This is the case where we have a pointer tht points to a string: can only happen w/ string lit, so
                    #we're still pointing to an address, which then points to a char array on data, hence %p for address
                    try:
                        if node_to_consider.rvalue.type == 'string':
                            str_lit = True
                            global var_typerep
                            var_typerep = '%p'
                    except:
                        pass
                else:
                    ptr_assign = False

                #If it's a function call assignment for a function in our program,
                #ensure there's a print statement in front of it too
                if isinstance(node_to_consider.rvalue, c_ast.FuncCall) and ((str)(self.get_funccall_funcname(node_to_consider.rvalue)) in self.func_list):
                    self.set_fn_returning_from(self.get_funccall_funcname(node_to_consider.rvalue))
                    self.add_after_node(parent, index, func_name, True, ptr_assign, False, False)
                    self.add_before_fn(parent, index, func_name)
                else:
                    self.add_after_node(parent, index, func_name, False, ptr_assign, False, False)
                    #again, if we have a string literal, we're going to create an array for it in data after the pointer print node
                    #if str_lit:
                        ##self.handle_str_lit_array(parent, index)
                        #print("str lit")
                     #Case for malloc, won't be mallocing inside a function header
                    self.try_malloc(parent, index+to_add_index, func_name, node_to_consider.lvalue.name, node_to_consider, struct_name_val)

            #Case for pointer assignment with stars in front, ie. *ptr = 3
            elif isinstance(node_to_consider.lvalue, c_ast.UnaryOp):

                self.set_assign_ptr_vars(node_to_consider, False)
                self.add_after_node(parent, index, func_name, False, True, False, False)
                try:
                    name_to_pass = node_to_consider.lvalue.expr.name
                except:
                    #If there's a binary op inside the unary op
                    name_to_pass = node_to_consider.lvalue.expr.left.name
                self.try_malloc(parent, index+to_add_index, func_name, name_to_pass, node_to_consider, struct_name_val)

            #Array assignment, not unary
            elif isinstance((node_to_consider.lvalue), c_ast.ArrayRef):
                returned_dict = self.set_assign_array(parent, index, False, node_to_consider)
                isPtr = returned_dict.get("is_ptr")
                isDeclArray = returned_dict.get("in_arr_dict")
                # if isDeclArray:
                #     self.add_after_node(parent, index+self.amt_after, func_name, False, isPtr, False, True)
                #     self.print_array_extra_nodes(parent, index+self.amt_after+1)

                #     #This is only to get the exact name of the var changing for malloc
                #     temp_node = parent[index+to_add_index].lvalue
                #     array_access = ""
                #     while isinstance(temp_node, c_ast.ArrayRef):
                #         array_access = array_access+"["+ temp_node.subscript.value +"]"
                #         temp_node = temp_node.name
                #     name_to_pass = var_name_val+array_access

                # #Handle as a pointer, but dont put in name table. It's arrayref opposed to binaryop, since we're referencing
                # #the pointer with array notation, ie ptr[2] = var
                # else:
                #     self.set_assign_ptr_vars(parent[index], False)
                #     self.add_after_node(parent, index, func_name, False, True, False, False)
                #     print ("not declared as an array")
                #     name_to_pass = var_name_val
                #pdb.set_trace()
                self.set_assign_ptr_vars(node_to_consider, False)
                self.add_after_node(parent, index, func_name, False, isPtr, False, False)
                name_to_pass = var_name_val
                self.try_malloc(parent, index+to_add_index, func_name, name_to_pass, node_to_consider, struct_name_val)

            #Case for string literal, add an array val on data
            if str_lit and isinstance(node_to_consider.rvalue, c_ast.Constant):
                #pdb.set_trace()
                self.call_funcs_for_str_lit(parent, index, func_name, node_to_consider)

    def call_funcs_for_str_lit(self, parent, index, func_name, node):
        self.handle_str_lit_array(parent, index, node)
        print_node = self.create_printf_node(parent[index+to_add_index], func_name, False, True, False, False, False, False, False, False, True, False, False, True)
        parent.insert(index+self.amt_after+1, print_node)
        self.amt_after += 1
        self.print_array_extra_nodes(parent, index+self.amt_after+1)

    #Try to malloc
    def try_malloc(self, parent, index, func_name, var_name, node, struct_name_val):
        try:
            if node.rvalue.name.name == 'malloc':
                self.set_heap_vars(parent, index, var_name, node.rvalue, struct_name_val)
                print_node = self.create_printf_node(parent[index+to_add_index], func_name, False, True, False, False, False, False, False, True, False, False, False, False)
                parent.insert(index+2, print_node)
                self.amt_after += 1
        except:
            pass

    def print_stdout(self, parent, index, func_name):
        global to_add_index

        print_node = self.create_printf_node(parent[index], func_name, False, False, False, False, True, False, False, False, False, False, False, False)
        parent.insert(index, print_node)
        to_add_index += 1
        self.amt_after += 1

    def print_stderr(self, parent, index, func_name):
        global to_add_index

        print_node = self.create_printf_node(parent[index], func_name, False, False, False, False, False, True, False, False, False, False, False, False)
        parent.insert(index, print_node)
        to_add_index += 1
        self.amt_after += 1

    def handle_free(self, parent, index, func_name):
        #global type_of_var
        global var_name_val
        #global var_new_val
        #global is_uninit
        global ptr_depth
        global var_typerep
        global to_add_index

        var_typerep = '%p'
        temp_to_free = parent[index].args.exprs[0]
        ptr_depth = 1
        while isinstance(temp_to_free, c_ast.UnaryOp):
            ptr_depth += 1
            temp_to_free = temp_to_free.expr

        var_name_val = '*'*ptr_depth + temp_to_free.name
        print_node = self.create_printf_node(parent[index], func_name, False, True, False, False, False, False, True, False, False, False, True, False)
        parent.insert(index, print_node)
        self.amt_after += 1
        to_add_index += 1
#onEntry, changedVar, onReturn, onRetFnCall, onStdOut, onStdErr, isPtr, onHeap, isArray, isElse, isFree):

    #If calling a function declared in the program, add print statements before and after the function
    #call, so that we can highlight this line twice, once when calling, and once when returning back
    def print_funccall_in_prog(self, parent, index, func_name, func_ret_from):
        global to_add_index
        #global amt_after
        #global cur_par_index
        print_node = self.create_printf_node(parent[index], func_name, False, False, False, False, False, False, False, False, False, False, False, False)
        parent.insert(index, print_node)
        self.set_fn_returning_from(func_ret_from)
        print_node = self.create_printf_node(parent[index+1], func_name, False, False, False, True, False, False, False, False, False, False, False, False)
        parent.insert(index+2, print_node)
        to_add_index += 2
        self.amt_after += 2

    #If calling a function not declared in the program, only add a print statement after the function call,
    #only need to highlight this line once.

    #
    def print_funccall_not_prog(self, parent, index, func_name):
        #pdb.set_trace()
        #Loop through all the arguments we're passing this function, print out each of their values after the function
        for variable_passed in parent[index].args.exprs:
            self.handle_types_variable_passed(parent, index, variable_passed, func_name)
        
        #Add this in without any changed vars just to show we got to this line, incase we didn't have any vars in the funccall

        # print_node = self.create_printf_node(parent, index, func_name, False, False, False, False, False, False, False, False, False, False, False, False)
        # parent.insert(index+1, print_node)
        # self.amt_after += 1

    def handle_types_variable_passed(self, parent, index, variable_passed, func_name):
            #Straight ID
            if isinstance(variable_passed, c_ast.ID):
                var_name = variable_passed.name
                self.handle_funccall_var_changes(parent, index, variable_passed, var_name, func_name)
            #binary op, like x+1 or 1+x - we'll just get value of x, run through this function until we get to an ID
            elif isinstance(variable_passed, c_ast.BinaryOp):
                self.handle_types_variable_passed(parent, index, variable_passed.left, func_name)
                self.handle_types_variable_passed(parent, index, variable_passed.right, func_name)    
            #Unary op, like x++ or *x

            #QUESTION - Should i check the val of the pointer, the thing it's pointing to, or both?

            elif isinstance(variable_passed, c_ast.UnaryOp):
                self.handle_types_variable_passed(parent, index, variable_passed.expr, func_name)
            #ArrayRef, like x[1]
            elif isinstance(variable_passed, c_ast.ArrayRef):
                #pdb.set_trace()

                cur_arrayref = variable_passed
                array_depth = 0
                while isinstance(cur_arrayref, c_ast.ArrayRef):
                    array_depth += 1
                    cur_arrayref = cur_arrayref.name

                var_name = cur_arrayref.name
                self.handle_funccall_var_changes(parent, index, variable_passed, var_name, func_name, array_depth)
            #Otherwise don't do anything with it - probably a constant


    #Actually set the variables - only have depth if it was an arrayref, in which case, do something a bit different
    def handle_funccall_var_changes(self, parent, index, id_node, name_val, func_name, depth=0):
        array_dict_entry = self.array_dict.get(name_val)

        is_str_lit = self.set_funccall_changed_vars(id_node, name_val)
        
        #Not an array, could be straight var or part of an array but the element itself isnt one
        if array_dict_entry == None or array_dict_entry[3] == depth:    
            #Add a regular node here first:
            self.add_after_all_nodes(parent, index, func_name, False, False, False, False)

        else:
            print("array - add this")
            isPtr = False
            if var_typerep == '%p':
                isPtr == True
            self.add_after_all_nodes(parent, index, func_name, False, isPtr, False, True)
            self.print_array_extra_nodes(parent, index+self.amt_after+1)

        #Now handle cases where it got assigned to a str lit: loop through it
        if is_str_lit:
            self.call_funcs_for_str_lit(parent, index+amt_after, func_name, parent[index+amt_after])


    #Set the variables to be used in the print statements for the changed funccall vars
    def set_funccall_changed_vars(self, node, name_val):
        global type_of_var
        global var_name_val
        global var_new_val
        global is_uninit
        global ptr_depth
        global var_typerep

        is_str_lit = False
        ptr_depth = 0
        
        #If arrayref, name is a bit different
        if isinstance(node, c_ast.ArrayRef):
            generator = c_generator.CGenerator()
            var_name_val = (str)(generator.visit(node))
        else:
            var_name_val = name_val

        type_of_var = (str)(self.var_type_dict.get(name_val)).replace("[]", "").strip()
        var_typerep = self.primitive_types.get(type_of_var)

        if type_of_var == "char *":
            is_str_lit = True

        #This should only happen if it's a pointer and we can't find its type, char* finds string so including that too
        if var_typerep == None or var_typerep == '%s':
            var_typerep = '%p'
        var_new_val = False
        is_uninit = False

        return is_str_lit

    def print_loop_entry(self, parent, index, func_name):
        print_node = self.create_printf_node(parent[index], func_name, False, False, False, False, False, False, False, False, False, False, False, False)
        parent[index].stmt.block_items.insert(0, print_node)
        self.amt_after += 1

    def print_for_entry(self, parent, index, func_name):
        self.set_assign_vars(parent[index].next, True)
        print_node = self.create_printf_node(parent[index], func_name, False, True, False, False, False, False, False, False, False, False, False, False)
        parent[index].stmt.block_items.insert(0, print_node)
        self.amt_after += 1

    def print_if_entry(self, parent, index, func_name):
        print_node = self.create_printf_node(parent[index], func_name, False, False, False, False, False, False, False, False, False, False, False, False)
        try:
            parent[index].iftrue.block_items.insert(0, print_node)
            self.amt_after += 1
        except:
            pass

        try:
            print_node = self.create_printf_node(parent[index].iffalse.block_items[0], func_name, False, False, False, False, False, False, False, False, False, True, False, False)
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
        #Check if the node contains a param list: if so, add the params as changed (declared) vars
        if isinstance(parent[index].decl.type.args, c_ast.ParamList) and not(is_void):
            #Loop through all the variables in the header, each of them will be handled as a declaration node
            header_vars = parent[index].decl.type.args.params
            for i in range(0, len(header_vars)):
                if isinstance(self.get_decl_type(header_vars[i]), c_ast.PtrDecl):
                    self.set_decl_ptr_vars(header_vars[i], "")
                    header_var_ptr = True
                else:
                    self.set_decl_vars(header_vars[i], "")

                    header_var_ptr = False
                global is_uninit
                is_uninit = False
                print_node = self.create_printf_node(parent[index], func_name, True, True, False, False, False, False, header_var_ptr, False, False, False, False, False)
                parent[index].body.block_items.insert(0, print_node)
                self.amt_after += 1

        #Otherwise just set a print node with no changed vars
        else:
            print_node = self.create_printf_node(parent[index], func_name, True, False, False, False, False, False, False, False, False, False, False, False)
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
        #ast.show()
        print("-----------------------")

        #Turning the new ast back into C code
        generator = c_generator.CGenerator()
        print(generator.visit(ast))
        return generator.visit(ast)


    #Takes a node, checks its type, and calls the appropriate function on it to add a print statement
    def handle_nodetypes(self, parent, index, func_name):
        pdb.set_trace()
        current_location = LocationInfo(parent, index, func_name)

        temp_class = SuperNode(self, parent[index], current_location)
        while (temp_class != None):
            try:
                temp_class = temp_class.Factory()
            except:
                break 
        #decl_node = run_node.Factory()
        # type_node = decl_node.create_decl_from_type()
        # typedecl_node = type_node.create_typedecl_from_type()
        # reg_decl = typedecl_node.add_reg_typedecl_from_type()

class SuperNode(CVisualizerRefactor):
    """ Superclass of all nodes, contains basic info such as location
    """
    def __init__(self, outer, node, location_info):
        self.location_info = location_info
        self.node = node
        self.outer = outer

    def Factory(self):
        if isinstance(self.node, c_ast.Decl):
            return DeclarationNode(self)

        else:
            return None

    def get_funccall_funcname(self):
        return self.node.name.name

class DeclarationNode(SuperNode):
    """ Info and handling of a declaration node object
    """ 
    def __init__(self, parent):
        SuperNode.__init__(self, parent.outer ,parent.node, parent.location_info)
        self.node_type = "declaration"
        self.declaration_type = self.node.children()[0][1]

    def Factory(self):
        if isinstance(self.declaration_type, c_ast.TypeDecl):
            return TypeDeclaration(self)
        
        elif isinstance(self.declaration_type, c_ast.PtrDecl):
            return PointerDeclaration(self)

        else:
            return None
             
    def getType(self):
        return self.node_type

    def getDeclType(self):
        return self.declaration_type

class TypeDeclaration(DeclarationNode):
    """ Handling a type declaration node object
    """
    def __init__(self, parent):
        DeclarationNode.__init__(self, parent)

        #This is the subtype of the type declaration node, such as "int" or "char" 
        self.typedecl_type = self.get_typedecl_type() 

        #self.actual_type is the actual type of the declaration: ie, if its typedef'd 
        self.actual_type = self.get_actual_type()

        self.is_struct = self.check_struct()

    #gets the typedecl type with a try/catch exception, which depends on what's inside our decl node
    def get_typedecl_type(self):
        try:
            #This will pass as long as node_to_consider.type.type is an IdentifierType node
            return self.node.type.type.names[0] 
        except:
            #This will generally happen only when it is a struct that has already been declared, inside another struct
            return self.node.type.type.name


    #Returns the actual type of the TypeDeclaration, if not typedef'd it stays the same
    def get_actual_type(self):
        typedef_entry = self.outer.typedef_dict.get(self.typedecl_type)
        if typedef_entry != None:
            return typedef_entry
        else:
            return self.typedecl_type

    #Check if its actual_type is inside the struct dictionary: if so, return True
    def check_struct(self):
        struct_entry = self.outer.struct_dict.get(self.actual_type)   
 
        if struct_entry != None:
            return True
        else:
            return False

    def Factory(self):
        if self.is_struct:
            return StructTypeDeclaration(self)

        else:
            return RegularTypeDeclaration(self)

class RegularTypeDeclaration(TypeDeclaration):
    """ Handling a non-struct declaration node object
    """
    def __init__(self, parent, struct_name_val=""):
        #pdb.set_trace()
        TypeDeclaration.__init__(self, parent)
        self.type_of_var = self.actual_type #just renaming this for consistency
        self.ptr_depth = 0
        self.var_typerep = self.outer.primitive_types.get(self.type_of_var)
        self.var_name_val = struct_name_val + self.node.name
        self.var_new_val = True
        self.is_uninit = self.check_if_init()
        self.is_funcdecl = self.check_if_funcdecl()

    def check_if_init(self):
        if self.node.init == None:
            return True
        else:
            return False

    def check_if_funcdecl(self):
        return (isinstance(self.node.init, c_ast.FuncCall) and ((self.get_funccall_funcname() in self.func_list)))

    def Factory(self):
        if self.is_funcdecl:
            return InsideFuncCall(self)

        else:
            return AddPrintNode(self)

    def create_printf_node(self):
        add_id = c_ast.ID('printf')
        add_id_addr = None
        add_id_val = None
        add_id_size = None
        add_return_val = None
        add_id_ptr_size = None
        add_id_hex = None
        line_to_add = self.location_info.line_no
        
        line_no = "line:"+ (str)(line_to_add)
        function = (str)(self.outer.item_delimiter) +"function:"+ (str)(self.location_info.func_name)


        var_info = ""
        var_name = (str)(self.outer.item_delimiter) +"var_name:"+ (str)(self.var_name_val)
        add_id_addr = c_ast.ID('&(' + self.var_name_val+')')

        var_addr = (str)(self.outer.item_delimiter) +"addr:%p"
        var_type = (str)(self.outer.item_delimiter) +"type:"+ (str)(self.type_of_var)
        var_new = (str)(self.outer.item_delimiter) +"new:"+ (str)(self.var_new_val)

        #If on the stack, size is just the sizeof the variable name and location is stack
        location_info = "stack"

        var_location = (str)(self.outer.item_delimiter) +"location:"+location_info

        var_uninitialized = (str)(self.outer.item_delimiter) +"uninitialized:" + (str)(self.is_uninit)

        var_size = (str)(self.outer.item_delimiter) +"max_size:%lu"
        var_hex = (str)(self.outer.item_delimiter) +"hex_value:%lX"
        value_type_set = (str)(self.var_typerep)

        var_val = (str)(self.outer.item_delimiter) +"value:" + value_type_set

        var_free = ""
        is_global = ""
        var_isarray = ""
        var_is_ptr = ""
        var_ptr_size = ""
        returning_func = ""

        var_info = var_name + var_addr +var_type + var_new + var_hex + var_isarray +is_global +var_location +var_uninitialized + var_free+var_size + var_is_ptr + var_ptr_size + var_val

        add_id_val = c_ast.ID(self.var_name_val)
        add_id_hex = c_ast.ID(self.var_name_val)
        
        add_id_size = c_ast.ID('(unsigned long)(sizeof(' + self.var_name_val+'))')
 
        var_dict_add = {(str)(self.var_name_val):(str)(self.type_of_var)}
        self.outer.var_type_dict.update(var_dict_add)

        #Finished changed variable block
        str_to_add = (str)(self.outer.print_wrapper) + line_no + function + var_info 
        add_const = c_ast.Constant('string', '"'+str_to_add+'"')

        all_items_array = [add_const, add_id_addr, add_id_hex, add_id_size, add_id_ptr_size, add_id_val, add_return_val]
        exprlist_array = []
        for item in all_items_array:
            if item != None:
                exprlist_array.append(item)
        add_exprList = c_ast.ExprList(exprlist_array)

        new_node = c_ast.FuncCall(add_id, add_exprList)
        
        return new_node


class StructTypeDeclaration(TypeDeclaration):
    """ Handling a struct declaration node object
    """
    def __init__(self, parent):
        TypeDeclaration.__init__(self, parent)

#TODO: change this later as it is a subclass of many different types of parent nodes
class InsideFuncCall(RegularTypeDeclaration):
    """ Handling nodes that are being assigned to return values of functions inside our program
    """
    def __init__(self, parent):
        RegularTypeDeclaration.__init__(self, parent)

#TODO: change this later as it is a subclass of many different types of parent nodes
class AddPrintNode(RegularTypeDeclaration):
    """ Handling nodes that are being assigned to return values of functions inside our program
    """
    def __init__(self, parent):
        RegularTypeDeclaration.__init__(self, parent)
        self.print_node = self.create_printf_node()

    def Factory(self):
        if self.location_info.func_name == None:
            self.outer.global_print_nodes.append(self.print_node)
            return None
        else:
            place_to_add = self.location_info.added_before + self.location_info.initial_index + self.location_info.additional_space + 1
            self.location_info.parent.insert(place_to_add, self.print_node)
            self.location_info.added_after += 1
            return None

class LocationInfo(object):
    """ Info on how many nodes we have added before and after the current node we are examining.
        Also contains information on the specific parent array that we are adding to, as well as
        which index of that parent we are adding to, and the function it's in
    """

    #on initialization, parent[initial_index] would give us the current node we're examining. Once 
    #we add more nodes in front of it, we can access it by getting parent[initial_index+added_before]
    def __init__(self, parent, initial_index, func_name):
        self.parent = parent
        self.initial_index = initial_index
        self.added_before = 0
        self.added_after = 0 #self.amt_after
        self.index_to_add = None
        self.additional_space = 0  #self.extra_after
        self.func_name = func_name
        self.line_no = parent[initial_index].coord.line

