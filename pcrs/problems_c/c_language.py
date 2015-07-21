import os, sys
import subprocess
import datetime
from pcrs.settings import PROJECT_ROOT, USE_SAFEEXEC, SAFEEXEC_USERID, SAFEEXEC_GROUPID
from languages.c.visualizer.cg_stacktrace import CVisualizer
import logging
import string
import re
from operator import mul
from functools import reduce
import shlex
import ast

from pprint import pprint
import pdb

class CompilationError(Exception):
    pass

class CSpecifics():
    """ Representation of C language:
        * running tests
    """
    # Compilation status and flags
    compiled = False
    compilation_ret = {}
    # File name addendum
    date_time = str((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())
    # Temporary directory path where the temporary C files and output files will be saved
    temp_path = PROJECT_ROOT + "/languages/c/execution/temporary/"
    # Username
    username = ""
    # Problem source code
    submission = ""

    def __init__(self, username, submission):
        self.username = username
        self.submission = submission

        # Get the size of an address on this machine
        self.max_addr_size = 8 if (sys.maxsize > 2**32) else 4

    def run_test_visualizer(self, test_input, username, source_code, deny_warnings=True):
        self.username = username
        self.submission = source_code
        self.compiled = False

        ret = self.run_test(test_input, test_input, deny_warnings)
        self.clear_exec_file(self.compilation_ret["temp_gcc_file"])

        return ret

    def run_test(self, test_input, expected_output, deny_warnings=False):
        """ Return dictionary ret containing results of a testrun.
            ret has the following mapping:
            'test_val' -> test output.
            'passed_test' -> boolean
            'exception' (only if exception occurs) -> exception message.
            'runtime_error' (only if a runtime error occurs) -> error message.
            'warning' (only if warning occurs) -> warning message.
        """
        ret = {}
        user = str(self.username)
        user_script = str(self.submission)

        # Compile C source code
        if not self.compiled:
            self.compilation_ret = self.compile_source_code(user, user_script, deny_warnings)
        # Naming the temporary output file
        temp_output_file = self.temp_path + user + self.date_time + ".out"
        # Naming the temporary runtime error file
        temp_runtime_error_file = self.temp_path + user + self.date_time + "_runtime_error.out"

        try:
            ret["exception_type"] = self.compilation_ret["exception_type"]
            ret["exception"] = self.compilation_ret["exception"]
            if self.compilation_ret["exception_type"] == "error":
                raise CompilationError

            # Test input and expected output data
            # Wrap each argument in '' and escape metacharacters
            test_input = " ".join([shlex.quote(c) for c in test_input.split(" ")])
            expected_output = str(expected_output)

            if USE_SAFEEXEC:
                # Safeexec path
                safe_exec = PROJECT_ROOT + "/languages/c/execution/safeexec_master/safeexec"

                # C safe execution parameters
                max_time_sec = "10"  # 10 seconds
                max_process_mem = "40960"  # 40 megabytes
                max_number_files = "20"  # 20 files -- need some runtime libraries
                max_file_size = "5120"  # 5 megabytes

                # Running C program in a secure environment
                cmd_str = safe_exec + " -o " + temp_output_file + " -d " + max_process_mem \
                                + " -U " + SAFEEXEC_USERID + " -G " + SAFEEXEC_GROUPID + " -e " \
                                + temp_runtime_error_file + " -T " + max_time_sec + " -F " + max_number_files \
                                + " -f " + max_file_size + " -q " + self.compilation_ret["temp_gcc_file"] \
                                + " " + test_input + " > /dev/null 2> /dev/null"
                process = subprocess.call(cmd_str, shell=True)
            else:
                process = subprocess.call(self.compilation_ret["temp_gcc_file"] + " " + test_input + " > " + temp_output_file + " 2> " + temp_runtime_error_file, shell=True)

            # Runtime error during process execution (ignore warning errors)
            if process != 0:
                print("Exit code: " + str(process))
                execution_output = 'Runtime error!'
                ret["exception_type"] = "error"
                ret["runtime_error"] = "Runtime error!<br />Please check your code for errors such as segmentation faults."

            # Getting the execution output
            f = open(temp_output_file, 'r', encoding="ISO-8859-1")
            execution_output = f.read()
            f.close()

            # Getting the run time error output
            f = open(temp_runtime_error_file, 'r')
            runtime_error = f.read()
            if runtime_error:
                print("===== safeexec runtime error =====\n", runtime_error, "==========")   # To system error log. Probably better to activity log.
                ret["runtime_error"] = runtime_error
            f.close()

            # Remove escape sequences in case of a string instance
            if isinstance(expected_output, str):
                expected_output_tmp = expected_output.replace('\n', "").replace('\r', "").replace(" ", "")
            else:
                expected_output_tmp = expected_output

            # Remove escape sequences in case of a string instance
            if isinstance(execution_output, str):
                execution_output_tmp = execution_output.replace('\n', "").replace('\r', "").replace(" ", "")
            else:
                execution_output_tmp = execution_output

            ret["test_val"] = execution_output
            ret["passed_test"] = False if expected_output_tmp != execution_output_tmp else True

        except CompilationError as e:
            ret["passed_test"] = False
            ret["exception_type"] = 'error'
            ret["test_val"] = ret["exception"]

        except SyntaxError as e:
            ret["exception_type"] = 'error'
            ret["exception"] = str(e)
            ret['passed_test'] = False
            ret['test_val'] = str(e)

        except Exception as e:
            ret["exception_type"] = 'error'
            ret["exception"] = str(e)
            ret['passed_test'] = False
            ret['test_val'] = str(e)

        finally:
            # Deleting temporary files
            try:
                os.remove(temp_output_file)
            except OSError:
                pass
            try:
                os.remove(temp_runtime_error_file)
            except OSError:
                pass
            print(ret["exception_type"] + ": " + ret["exception"])
            return ret

    def compile_source_code(self, user, user_script, deny_warning=False):

        # Naming the C file
        temp_c_file = self.temp_path + user + self.date_time + ".c"
        # Naming the file which the gcc creates
        temp_gcc_file = self.temp_path + user + self.date_time + ".o"
        # Naming the temporary error file
        temp_error_file = self.temp_path + user + self.date_time + "_error.out"
        # Compilation flags
        flags = "-Wall"

        ret = {"temp_gcc_file": temp_gcc_file}
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

            # Compiling the C file
            subprocess.call("gcc " + flags + " " + temp_c_file + " -o " + temp_gcc_file + " 2> " + temp_error_file,
                            shell=True)

            # Getting the error output to check if there were any compilation errors
            f = open(temp_error_file, 'r')
            compilation_alert = f.read()
            f.close()

            # Check compilation alerts (errors and warnings)
            if compilation_alert:
                # Removing the temporary path of the string
                compilation_alert = compilation_alert.replace(self.temp_path, "")
                # Removing the file name from the error string
                compilation_alert = compilation_alert.replace((user + self.date_time + ".c:"), '')
                # Check for compilation, or warning errors
                if not compilation_alert.find("warning") != -1:
                    ret["exception_type"] = "error"
                    ret["exception"] = str("Compilation Error:\n" + compilation_alert).replace('\n', '<br />')
                elif not deny_warning:
                    ret["exception_type"] = "warning"
                    ret["exception"] = str("Compilation Warning:\n" + compilation_alert).replace('\n', '<br />')
                else:
                    ret["exception_type"] = " "
                    ret["exception"] = " "
            else:
                ret["exception_type"] = " "
                ret["exception"] = " "

        except Exception as e:
            ret["exception_type"] = "error"
            ret["exception"] = "Compilation Error\n"

        finally:
            # Check compilation flag
            self.compiled = True
            # Deleting temporary files
            try:
                os.remove(temp_c_file)
            except OSError:
                pass
            try:
                os.remove(temp_error_file)
            except OSError:
                pass
            return ret

    def clear_exec_file(self, file_location):
        try:
            os.remove(file_location)
        except OSError:
            pass
        self.compiled = False

    def get_exec_trace(self, user_script, add_params, hidden_lines_list):
        """ Return dictionary ret containing all variables results.
            ret has the following mapping:
            'exception' (only if exception occurs) -> exception message.
            'trace' -> program trace.
        """
        logger = logging.getLogger('activity.logging')

        user = add_params['user']
        test_input = add_params['test_case']
        deny_warnings = True

        # Compile code checking for invalid changes after submission
        ret = self.compile_source_code(user, user_script, deny_warnings)

        # Remove compiled file
        self.clear_exec_file(ret["temp_gcc_file"])
        # Return compilation/warning error if it exists
        if ret['exception_type'] != 'warning' and ret['exception'] != ' ':
            return {'trace': None, 'exception': ret["exception"]}

        c_visualizer = CVisualizer(user, self.temp_path)

        # Build initial stack with functions and variables data
        #Each element of stack trace contains a dictionary for a
        #function in the code(one element per function, ie. stacktrace[0]
        #is the main function, etc)

        mod_user_script = c_visualizer.add_printf(user_script)

        #logger.info("--------------")
        #print(mod_user_script)
        #logger.info("--------------")
        # Compile and run the modified source code and remove compiled file
        code_output = self.run_test_visualizer(test_input, user, mod_user_script, deny_warnings)

        if 'exception_type' in code_output and code_output['exception_type'] != 'error':
            # Get the proper encoding for the javascript visualizer
            json_output = self.code_output_to_json((str)(code_output.get("test_val")), c_visualizer, hidden_lines_list)
            return json_output

        else:
            # Return error to user, we will remove this once we put to production
            #TODO: Compiler is letting users declare function header variables with no type, but this messes up visualizer - change this to restrict!!! - Julianna
            return {"error": code_output}

    def get_download_mimetype(self):
        """ Return string with mimetype. """
        return 'text/x-c'


    def to_hex(self, dec_num):
        return self.hex_pad(hex(dec_num)[2:], 8)

    def hex_pad(self, value, length):
        # Length is in bytes
        return ("0x" + value.zfill(length*2)).lower();

    def convert_bool_strs(self, line_info):
        for k,v in line_info.items():
            if v.lower() == "true":
                line_info[k] = True
            elif v.lower() == "false":
                line_info[k] = False

    """ Convert a list of values into the correct format """
    def parse_value(self, current_var, sizes_by_level):
        value = current_var['value']
        hex_value = current_var['hex_value']
        value_type = current_var['type']
        is_uninitialized = current_var['uninitialized']

        # Collapse spaces to judge the type accurately
        value_type = value_type.replace(" ", "")

        # Currently only handles arrays, not structs
        if("[]" in value_type):
            # TODO: Handle arrays recursively by creating a list of dictionaries, similar to changed_vars
            # Find at which level we are and go down one level
            level = value_type.count("[]")
            next_type = value_type.replace("[]","",1)
            start_addr = int(current_var["addr"], 16)

            # The last one in the array is the base array size
            base_size = sizes_by_level[len(sizes_by_level)-1]

            # Multiply the rest of the sizes to get the size of an element at this level
            level_size = reduce(mul, sizes_by_level[len(sizes_by_level) - level:], 1)

            # Turn everything inside the opening and closing brackets into an array
            ar_values = value
            ar_hex_values = hex_value

            # Create an array of dictionaries for each of the values in ar_values
            new_values_array = []
            for i in range(len(ar_values)):
                new_var = {}
                new_var["var_name"] = ""
                new_var["addr"] = self.to_hex(start_addr + (i * level_size))
                new_var["type"] = next_type
                new_var["new"] = True
                new_var["hex_value"] = self.hex_pad(ar_hex_values[i], level_size) if level == 1 else ar_hex_values[i]
                new_var["invalid"] = False
                new_var["location"] = current_var["location"]
                new_var["max_size"] = level_size
                new_var["uninitialized"] = is_uninitialized

                is_ptr = (level == 1) and (next_type.count('*') > 0)
                new_var["is_ptr"] = is_ptr
                new_var["ptr_size"] = base_size if is_ptr else 0

                new_var["value"] = ar_values[i]
                new_var["value"] = self.parse_value(new_var, sizes_by_level)

                new_values_array.append(new_var)

            return new_values_array

        else:
            # Pointers values must always be as wide as an address
            if '*' in value_type:
                value = self.hex_pad(value[2:], self.max_addr_size)

            # If not a pointer, return the value as is
            return value

    def parse_var(self, line_info):
        current_var = dict(line_info)

        # Pad each hex value to the length of max_size
        # Arbitrarily chosen size of 8 bytes for anything without a max_size specified
        max_size = int(current_var['max_size']) if ('max_size' in current_var) else 8

        self.convert_bool_strs(current_var)
        del(current_var['line'])
        del(current_var['function'])

        current_var['addr'] = self.hex_pad(current_var['addr'][2:], self.max_addr_size)

        sizes_by_level = []
        if 'array' in current_var:
            sizes_by_level = ast.literal_eval(current_var['arr_dims'].replace(',]', ']'))
            sizes_by_level.append(int(current_var['arr_type_size']))

            # For arrays, the 'value' and 'hex_value' properties will be arrays in string form, like "[['1','2'],['3','4']]" and "[['0x01','0x02'],['0x03','0x04']]"
            current_var['value'] = ast.literal_eval(current_var['value'].replace(',]', ']'))
            current_var['hex_value'] = ast.literal_eval(current_var['hex_value'].replace(',]', ']'))

        else:
            current_var['hex_value'] = self.hex_pad(current_var['hex_value'], max_size)

        current_var['value'] = self.parse_value(current_var, sizes_by_level)

        return current_var

    def code_output_to_json(self, code_output, c_visualizer, hidden_lines_list):
        """ Convert the code output into a dictionary to be converted into a JSON file """

        block_delim = c_visualizer.print_wrapper
        print_delim = c_visualizer.item_delimiter


        json_output = {
            "global_vars": [],
            "steps": []
        }


        current_step_number = 0
        current_line = None
        current_step = {}

        # Split the output into blocks of print statements
        print_blocks = code_output.split(block_delim)
        for print_statement in filter(None, print_blocks):
            # Make a dictionary out of all of parts of the line
            line_info_list = print_statement.split(print_delim)
            pprint(line_info_list)
            line_info = { info.split(':',1)[0]: info.split(':',1)[1] for info in line_info_list }
            print(line_info)

            if 'global' in line_info:
                current_var = self.parse_var(line_info)
                json_output["global_vars"].append(current_var)

            else:
                # If we reach a new line, save the current step and start new one
                if int(line_info['line']) != current_line:
                    if current_step:
                        json_output["steps"].append(current_step)

                    current_line = int(line_info['line'])

                    # Adjust the actual lines correctly
                    adjustment = len([l for l in hidden_lines_list if l < current_line])
                    student_view_line = current_line - adjustment

                    current_step_number = current_step_number + 1
                    current_step = {
                        "step": current_step_number,
                        "line": current_line,
                        "student_view_line": student_view_line,
                        "function": line_info['function']
                        }


                if 'std_out' in line_info:
                    # Add stdout information
                    current_step['std_out'] = line_info['std_out']
                    del(line_info['std_out'])

                if 'std_err' in line_info:
                    # Add stderr information
                    current_step['std_err'] = line_info['std_err']
                    del(line_info['std_err'])

                if 'return' in line_info:
                    # Add a "return" info
                    current_step['return'] = line_info['return']
                    del(line_info['return'])

                if 'on_entry_point' in line_info:
                    # Add a info for the entry point of a function
                    current_step['on_entry_point'] = True
                    del(line_info['on_entry_point'])

                if 'returned_fn_call' in line_info:
                    # Add info for returning from a function call
                    current_step['returned_fn_call'] = line_info['returned_fn_call']
                    del(line_info['returned_fn_call'])

                if 'var_name' in line_info:
                    # There is a variable to add to changed_vars
                    if not 'changed_vars' in current_step:
                        current_step['changed_vars'] = []


                    current_var = self.parse_var(line_info)

                    current_step['changed_vars'].append(current_var)

        # Append the last step
        json_output["steps"].append(current_step)

        pprint(json_output)
        return json_output
