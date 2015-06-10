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
    add_const = c_ast.Constant('string', '"%dhello world"')
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
    if isinstance(parent[index], c_ast.FuncCall) and isinstance(parent[index].args.exprs[0], c_ast.Constant) and (parent[index].args.exprs[0].value =='"%dhello world"'):
        return

    ast_function = parent[index]
    print(ast_function)
    print_node = create_printf_node()
    parent.insert(index+1, print_node)
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