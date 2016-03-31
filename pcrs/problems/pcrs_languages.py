import os
import subprocess
import sys


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
        self.extensions = {'python': '.py',
                           'java': '.java'
                          }

        if language == 'python':
            from problems_python.python_language import PythonSpecifics
            self.lang = PythonSpecifics()

        # C was not built using the GenericLanguage pattern ...
        #elif language == 'c':
        #    pass

        elif language == 'java':
            from problems_java.java_language import JavaSpecifics
            self.lang = JavaSpecifics()

        else:    # No known language
            raise ValueError("Language unknown")


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
