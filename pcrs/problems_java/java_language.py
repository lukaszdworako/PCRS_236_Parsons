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
    jvm_res_path = PROJECT_ROOT + "/languages/java/execution/resources/"

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

    # TODO: change this to parse a JUnit dump
    # TODO: return an array of results
    # Start ignoring the expected output completely
    def run_test(self, test_name):
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
            flags = " ".join([
                "-Djava.security.manager=default",
                "-Djava.security.policy={0}pcrs.policy".format(self.jvm_res_path),
                self.createDependencyFlagString(),
                "org.junit.runner.JUnitCore", # run our test through JUnit
            ])
            proc = subprocess.Popen(
                    "java {0} Tests".format(flags),
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
                match = re.search('AssertionError(.*)', err)
                if match:
                    assertMessage = match.group(1)
                    if len(assertMessage) > 1:
                        # Prune off the ": "
                        assertMessage = assertMessage[2:]
                    else:
                        assertMessage = '(Hidden Assert Message)'

                    #ret['exception_type'] = 'warning'
                    #ret['runtime_error'] = "Test failed: " + assertMessage
                    ret['test_val'] = assertMessage
                else:
                    error_str = err.replace(self.tempdir + os.sep, '').replace('\n', '<br />')
                    ret['exception_type'] = 'error'
                    ret['runtime_error'] = "Runtime Error: " + error_str
                    ret['test_val'] = 'Runtime Error'
            else:
                ret["test_val"] = output.strip().replace('\n', '<br />')
                #ret["passed_test"] = exp_output.strip() == output.strip()
                ret["passed_test"] = True
        return ret

    def compile(self, user, user_code, test_code, deny_warning=False):
        ''' Compile the given user code, raising a compile error if unable.
        '''
        if self.compiled:
            return

        # From this point on, we need to delete the tempdir if there is a failure.
        try:
            self.tempdir = tempfile.mkdtemp(
                    prefix="{0}-{1}-".format(user, datetime.now().strftime('%m%d-%H:%M:%S'), dir=self.temp_path),
                    dir=self.temp_path)
            self._compileSource(user_code)
            self._compileSource(test_code, isTestCode=True)
            self.compiled = True
        except Exception as e:
            self.clear()
            raise # reraise

    def _compileSource(self, source_code, isTestCode=False):
        ''''Compiles given source code into the temporary run directory.

        Args:
            source_code: The raw source code to compile
            isTestCode:  If this is test code, it will be more
                         cautious with error message information.
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
            flags = self.createDependencyFlagString()
            proc = subprocess.Popen(
                    'javac {0} {1}'.format(flags, source_fname),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.tempdir,
                    shell=True,
                    universal_newlines=True)
            output, err = proc.communicate(timeout=8) # 8 second timeout on run
        except subprocess.CalledProcessError as e:
            raise CompilationError("javac failed with:\n" + str(e.output))
        except TimeoutExpired:
            try:
                proc.kill()
            except:
                pass # If it is already dead
            raise CompilationError('Compilation timeout expired. Please try again')

        if err:
            if isTestCode:
                err = self.stripTestCodeCompileError(err)
            raise CompilationError(err)

        return classname

    def createDependencyFlagString(self):
        dependencies = [ 'junit-4.12.jar', 'hamcrest-core-1.3.jar' ]
        classpath = ":".join([self.jvm_res_path + d for d in dependencies])
        # We need '.' in the classpath to load student class files
        return "-cp .:" + classpath

    def stripTestCodeCompileError(self, error):
        ''''Strips important compile errors from test code compile issues

        Args:
            error: The error message (from javac)
        Returns:
            A nicely stripped error message, not exposing the test case code.
        '''
        # TODO check if the 'user' object has some type of "admin" property
        # TODO check for:
        # s/\w\.java:\d+: error: cannot find symbol
        # Then strip out:
        # symbol: (.*)
        return error

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

