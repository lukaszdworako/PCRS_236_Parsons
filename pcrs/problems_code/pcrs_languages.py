import os
import subprocess
import sys
# from subprocess import TimeoutExpired
import subprocess


def set_path_to_languages():
    ''' Add all subdirectories in directory language to python path. '''
    
    lang_dir = '../languages/'

    module_dir = os.path.dirname(__file__)  # get current directory
    file_path = os.path.join(module_dir, lang_dir)
    abs_path = os.path.abspath(file_path)

    for fn in os.listdir(abs_path):
        lang_path = os.path.join(abs_path, fn)
        if os.path.isdir(lang_path):
            sys.path.append(lang_path)
            


class GenericLanguage(object):
    ''' Generic language representation. To add programming language, specify it 
        in self.lang and define corresponding language class. 
    '''

    def __init__(self, language=None):
        self.extensions = {'python' : '.py'}        

        if language == "python": 
            self.lang = PythonSpecifics()


    def encode_str(self, target_value):
        return self.lang.encode_str(target_value)

    def get_exec_trace(self, user_script, add_params):
        return self.lang.get_exec_trace(user_script, add_params)

    def run_test(self, user_script, test_input, exp_output):
        return self.lang.run_test(user_script, test_input, exp_output)

    def get_download_mimetype(self):
        return self.lang.get_download_mimetype()    
            

class BaseLanguage(object):
    ''' Base language representation with required methods provided. 
        No visualizer support is included by default. 
    '''

    def encode_str(self, target_value):
        ''' Return string by default. '''
        return target_value

    def run_test(self, user_script, test_input, exp_output):
        pass


class PythonSpecifics(BaseLanguage):
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
                
        except TimeoutExpired as ex: 
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
                        "import pg_logger_v3",
                        "import pg_encoder",
                        "code_lines =" + str(user_script.split("\n")),
                        "code = '\\n'.join(code_lines)",
                        "print(pg_logger_v3.exec_script_str(code," +\
                                                                cumulative_mode + "," + 
                                                                heap_primitives +" ))",
                        "exit()"]
        
            p = self.run_subprocess(script)
            p.wait(timeout=5)
            
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
                
        except TimeoutExpired as ex: 
            p.kill()
            data = {'trace' : None, 'exception' : 'Infinite loop or memory error' }
            
        except Exception as e:
            print(e)
            data = {'trace' : None, 'exception' : 'Unknown error' }
          
        return data
        

    def run_test(self, user_script, test_input, exp_output):
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
           
            code_lines = self.sanitize_user_script(user_script)
            
            script = [  "import sys, os", 
                        "import resource",
                        "resource.setrlimit(resource.RLIMIT_AS, (200000000, 200000000))",
                        "import pg_encoder"] +\
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
                ret["exception"] = stderr_output[-1].decode()
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
                ret['exp_test_val'] = eval(exp_test_val)

            p.stdout.close()
            p.stderr.close()
 
        except TimeoutExpired as ex: 
            ret["exception"] = str(ex)
            ret['passed_test'] = False
            ret['test_val'] = "Infinite loop or memory error"
            p.kill()
            
        except Exception as e:
            ret["exception"] = str(e) 
            ret['passed_test'] = False
            ret['test_val'] = str(e)

        finally: 
            return ret

    def run_subprocess(self, script):
        """ Run python subprocess executed with provided script. Return process p. """

        command = ['python']     
        module_dir = os.path.dirname(__file__)
        file_path = os.path.join(module_dir, '../languages/python/')
        abs_path = os.path.abspath(file_path)
        cwd_path = abs_path.replace("\\", r"\\")

        p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd = cwd_path)
        for line in script:
            p.stdin.write(bytearray(line + "\n", 'utf-8'))
        p.stdin.close()
        return p        

    def sanitize_user_script(self, user_script):
        ''' Return list of strings code_lines consisting of lines of code 
            after removing unsafe imports and not allowed builtins.
        '''

        safe_imports = ['math', 'random', 'datetime', 'functools', 'operator', 
                        'string', 'collections', 're', 'json', 'heapq', 'bisect']

        BANNED_BUILTINS = ('reload', 'input', 'apply', 'open', 'compile',
                           'file', 'eval', 'exec', 'execfile',
                           'exit', 'quit', 'raw_input', 'help',
                           'dir', 'globals', 'locals', 'vars')

        code_lines = user_script.split("\n")

        i = 0
        while(i < len(code_lines)): 
            line = code_lines[i]               
            if "import " in line:
                ind = line.find("import")
                pre_import = line[: ind + 7]
                import_list = line[ind + 7:].split()
                j = 0
                while(j < len(import_list)):
                    if import_list[j] not in safe_imports:
                        import_list.pop(j)
                    else:
                        j += 1
                new_code_line = pre_import + ", ".join(import_list)
                if new_code_line == pre_import:   
                    # if import consisted only of banned input, remove it
                    code_lines[i] = "" 
                else:
                    code_lines[i] = new_code_line

            # remove lines with banned builtins
            for banned_builtin in BANNED_BUILTINS:
                if banned_builtin in line:
                    code_lines[i] = "" 

            i += 1
        return code_lines


    def get_download_mimetype(self):
        ''' Return string with mimetype. '''

        return 'application/x-python'
       
        
        
