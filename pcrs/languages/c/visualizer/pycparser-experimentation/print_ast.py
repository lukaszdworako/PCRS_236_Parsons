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


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print('Please provide a filename.')
        sys.exit()


    filename  = sys.argv[1]

    ast = parse_file(filename, use_cpp=True,
            cpp_path='gcc',
            cpp_args=['-nostdinc', '-E', r'-Iutils/fake_libc_include'])

    #ast.show()

    amt_of_functions = len(ast.ext)
    for i in range(0, amt_of_functions):
        #Note:ast.ext[0] gets the first function, .body gets the stuff under Compound, and block_items gets each group of elements under Compound
        body_node_list = ast.ext[i].body.block_items
        j = 0
        total_len = len(body_node_list)

        while j < total_len:
            print("node line num:" + (str)(body_node_list[j].coord.line))
            j += 1

    generator = c_generator.CGenerator()
    print(generator.visit(ast))
