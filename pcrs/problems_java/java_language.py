import sys
import os
import shutil
import subprocess
import tempfile
import re
from datetime import datetime

from pcrs.settings import PROJECT_ROOT
from problems.pcrs_languages import BaseLanguage


class CompilationError(Exception):
    pass


class JavaSpecifics(BaseLanguage):
    ''' Representation of Java language:
        * string encoding in visualizer format,
        * generation of execution trace for visualizer,
        * running tests

        TODO: no visualizer support currently provided
              see http://www.pythontutor.com/java.html#mode=edit
              for a tool that could be used to provide support
        TODO: execution not yet supported
    '''

    temp_path = PROJECT_ROOT + "/languages/java/execution/temporary/"

    def __init__(self, *args, **kwargs):
        BaseLanguage.__init__(self, *args, **kwargs)
        self.compiled = False
        self.tempdir = None
        self.classname = None

    def encode_str(self, target_value):
        ''' Encode string target_value in visualizer format.
        '''
        raise NotImplementedError("Visualization not yet supported")

    def get_exec_trace(self, user_script, add_params):
        ''' Get execution trace of string user_script providing additional parameters.
        '''
        raise NotImplementedError("Visualization not yet supported")

    def run_test(self, test_input, exp_output):
        ''' Return dictionary ret containing results of a testrun.
            ret has the following mapping:
            'test_val' -> encoded for visualizer format test output.
            'passed_test' -> boolean
            'exception' (only if exception occurs) -> exception message.
        '''
        ret = {'passed_test': False,
               'test_val': ''}
        if not self.compiled:
            ret['exception'] = "Code could not be compiled before test execution"
            return ret

        try:
            command = ["java {0} {1}".format(self.classname, test_input)]

            # 8 second timeout on run
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.tempdir, shell=True, universal_newlines=True)
            output, err = proc.communicate(timeout=8)
        except subprocess.TimeoutExpired as e:
            try:
                proc.kill()
            except:    # May already have terminated or been killed
                pass
            ret['exception_type'] = 'error'
            ret['runtime_error'] = "Timeout expired: do you have an infinite loop?"
            ret['test_val'] = "Timeout"
        except Exception as e:
            print(e)
            raise
        else:
            if err:
                error_str = err.replace(self.tempdir + os.sep, '').replace('\n', '<br />')
                ret['exception_type'] = 'error'
                ret['runtime_error'] = "Runtime Error: " + error_str
                ret['test_val'] = 'Runtime Error'
            else:
                ret["test_val"] = output.strip()
                ret["passed_test"] = exp_output.strip() == output.strip()
        return ret

    def compile(self, user, user_code, deny_warning=False):
        ''' Compile the given user code, raising a compile error if unable.
        '''
        try:
            self.classname = re.search('public class (\w+)', user_code).group(1)
        except AttributeError:     # class name not found
            raise CompilationError("'public static classname' not found during compilation")

        if self.compiled:
            return

        # Sanitize classname and usercode
        if '..' in self.classname:
            raise CompilationError("'{0}' is not a valid class name".format(self.classname))
        self._sanitize_user_program(user_code)

        # From this point on, we need to delete the tempdir if there is a failure.
        try:
            self.tempdir = tempfile.mkdtemp(prefix="{0}-{1}-".format(user, datetime.now().strftime('%m%d-%H:%M:%S'), dir=self.temp_path), dir=self.temp_path)
            source_fname = "{0}{1}{2}.java".format(self.tempdir, os.sep, self.classname)
            open(source_fname, "w").write(user_code)

            # Actual compilation
            try:
                # 4 second timeout on compilation
                subprocess.check_output(" ".join(['javac', source_fname]), stderr=subprocess.STDOUT, shell=True, timeout=4, universal_newlines=True);
            except subprocess.CalledProcessError as e:
                error_str = str(e.output).replace(self.tempdir + os.sep, '').replace('\n', '<br />')
                raise CompilationError("javac failed with:\n" + error_str)
            self.compiled = True
        except Exception as e:
            self.clear()
            raise       # reraise

        return

    def clear(self):
        ''' Delete the executable and other files associated with this code.
        '''
        try:
            shutil.rmtree(self.tempdir)
        except OSError as e:
            pass
        self.compiled = False
        self.tempdir = None
        self.classname = None

    def _sanitize_user_program(self, user_code):
        ''' Return a list of strings consisting of the remaining user_code after
            removing unsafe libraries.

            TODO: This list is not complete, and it may be better implemented by restricting the jvm
            call when executing user code. This implementation is only good for proof-of-concept.
        '''

        blacklist = ['getRuntime',         # The only way to access the Runtime object
                     'java.lang.Runtime',  # The Runtime library as well as the RuntimePermission library
                     'java.lang.Security', # The security manager
                     'java.lang.System',   # Access to system information
                     'java.lang.Process',  # Process builders -- note that Threads are still allowed
                     'java.io.File',       # The library for file access -- including file deletion -- plus filestreams
                     'java.nio.File',      # A helper library for files
                     'java.net',           # The library for network access
                    ]
        for item in blacklist:
            if item in user_code:
                raise CompilationError("User code is not permitted to access '{0}'".format(item))

    def get_download_mimetype(self):
        ''' Return string with mimetype.
        '''
        return 'application/x-java'
