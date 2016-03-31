import os
import subprocess
import sys

import problems.pcrs_languages as languages


class JavaSpecifics(languages.BaseLanguage):
    ''' Representation of Java language:
        * string encoding in visualizer format,
        * generation of execution trace for visualizer,
        * running tests

        TODO: no visualizer support currently provided
              see http://www.pythontutor.com/java.html#mode=edit
              for a tool that could be used to provide support
        TODO: execution not yet supported
    '''

    def encode_str(self, target_value):
        ''' Encode string target_value in visualizer format.
        '''
        raise NotImplementedError("Visualization not yet supported")

    def get_exec_trace(self, user_script, add_params):
        ''' Get execution trace of string user_script providing additional parameters.
        '''
        raise NotImplementedError("Visualization not yet supported")

    def run_test(self, user_program, test_input, exp_output):
        ''' Return dictionary ret containing results of a testrun.
            ret has the following mapping:
            'test_val' -> encoded for visualizer format test output.
            'passed_test' -> boolean
            'exception' (only if exception occurs) -> exception message.
        '''
        raise NotImplementedError("Java execution not yet built")

    def run_subprocess(self, program):
        ''' Run provided program as a subprocess. Return the process.
        '''
        raise NotImplementedError("Java execution not yet built")

    def sanitize_user_program(self, user_code):
        ''' Return a list of strings consisting of the remaining user_code after
            removing unsafe libraries.
        '''
        raise NotImplementedError("Java execution not yet built")

    def get_download_mimetype(self):
        ''' Return string with mimetype.
        '''

        return 'application/x-java'
