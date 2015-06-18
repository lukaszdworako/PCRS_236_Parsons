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
        #func_list keeps track of all the function declaractions in our program
        self.func_list = []

        #Global hash variables, these are what we'll use to denote different parts of our added print statements

        #print_wrapper will hold the pattern we'll use to identify where our print statements begin and end
        self.print_wrapper = uuid.uuid4().hex

        #item_delimiter will hold the pattern we'll use to identify where different items in a single print statement begin and end
        self.item_delimiter = uuid.uuid4().hex

        #stdout_wrapper will hold the pattern we'll print right before and after each stdout line
        self.stdout_wrapper = uuid.uuid4().hex

        #stderr_wrapper will hold the pattern we'll print right before and after each stderr line
        self.stderr_wrapper = uuid.uuid4().hex

        #var_type_dict will hold a dictionary of all the variables we've seen, and their types - used for return val printing
        self.var_type_dict = {}

        #amt_after keeps track of the amount of print nodes we just added after the current node, used for returns
        self.amt_after = 0

        #cur_par_index keeps track of the index we're at for the current parent. Important to be global in the case where we
        #add nodes in front of our current node, we want to be able to increase this by more than 1
        self.cur_par_index = 0

    def add_printf(self, user_script):
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

            f.write(user_script)
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
        # find_all_function_decl(ast)
        # recurse_by_function(ast)
        # print("-----------------------")
        # ast.show()
        # print("-----------------------")
        # generator = c_generator.CGenerator()
        # print(generator.visit(ast))