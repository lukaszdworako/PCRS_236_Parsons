import logging
import datetime
import json

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import localtime, utc
from django.contrib.postgres.fields import HStoreField

from pcrs.model_helpers import has_changed
from problems.models import AbstractProblem, AbstractSubmission, SubmissionPreprocessorMixin
from problems_python.python_language import PythonSpecifics
from multiselectfield import MultiSelectField



class Problem(AbstractProblem):
    name = models.CharField(max_length=50, default="")
    description = models.TextField(blank=True)
    starter_code = models.TextField(blank=True)
    invariant = models.TextField(blank=True)
    unit_tests = models.TextField(blank=True)
    visible_unit = models.BooleanField(default=False)
    evaluation_choices = ((0, 'Evaluate using all methods'), (1, 'Evaluate using line comparison (simple)'), (2, 'Evaluate using unit tests method'))
    evaluation_type = MultiSelectField(choices=evaluation_choices, max_choices=1, max_length=1, default=1)
    


class Submission(SubmissionPreprocessorMixin, AbstractSubmission):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    
    def build_code(self, code):
        assembled = ""
        code = json.loads(code)
        for line in code:
            print(line)
            if("<br>" in line["code"]):
                grouped = line.split("<br>")
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
                    solution_split[i].replace("    ", "\t")
                    if solution_split[i].count("\t") != student_split[i].count("\t"):
                        result = 4
                        incorrect_lines.append(i)
        return incorrect_lines, result


    # for now, this only supports simple line comparison. In the future will need to implement more advanced comparison
    def run_against_solution(self, student_code):
        stu_code = self.build_code(student_code)
        sol_code = self.build_sol_code(self.problem.starter_code)
        incorrect, result = self.line_comparison(stu_code, sol_code)
        return (result, incorrect)


    def set_score(self, student_code):
        ret = self.run_against_solution(student_code)
        if(ret[0] == 0):
            self.score = 1
        else:
            self.score = 0
        self.save()
        self.set_best_submission()
