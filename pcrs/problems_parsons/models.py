import logging
import datetime
import json

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import localtime, utc
from django.contrib.postgres.fields import HStoreField
from django.utils.translation import gettext as _

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
    


class Submission(SubmissionPreprocessorMixin, AbstractSubmission):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    
    def run_python_testcases(self, student_code, save=True):
        """
        Run all testcases for the submission and create testrun objects.
        Return the list of testrun results.
        """
        results = []
        error = None

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

        return results, error

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
        sol_code.replace("<br>", "\n")
        sol_list = sol_code.split("\n")
        new_sol = ""
        for line in sol_list:
            if("#distractor" not in line):
                new_sol += line
                new_sol += "\n"
        return new_sol
            
    def run_testcases(self, student_code):
        results = None
        error   = None
        try:
            results = self.run_against_solution(student_code)

        except Exception:
            error = "Submission could not be run"
            return results, error

    # result 0 -> correct answer
    # result 1 -> too many lines
    # result 2 -> too few lines
    # result 3 -> line mismatch
    # result 4 -> indent mismatch
    # this entire thing is just a mess not gonna lie...
    def line_comparison(self, student_code, solution_code):
        result = 0
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


    # for now, this only supports simple line comparison. In the future will need to implement more advanced comparison
    def run_against_solution(self, student_code):
        stu_code = self.build_code(student_code)
        incorrect, result = [], 0
        print(self.problem.evaluation_type[0])
        if self.problem.evaluation_type[0] == "0" or self.problem.evaluation_type[0] == "1":
            sol_code = self.build_sol_code(self.problem.starter_code)
            incorrect, result = self.line_comparison(stu_code, sol_code)
        
        if self.problem.evaluation_type[0] == "0" or self.problem.evaluation_type[0] == "2":
            # do nothing for now
            pass
        return (result, incorrect, stu_code)


    def set_score(self, student_code):
        ret = self.run_against_solution(student_code)
        if(ret[0] == 0):
            self.score = 1
        else:
            self.score = 0
        self.incorrect_lines = ret[1]
        self.submission = ret[2]
        self.save()
        self.set_best_submission()

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
        runner = GenericLanguage(self.problem.language)
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