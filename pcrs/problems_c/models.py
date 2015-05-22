import logging
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete
from django.core.exceptions import ObjectDoesNotExist

from .c_language import CSpecifics
from pcrs.model_helpers import has_changed
from problems.models import (AbstractProgrammingProblem, AbstractSubmission,
                             AbstractJobScheduler,
                             AbstractTestCase, AbstractTestRun,
                             testcase_delete, problem_delete)

from rest_framework import status
from json import loads, dumps
from requests import post
from hashlib import sha1
from re import finditer, search
import re
import bisect

class Problem(AbstractProgrammingProblem):
    """
    A coding problem.

    A coding problem has all the properties of a problem, and
    a language and starter code
    """

    language = models.CharField(max_length=50,
                                choices=settings.LANGUAGE_CHOICES,
                                default='c')


class JobScheduler(AbstractJobScheduler):
    """
    JobScheduler configuration.

    Configuration information regarding the Job Scheduler system
    that enables remote compiling/interpreting
    """
    pass

class Submission(AbstractSubmission):
    """
    A coding problem submission.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    def run_testcases_locally(self):
        """
        Run all testcases for the submission locally and create testrun objects.
        Return the list of testrun results.
        """
        results = []

        runner = CSpecifics(self.user.username, self.mod_submission)
        for testcase in self.problem.testcase_set.all():
            run = runner.run_test(testcase.test_input, testcase.expected_output)
            # Modify compilation and warning messages suppressing hidden code
            if run["exception"] != " ":
                run["exception"] = self.treat_exception_text(run["exception"])
            TestRun.objects.create(submission=self, testcase=testcase,
                                   test_passed=run['passed_test'])
            run['test_input'], run['expected_output'] = None, None
            run['test_desc'] = testcase.description
            if testcase.is_visible:
                run['test_input'] = testcase.test_input
                run['expected_output'] = testcase.expected_output
            results.append(run)

        # Clear exec file created by GCC during compilation process
        if len(self.problem.testcase_set.all()) > 0:
            runner.clear_exec_file(runner.compilation_ret["temp_gcc_file"])

        # Condition for editor running code - no testcases, just result
        if self.problem.id == 9999999:
            run = runner.run_test("", "")
            if run["exception"] != " ":
                run["exception"] = self.treat_exception_text(run["exception"])
            run['test_input'], run['expected_output'] = None, None
            results.append(run)

        return results

    def run_testcases_online(self):
        """
        Run all testcases for the submission online and create testrun objects.
        Return the list of testrun results.
        """

        try:
            jobscheduler_conf = JobScheduler.objects.get(id=1)
        except ObjectDoesNotExist:
            return Submission.run_testcases_locally(self)

        # Generate URL to JobScheduler server
        if jobscheduler_conf.dns == "":
            host = jobscheduler_conf.protocol + "://" + jobscheduler_conf.ip
        else:
            host = jobscheduler_conf.protocol + "://" + jobscheduler_conf.dns
        if jobscheduler_conf.port != "":
            host += ":" + jobscheduler_conf.port
        host += "/" + jobscheduler_conf.api_url + "/"

        # Prepare JSON to be submitted
        headers = {'content-type': 'application/json'}
        code_problem = \
            {
                "username": str(self.user.username),
                "code": str(self.mod_submission),
                'language': str(self.problem.language),
                "tests": []
            }

        for testcase in self.problem.testcase_set.all():
            code_problem["tests"].append({
                "test_input": str(testcase.test_input),
                "exp_output": str(testcase.expected_output),
            })

        results = []

        # Try to submit request to JobScheduler server
        try:
            r = post(host, dumps(code_problem), auth=(jobscheduler_conf.user, jobscheduler_conf.password),
                     headers=headers)
            if r.status_code == status.HTTP_201_CREATED:
                code_return = loads(r.text)
                i = 0
                for testcase in self.problem.testcase_set.all():
                    run = {}
                    run['test_input'], run['expected_output'] = None, None
                    run['test_desc'] = testcase.description
                    if testcase.is_visible:
                        run['test_input'] = testcase.test_input
                        run['expected_output'] = testcase.expected_output
                    run['test_val'] = code_return['tests'][i]['real_output']
                    run['passed_test'] = code_return['tests'][i]['passed']
                    run['exception_type'] = code_return['exception_type']
                    run['exception'] = code_return['exception']
                    TestRun.objects.create(submission=self, testcase=testcase,
                                           test_passed=run['passed_test'])
                    i += 1
                    results.append(run)
            else:
                print("Code request not created! Probably no Client was found by the JobScheduler.")
                results = Submission.run_testcases_locally(self)
        except Exception as e:
            print("Connection Error: " + str(e))
            results = Submission.run_testcases_locally(self)

        return results

    def run_testcases(self, request):
        """
        Determines how the testcases should be executed
        Return the list of testrun results.
        """

        # Remove tags from the C programs
        self.pre_process_code_tags()

        # Check if remote compilation (JobScheduler) is activated
        if JobScheduler.objects.get(id=1).active:
            return Submission.run_testcases_online(self), None
        else:
            return Submission.run_testcases_locally(self), None

    def treat_exception_text(self, program_exception):

        exception = ""
        # No hidden code in the script, no need to process the exception message
        if not self.hidden_lines_list:
            return program_exception

        hidden_error = 0
        #First, get only the parts that match what I want to split by
        split_pattern = re.compile(r'(([0-9]+):[0-9]+:\s(?:warning:|error:))')
        tuple_of_delims = split_pattern.findall(program_exception)

        msg_delim = [str(cur_tuple[0]) for cur_tuple in tuple_of_delims]

        split_warning = re.split(r'[0-9]+:[0-9]+:\s(?:warning:|error:)', program_exception)

        first_item = split_warning.pop(0)
        msg_delim[0]=first_item + msg_delim[0]
        final_split = map("".join, zip(msg_delim, split_warning))

        #Split by either ": warning:" or ": error:"
        count=0
        for exception_line in final_split:
            if (int)(tuple_of_delims[count][1]) in self.hidden_lines_list:
                if hidden_error == 0:
                    hidden_error = 1
                    exception_line = "There's a problem in your code! Please check the exercise description."
                else:
                    exception_line = ""
            else:
                #Getting a list of all lines that are less than the current line number in the hidden list
                list_amt = bisect.bisect_left(self.hidden_lines_list, (int)(tuple_of_delims[count][1]))
                adjusted_line_no = (int)(tuple_of_delims[count][1]) - list_amt
                #Replacing the actual line number with the one that the user sees
                exception_line = exception_line.replace((str)(tuple_of_delims[count][1])+":", (str)(adjusted_line_no)+":")

            exception += exception_line
            count += 1

        return exception

    def pre_process_code_tags(self):
        # Get student code hashed key

        #if code from editor, just return straight code
        if self.problem_id == 9999999:
            if len(self.submission) == 0:
                raise Exception("No code found!")
            else:
                self.hidden_lines_list = []
                self.mod_submission = self.submission

        #Code not from editor, process tags
        else:
            student_code_key = sha1(str(self.problem_id).encode('utf-8')).hexdigest()
            student_code_key_list = [m.start() for m in finditer(student_code_key, self.submission)]
            student_code_key_len = len(student_code_key)
            student_code_key_list_len = len(student_code_key_list)

            # Could not find student code
            if len(student_code_key_list) == 0 or len(student_code_key_list) % 2 != 0:
                raise Exception("No student code found!")

            # Get student code from submission and add it to the official exercise (from the database)
            student_code_list = []
            while len(student_code_key_list) >= 2:
                student_code_list.append(
                    self.submission[student_code_key_list[0]+student_code_key_len+1: student_code_key_list[1]])
                del student_code_key_list[0], student_code_key_list[0]

            # Create variable mod_submission to handle the fusion of student code with starter_code from the database
            self.mod_submission = self.problem.starter_code
            last_tag_size = len('[/student_code]') + 1
            for student_code in student_code_list:
                self.mod_submission = self.mod_submission[: self.mod_submission.find('[student_code]')] + \
                                        '\r\n' + student_code + '' +\
                                        self.mod_submission[self.mod_submission.find('[/student_code]')+last_tag_size:]

            # Replace hashed key with text (Implementation start/end)
            x = 0
            while x < student_code_key_list_len:
                m = search(student_code_key, self.submission)
                self.submission = self.submission[: m.start()] + self.submission[m.end():]
                x += 1

            # Remove blocked tags from the source code
            self.mod_submission = self.mod_submission.replace("[blocked]\r\n", '').replace("[/blocked]\r\n", '')
            self.mod_submission = self.mod_submission.replace("[blocked]", '').replace("[/blocked]", '')

            # Store hidden code lines for previous use when showing compilation and warning errors
            inside_hidden_tag = False
            self.hidden_lines_list = []
            line_num = 1
            for line in self.mod_submission.split('\n'):
                if line.find("[hidden]") > -1:
                    inside_hidden_tag = True
                    continue
                elif line.find("[/hidden]") > -1:
                    inside_hidden_tag = False
                    continue
                if inside_hidden_tag:
                    self.hidden_lines_list.append(line_num)
                line_num += 1

            # Remove hidden tags from the source code
            self.mod_submission = self.mod_submission.replace("[hidden]\r\n", '').replace("[/hidden]\r\n", '')
            self.mod_submission = self.mod_submission.replace("[hidden]", '').replace("[/hidden]", '')

def raw_string(s):
    if isinstance(s, str):
        s = bytes(s, "utf-8").decode("unicode_escape")
    return s


class TestCase(AbstractTestCase):
    """
    A coding problem testcase.

    A testcase has an input and expected output and an optional description.
    The test input and expected output may or may not be visible to students.
    This is controlled by is_visible flag.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE,
                                null=False, blank=False)
    test_input = models.TextField()
    expected_output = models.TextField()

    def __str__(self):
        testcase = '{input} -> {output}'.format(input=self.test_input,
                                                output=self.expected_output)
        if self.description:
            return self.description + ' : ' + testcase
        else:
            return testcase

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)
        if self.pk:
            if has_changed(self, 'problem_id'):
                raise ValidationError({
                    'problem': ['Reassigning a problem is not allowed.']
                })
            if self.problem.submission_set.all():
                clear = 'Submissions must be cleared before editing a testcase.'
                if has_changed(self, 'test_input'):
                    raise ValidationError({'test_input': [clear]})
                if has_changed(self, 'expected_output'):
                    raise ValidationError({'expected_output': [clear]})


class TestRun(AbstractTestRun):
    """
    A coding problem testrun, created for each testcase on each submission.
    """
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE)

    def get_history(self):
        return {
            'visible': self.testcase.is_visible,
            'input': self.testcase.test_input,
            'output': self.testcase.expected_output,
            'passed': self.test_passed,
            'description': self.testcase.description
        }


# Signal handlers

# update submission scores when a testcase is deleted
post_delete.connect(testcase_delete, sender=TestCase)

post_delete.connect(problem_delete, sender=Problem)
