import os, sys
import subprocess
import datetime
from pcrs.settings import PROJECT_ROOT, USE_SAFEEXEC, SAFEEXEC_USERID, SAFEEXEC_GROUPID
from languages.c.visualizer.cg_stacktrace import CVisualizer
import logging
import string

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
        # temp_runtime_error_file = self.temp_path + user + self.date_time + "_runtime_error.out"

        try:
            ret["exception_type"] = self.compilation_ret["exception_type"]
            ret["exception"] = self.compilation_ret["exception"]
            if self.compilation_ret["exception_type"] == "error":
                raise CompilationError

            # Test input and expected output data
            test_input = str(test_input)
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
                process = subprocess.call(safe_exec + " -o " + temp_output_file + " -d " + max_process_mem
                                + " -U " + SAFEEXEC_USERID + " -G " # + " -e " + temp_runtime_error_file
                                + SAFEEXEC_GROUPID + " -T " + max_time_sec + " -F " + max_number_files
                                + " -f " + max_file_size + " -q " + self.compilation_ret["temp_gcc_file"]
                                + " " + test_input + " > /dev/null 2> /dev/null", shell=True)
            else:
                process = subprocess.call(self.compilation_ret["temp_gcc_file"] + " " + test_input + " > " + temp_output_file, shell=True)
                # + " 2> " + temp_runtime_error_file

            # Getting the execution output
            f = open(temp_output_file, 'r', encoding="ISO-8859-1")
            execution_output = f.read()
            f.close()

            # Runtime error during process execution (ignore warning errors)
            if process != 0 and ret["exception"] == " ":
                execution_output = 'Runtime error!'
                ret["exception_type"] = "warning"
                ret["exception"] = "Runtime error!<br />Please check your code for errors such as segmentation faults."

            # Getting the run time error output
            #f = open(temp_runtime_error_file, 'r')
            #runtime_error = f.read()
            #if runtime_error:
            #    print("===== safeexec runtime error=====\n", runtime_error, "==========")   # To system error log. Probably better to activity log.
            #f.close()

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
            #try:
            #    os.remove(temp_runtime_error_file)
            #except OSError:
            #    pass
            # print(ret["exception_type"] + ": " + ret["exception"])
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

    def get_exec_trace(self, user_script, add_params):
        """ Return dictionary ret containing all variables results.
            ret has the following mapping:
            'exception' (only if exception occurs) -> exception message.
            'trace' -> program trace.
        """
        logger = logging.getLogger('activity.logging')

        user = add_params['user']
        temp_path = os.getcwd()
        test_input = add_params['test_case']
        deny_warnings = True

        # Compile code checking for invalid changes after submission
        ret = self.compile_source_code(user, user_script, deny_warnings)

        # Remove compiled file
        self.clear_exec_file(ret["temp_gcc_file"])
        # Return compilation/warning error if it exists
        if ret['exception_type'] != 'warning' and ret['exception'] != ' ':
            return {'trace': None, 'exception': ret["exception"]}

        c_visualizer = CVisualizer(user, temp_path)
        logger.info("gets here 1")
        # Build initial stack with functions and variables data
        #Each element of stack trace contains a dictionary for a
        #function in the code(one element per function, ie. stacktrace[0]
        #is the main function, etc)

        #stack_trace = c_visualizer.build_stacktrace(user_script)
        #logger.info("gets here 2")
        #for item in stack_trace:
        #    logger.info(item)



        # Change original source code with the proper printf (debug)
        #mod_user_script = c_visualizer.change_code_for_debbug(stack_trace, user_script)
        #print(user_script)

        mod_user_script = c_visualizer.add_printf(user_script)

        logger.info("here 3")
        # Compile and run the modified source code and remove compiled file
        code_output = self.run_test_visualizer(test_input, user, mod_user_script, deny_warnings)
        #print(code_output.get("test_val"))

        if 'exception_type' in code_output and code_output['exception_type'] != 'error':
            # Get the proper encoding for the javascript visualizer
            json_output = self.code_output_to_json((str)(code_output.get("test_val")), c_visualizer.print_wrapper, c_visualizer.item_delimiter)
            return json_output

        else:
            # Return error to user
            return {"error": code_output}

    def get_download_mimetype(self):
        """ Return string with mimetype. """
        return 'text/x-c'



    def hex_pad(self, value, length):
        # Length is in bytes
        return ("0x" + value.zfill(length*2)).lower();

    def convert_bool_strs(self, line_info):
        for k,v in line_info.items():
            if v.lower() == "true":
                line_info[k] = True
            elif v.lower() == "false":
                line_info[k] = False

    def code_output_to_json(self, code_output, block_delim, print_delim):
        """ Convert the code output into a dictionary to be converted into a JSON file """

        json_output = { "global_vars": [], "steps": [] }

        current_step_number = 0
        current_line = None
        current_step = {}


        pprint(code_output)
        pdb.set_trace()

        # Split the output into blocks of print statements
        print_blocks = code_output.split(block_delim)
        for print_statement in filter(None, print_blocks):
            # Make a dictionary out of all of parts of the line
            line_info_list = print_statement.split(print_delim)
            line_info = { info.split(':',1)[0]: info.split(':',1)[1] for info in line_info_list }


            # If we're on a new line, save the current step and start new one
            if line_info['line'] != current_line:
                if current_step:
                    json_output["steps"].append(current_step)

                current_line = int(line_info['line'])
                current_step_number = current_step_number + 1
                current_step = {
                    "step": current_step_number,
                    "line": current_line,
                    "student_view_line": current_line, # TODO: Adjust correctly
                    "function": line_info['function']
                    }




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

                # Pad each hex value to the length of max_size
                # Arbitrarily chosen size of 8 bytes for anything without a max_size specified
                max_size = int(line_info['max_size']) if ('max_size' in line_info) else 8

                current_var = dict(line_info)
                self.convert_bool_strs(current_var)
                del(current_var['line'])
                del(current_var['function'])


                current_var['addr'] = self.hex_pad(line_info['addr'][2:], self.max_addr_size)
                current_var['hex_value'] = self.hex_pad(line_info['hex_value'], max_size)

                # Pointers values must always be as wide as an address
                if '*' in current_var['type']:
                    current_var['value'] = self.hex_pad(current_var['value'][2:], self.max_addr_size)

                current_step['changed_vars'].append(current_var)



        json_output["steps"].append(current_step)
        return json_output
