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
            testClassName = self.compileSource(test_input)
            # TODO enable the policy manager to block network and filesystem access
            command = ["java -enableassertions -Djava.security.manager=default {0}".format(testClassName)]

            proc = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.tempdir,
                    shell=True,
                    universal_newlines=True)
            output, err = proc.communicate(timeout=8) # 8 second timeout on run
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
                ret["test_val"] = output.strip().replace('\n', '<br />')
                ret["passed_test"] = exp_output.strip() == output.strip()
        return ret

    def compile(self, user, user_code, deny_warning=False):
        ''' Compile the given user code, raising a compile error if unable.
        '''
        if self.compiled:
            return

        # From this point on, we need to delete the tempdir if there is a failure.
        try:
            self.tempdir = tempfile.mkdtemp(
                    prefix="{0}-{1}-".format(user, datetime.now().strftime('%m%d-%H:%M:%S'), dir=self.temp_path),
                    dir=self.temp_path)
            self.compileSource(user_code)
            self.compiled = True
        except Exception as e:
            self.clear()
            raise # reraise

    def compileSource(self, source_code):
        ''''Compiles given source code into the temporary run directory.

        Args:
            source_code: The raw source code to compile
        Returns:
            The name of the main public class of the source code
        Raises:
            CompilationError: On failure
        '''
        try:
            # Since javac should compile from PUBLICCLASS.java
            classname = re.search('public\s+class\s+(\w+)', source_code).group(1)
        except AttributeError:
            raise CompilationError("'public class NAME' not found during compilation")

        # Sanitize classname
        if '..' in classname:
            raise CompilationError("'{0}' is not a valid class name".format(classname))

        source_fname = classname + '.java'
        source_path = "{0}{1}{2}".format(self.tempdir, os.sep, source_fname)
        with open(source_path, "w") as f:
            f.write(source_code)

        # Actual compilation
        try:
            proc = subprocess.Popen(
                    'javac {0}'.format(source_fname),
                    stdout=None,
                    stderr=None,
                    cwd=self.tempdir,
                    shell=True,
                    universal_newlines=True)
            output, err = proc.communicate(timeout=8) # 8 second timeout on run
        except subprocess.CalledProcessError as e:
            error_str = str(e.output).replace(self.tempdir + os.sep, '').replace('\n', '<br />')
            raise CompilationError("javac failed with:\n" + error_str)

        return classname

    def clear(self):
        ''' Delete the executable and other files associated with this code.
        '''
        try:
            shutil.rmtree(self.tempdir)
        except OSError as e:
            pass
        self.compiled = False
        self.tempdir = None

    def get_download_mimetype(self):
        ''' Return string with mimetype.
        '''
        return 'application/x-java'

