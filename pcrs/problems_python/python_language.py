import os
import subprocess
import sys

import problems.pcrs_languages as languages


class IllegalInputCode(ValueError):
    pass


class PythonSpecifics(languages.BaseLanguage):
    ''' Representation of Python language (visualizer supported):
        * string encoding in visualizer format,
        * generation of execution trace for visualizer,
        * running tests
    '''

    def encode_str(self, target_value):
        ''' Encode string target_value in visualizer format. '''

        # pg_logger_v3.exec_script_str(tc.test_output, False, False, True)

        try:

            script = [  "import sys",
                        "import resource",
                        "resource.setrlimit(resource.RLIMIT_AS, (200000000, 200000000))",
						"resource.setrlimit(resource.RLIMIT_CPU, (3, 3))",    # 3 seconds of CPU. Insurance.
                        "import pg_encoder",
                        "expected_val =" + str(target_value),
                        "print(pg_encoder.encode(expected_val, True))",
                        "exit()"]

            p = self.run_subprocess(script)
            p.wait(timeout=1)

            output = p.stdout.readlines()
            trace = eval(output[-1].decode().strip())

            stderr_output = p.stderr.readlines()

            p.stdout.close()
            p.stderr.close()

            if len(stderr_output) > 0:
                trace = None

        except subprocess.TimeoutExpired as ex:
            p.kill()
            trace = None

        except Exception as e:
            print(e)
            trace = str(e)

        return trace

    def get_exec_trace(self, user_script, add_params):
        ''' Get execution trace of string user_script providing additional parameters. '''

        try:
            cumulative_mode = add_params["cumulative_mode"].capitalize()
            heap_primitives = add_params["heap_primitives"].capitalize()

            script = [  "import sys",
                        "import resource",
                        "resource.setrlimit(resource.RLIMIT_AS, (200000000, 200000000))",
						"resource.setrlimit(resource.RLIMIT_CPU, (3, 3))",    # 3 seconds of CPU. Insurance.
                        "import pg_encoder",
                        "import pg_logger_v3",
                        "code_lines =" + str(user_script.split("\n")),
                        "code = '\\n'.join(code_lines)",
                        "print(pg_logger_v3.exec_script_str(code," +\
                                                                cumulative_mode + "," +
                                                                heap_primitives +" ))",
                        "exit()"]

            p = self.run_subprocess(script)
            p.wait(timeout=3)

            output = p.stdout.readlines()
            data = output[-1].decode()

            stderr_output = p.stderr.readlines()

            p.stdout.close()
            p.stderr.close()

            if len(stderr_output) > 0:
                # print(stderr_output)
                exc = stderr_output[-1].decode()
                data = {'trace' : None, 'exception' : exc }

            else:
                data = eval(data)

        except subprocess.TimeoutExpired as ex:
            p.kill()
            data = {'trace' : None, 'exception' : 'Infinite loop or memory error' }

        except Exception as e:
            print(e)
            data = {'trace' : None, 'exception' : 'Unknown error' }

        return data


    def run_test(self, user_script, test_input, exp_output, pre_code=""):
        ''' Return dictionary ret containing results of a testrun.
            ret has the following mapping:
            'test_val' -> encoded for visualizer format test output.
            'passed_test' -> boolean
            'exception' (only if exception occurs) -> exception message.
        '''
        try:
            ret = {}
            user_script = str(user_script)
            test_input = str(test_input)
            exp_output = str(exp_output)

            # calling the resulting value is always last
            test_params = test_input.split('; ')
            if pre_code:
                prepended_code = pre_code.split('\n')
            else:
                prepended_code = []
            code_lines = self.sanitize_user_script(user_script)

            script = [  "import sys, os",
                        "import resource",
                        "resource.setrlimit(resource.RLIMIT_AS, (200000000, 200000000))",
						"resource.setrlimit(resource.RLIMIT_CPU, (3, 3))",    # 3 seconds of CPU. Insurance.
                        "import pg_encoder",
                        "import pg_logger_v3"] +\
                        prepended_code +\
                        code_lines +\
                        test_params[: -1] +\
                        ["result = " + test_params[-1],
                        "exp_output = " + exp_output,
                        "try:",
                        "\texpected_val = eval(exp_output)",
                        "except Exception as e:",
                        "\texpected_val = exp_output",
                        "passed_test = result == expected_val",
                        "test_val = pg_encoder.encode(result, True)",
                        "exp_test_val = pg_encoder.encode(expected_val, True)",
                        "print(test_val)",
                        "print(passed_test)",
                        "print(exp_test_val)",
                        "exit()"]

            p = self.run_subprocess(script)
            p.wait(timeout=2)

            stderr_output = p.stderr.readlines()
            if len(stderr_output) > 0:
                if 'SyntaxError' in stderr_output[-1].decode():
                    ret['exception'] = '<br />'.join([line.decode().replace('\n', '').replace(' ', '&nbsp;') for line in stderr_output[-3:]])
                else:
                    ret['exception'] = stderr_output[-1].decode()
                ret['passed_test'] = False
                ret['test_val'] = ret["exception"]

            else:
                # ignore user print statements
                output = p.stdout.readlines()[-3: ]
                test_val = output[0].decode().strip()
                passed_test = output[1].decode().strip()
                exp_test_val = output[2].decode().strip()

                ret['test_val'] = eval(test_val)
                ret['passed_test'] = eval(passed_test)
                ret['expected_output'] = eval(exp_test_val)

            p.stdout.close()
            p.stderr.close()

        except subprocess.TimeoutExpired as ex:
            ret['exception'] = str(ex)
            ret['passed_test'] = False
            ret['test_val'] = "Infinite loop or memory error"
            p.kill()

        except IllegalInputCode as ex:
            ret['exception'] = str(ex)
            ret['passed_test'] = False
            ret['test_val'] = "Submission contained invalid string"

        except Exception as e:
            ret['exception'] = str(e)
            ret['passed_test'] = False
            ret['test_val'] = str(e)

        return ret

    def run_subprocess(self, script):
        ''' Run python subprocess executed with provided script. Return process p.
        '''

        command = ['python3']
        module_dir = os.path.dirname(__file__)
        file_path = os.path.join(module_dir, '../languages/python/')
        abs_path = os.path.abspath(file_path)
        cwd_path = abs_path.replace("\\", r"\\")

        p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd_path)
        for line in script:
            p.stdin.write(bytearray(line + "\n", 'utf-8'))
        p.stdin.close()
        return p

    def sanitize_user_script(self, user_script):
        ''' Return list of strings code_lines consisting of lines of code
            after removing unsafe imports and not allowed builtins.
        '''

        safe_imports = ['math', 'random', 'datetime', 'functools', 'operator',
                        'string', 'collections', 're', 'json', 'heapq', 'bisect',
                        'numpy', 'scipy', 'typing', 'io']

        BANNED_BUILTINS = ('reload', 'input', 'apply', 'open', 'compile',
                           'file', 'eval', 'exec', 'execfile',
                           'exit', 'quit', 'raw_input', 'help',
                           'dir', 'globals', 'locals', 'vars')

        code_lines = user_script.split("\n")

        import_statement = "import {0}"
        import_as_variable = "{0} = {1}"

        i = 0
        while(i < len(code_lines)):
            line = code_lines[i]
            # hack for import as statements; imports the module and sets
            # the variable after "as" to point to that module
            if ("import " in line) and ("as " in line):
                short_ind = line.find("as")
                short_name = line[short_ind + 3:].split()[0]
                import_ind = line.find("import")
                import_name = line[import_ind + 7:].split()[0]
                if import_name in safe_imports:
                    code_lines[i] = import_statement.format(import_name)
                    i += 1
                    code_lines.insert(i, import_as_variable.format(short_name, import_name))
                else:
                    raise IllegalInputCode("The import '{0}' was found in your program; please remove it.".format(import_name))

            # hack for "from ... import" statements; imports the module and
            # sets the variable to point to that item
            elif ("from" in line) and (" import " in line):
                from_ind = line.find("from ")
                import_ind = line.find("import")
                import_name = line[from_ind + 5: import_ind].strip()
                short_names = line[import_ind + 6:].split(',')
                if import_name in safe_imports:
                    code_lines[i] = import_statement.format(import_name)
                    for sname in short_names:
                        i += 1
                        code_lines.insert(i, "{0} = {1}.{0}".format(sname.strip(), import_name))
                else:
                    raise IllegalInputCode("The import '{0}' was found in your program; please remove it.".format(import_name))

            elif "import " in line:
                ind = line.find("import")
                pre_import = line[: ind + 7]
                import_list = line[ind + 7:].split()
                for item in import_list:
                    if item not in safe_imports:
                        raise IllegalInputCode("The import '{0}' was found in your program; please remove it.".format(item))

            # remove lines with banned builtins
            for banned_builtin in BANNED_BUILTINS:
                if banned_builtin in line:
                    raise IllegalInputCode("The string '{0}' was found in your program; please remove it.".format(banned_builtin))

            i += 1
        return code_lines


    def get_download_mimetype(self):
        ''' Return string with mimetype. '''

        return 'application/x-python'
