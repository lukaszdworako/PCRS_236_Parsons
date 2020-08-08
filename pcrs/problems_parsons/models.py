import logging
import datetime
import json

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import localtime, utc
from django.contrib.postgres.fields import HStoreField
from django.utils.translation import gettext as _
from django.db.models import Count

from problems.pcrs_languages import GenericLanguage
from pcrs.model_helpers import has_changed
from problems.models import AbstractProblem, AbstractSubmission, SubmissionPreprocessorMixin, AbstractTestCaseWithDescription, AbstractTestRun, testcase_delete, problem_delete
from problems_python.python_language import PythonSpecifics
from multiselectfield import MultiSelectField



class Problem(AbstractProblem):
    name = models.CharField(max_length=50, default="")
    description = models.TextField(blank=True)
    starter_code = models.TextField(blank=True)
    invariant = models.TextField(blank=True)
    evaluation_choices = ((0, _('Evaluate using all methods')), (1, _('Evaluate using line comparison (simple)')), (2, _('Evaluate using unit tests method')))
    evaluation_type = MultiSelectField(choices=evaluation_choices, max_choices=1, max_length=1)
    
    def get_testitem_data_for_submissions(self, s_ids):
        """
        Return a list of tuples summarizing for each testcase how many times it
        passed and failed in submissions with pk in s_ids.
        Each tuple has the form (testcase_id, times_passed, times_failed).
        """
        data = self.get_testrun_class().objects.filter(submission_id__in=s_ids)\
            .values('testcase_id', 'test_passed')\
            .annotate(count=Count('test_passed'))
        results = {}
        # data is a list of dictionaries
        # {test_case_id: '',  test_passed: ', count: ''}
        # every dictionary encodes how many times a testcase passed or failed
        for dict in data:
            opt_id = dict['testcase_id']
            count = dict['count']
            res = results.get(opt_id, [0, 0])
            if dict['test_passed'] is True:
                res[0] = count
            if dict['test_passed'] is False:
                res[1] = count
            results[opt_id] = res
        return results


class Submission(SubmissionPreprocessorMixin, AbstractSubmission):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    incorrect_lines = models.TextField(blank=True)
    reason_incorrect = models.IntegerField(default=-1)
    
    def run_python_testcases(self, student_code, save=True):
        """
        Run all testcases for the submission and create testrun objects.
        Return the list of testrun results.
        """
        results = []
        error = None
        passed = False
        for testcase in self.problem.testcase_set.all():
            run = testcase.run(student_code)
            try:
                passed = run['passed_test']
            except KeyError:
                passed = False
                if 'exception' in run:
                    error = run['exception']
                else:
                    error = "The testcase could not be run"
            if save:
                TestRun.objects.create(submission=self, testcase=testcase,
                                       test_passed=passed)

            run['test_desc'] = testcase.description
            run['debug'] = False
            if testcase.is_visible:
                run['test_input'] = testcase.test_input.replace('\n','<br />')
                run['debug'] = True
            else:
                run['test_input'] = None
            results.append(run)

        return results, error, passed

    def build_code(self, code):
        assembled = ""
        code = json.loads(code)
        for line in code:
            if("<br>" in line["code"]):
                grouped = line["code"].split("<br>")
                for temp_line in grouped:
                    assembled += line["indent"]*"\t"
                    assembled += temp_line
                    assembled += "\n"
            else:
                assembled += line["indent"]*"\t"
                assembled += line["code"]
                assembled += "\n"
        return assembled

    def build_sol_code(self, sol_code):
        sol_list, assembled = [], ""
        # need to split to determine which lines have indentation issues due to <br>
        split = sol_code.split("\n")
        for i in range(len(split)):
            # normalize to tabs, cause we aren't monsters but some people are...
            split[i] = split[i].replace("    ", "\t")
            # need to know since perhaps multiple lines were on this line
            num_br = split[i].count("<br>")
            if num_br:
                # if the given split line contained it, then we need to prepend tabs
                line_split = split[i].split("<br>")
                num_tabs = line_split[0].count("\t")
                sol_list.append(line_split[0])
                # can ignore first index since it's tabbing is what we're basing it off of
                for i in range(1, len(line_split)):
                    sol_list.append("\t"*num_tabs+line_split[i])
            else:
                # if there isn't a <br> then we're OK to just add it
                sol_list.append(split[i])

        for line in sol_list:
            # the solution cannot contain any distractor lines!
            if("#distractor" not in line):
                assembled += line
                assembled += "\n"
        return assembled

    # result 0 -> correct answer
    # result 1 -> too many lines
    # result 2 -> too few lines
    # result 3 -> line mismatch
    # result 4 -> indent mismatch
    # this entire thing is just a mess not gonna lie...
    def line_comparison(self, student_code, solution_code):
        result = 0
        student_code = student_code.replace("<br>", "\n")
        solution_code = solution_code.replace("<br>", "\n")
        student_split = student_code.split("\n")
        solution_split = solution_code.split("\n")
        incorrect_lines = []
        # in the simple line comparison case, if we don't have exact number of lines matched, it is auto wrong
        if (len(student_split) != len(solution_split)):
            # in either of these cases all lines are considered to be incorrect for simplicity sake
            if (len(student_split) > len(solution_split)):
                result = 1
            else:
                result = 2
        else:
            # at this point, student has correct number of lines, but we need to verify correct organization first
            for i in range(len(student_split)):
                # strip the special characters from both sides of both strings
                if student_split[i].strip(' \t\n\r') != solution_split[i].strip(' \t\n\r'):
                    incorrect_lines.append(i)
            if incorrect_lines:
                result = 3
            else:
                # so the lines are in the correct order, but are they the right indentation?
                for i in range(len(student_split)):
                    # need to normalize indentation from space to tab still... yucky ucky
                    # this probably isn't the best way but honestly who knows at this point
                    solution_split[i] = solution_split[i].replace("    ", "\t")
                    if solution_split[i].count("\t") != student_split[i].count("\t"):
                        result = 4
                        incorrect_lines.append(i)
        return incorrect_lines, result

    def set_score(self, student_code):
        if student_code != None:
            stu_code = self.build_code(student_code)
        else:
            stu_code = ""
        incorrect_lines, result_lines = [], -1
        over_pass = False
        ret_json = {}

        # if we want to run all test cases or if we want line comparison specifically
        if self.problem.evaluation_type[0] == "0" or self.problem.evaluation_type[0] == "1":
            sol_code = self.build_sol_code(self.problem.starter_code)
            incorrect_lines, result_lines = self.line_comparison(stu_code, sol_code)
            ret_json["result_lines"] = result_lines
            # you can optionally choose to return to student the incorrect lines, however not currently supported
            #ret_json["incorrect_lines"] = incorrect_lines
            self.reason_incorrect = result_lines
            if result_lines == 0:
                self.score = 1
            else:
                self.score = 0

        # if we want to run testcases, we can optimize to not run if it's already an exact match
        # or, if it is not, run testcases to make sure, or if just want testcase
        if (self.problem.evaluation_type[0] == "0" and result_lines != 0) or self.problem.evaluation_type[0] == "2":
            results_test, error_test, over_pass = self.run_python_testcases(stu_code)
            ret_json["result_test"] = results_test
            ret_json["error_test"]  = error_test
            if over_pass == True:
                self.score = 1
            else:
                self.reason_incorrect = 5
                self.score = 0

        self.incorrect_lines    = incorrect_lines
        self.submission         = stu_code
        self.save()
        self.set_best_submission()
        return ret_json

class TestCase(AbstractTestCaseWithDescription):
    """
    A coding problem testcase.

    A testcase has an input and expected output and an optional description.
    The test input and expected output may or may not be visible to students.
    This is controlled by is_visible flag.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE,
                                null=False, blank=False)
    pre_code = models.TextField(default="", blank=True)
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

    def run(self, code):
        runner = GenericLanguage('python')
        return runner.run_test(code, self.test_input, self.expected_output, self.pre_code)


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