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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename  = sys.argv[1]
    else:
        filename = 'examples/c_files/year.c'

    ast = parse_file(filename, use_cpp=True,
            cpp_path='gcc',
            cpp_args=['-nostdinc','-E', r'-Iutils/fake_libc_include'])

    ast.show()
    inserted_node = create_printf_node()
    ast.show()
    ast.ext[0].body.block_items.insert(1, inserted_node)    
    recurse_nodes(ast)