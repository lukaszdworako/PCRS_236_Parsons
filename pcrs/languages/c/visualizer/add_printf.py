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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename  = sys.argv[1]
    else:
        filename = 'examples/c_files/year.c'

    ast = parse_file(filename, use_cpp=True,
            cpp_path='gcc',
            cpp_args=['-nostdinc','-E', r'-Iutils/fake_libc_include'])

    ast.show()



    #Going to try a diff approach since this doesn't go deep enough if there's assignments in if statements, etc: 
    #can I get where all the assignments & declarations are?
    #write a recursive tree search that returns the parent and the # index of the node, so we can add a print statement right after it.
    amt_of_functions = len(ast.ext)
    for i in range(0, amt_of_functions):
	    #Note:ast.ext[0] gets the first function, .body gets the stuff under Compound, and block_items gets each group of elements under Compound
        body_node_list = ast.ext[i].body.block_items
        j=0
        total_len = len(body_node_list)
        while j < total_len:
            if isinstance(body_node_list[j], c_ast.Decl) or isinstance(body_node_list[j], c_ast.Assignment):
                if isinstance(body_node_list[j], c_ast.Decl):
                    var_name = (str)(body_node_list[j].name)
                else:
                    var_name = (str)(body_node_list[j].lvalue.name)
                    print("node line num:"+(str)(body_node_list[j].coord.line)+" name: " +var_name)
                node_to_insert = create_printf_node()
                body_node_list.insert(j+1, node_to_insert)
                j += 1
                total_len += 1
            j += 1
	    

    # new_node.show()

    # node_to_add_after = ast.ext[0].body.block_items[1]
    # node_to_add_after.show()

    # ast.ext[0].body.block_items.insert(2, new_node)

    # ast.show()
    generator = c_generator.CGenerator()
    print(generator.visit(ast))