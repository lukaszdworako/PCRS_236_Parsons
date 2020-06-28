import logging
import datetime
import re
import json
from django.db import models

from problems.models import AbstractProblem, AbstractSubmission
from pcrs.model_helpers import has_changed

from django.core.exceptions import ValidationError
from django.db import connection, models
from django.db.models.signals import pre_migrate
from django.utils.timezone import localtime, utc
from django.contrib.postgres.fields import HStoreField
from django.dispatch import receiver

from pcrs.model_helpers import has_changed
from problems.models import AbstractProblem, AbstractSubmission
from problems_python.python_language import PythonSpecifics

# TODO -- add to required imports
from sympy import simplify
from sympy.abc import *

# Recipe from: 
# https://stackoverflow.com/questions/11577993/how-to-setup-django-hstore-with-an-existing-app-managed-by-south
@receiver(pre_migrate)
def setup_postgres_hstore(sender, **kwargs):
    """
    Always create PostgreSQL HSTORE extension if it doesn't already exist
    on the database before syncing the database.
    Requires PostgreSQL 9.1 or newer.
    """
    cursor = connection.cursor()
    cursor.execute("CREATE EXTENSION IF NOT EXISTS hstore")


# Create your models here.
class Problem(AbstractProblem):
    name = models.CharField(max_length=150)
    proof_statement = models.TextField(blank=True)
    incomplete_proof = models.TextField(blank=True)
    no_correct_response = models.BooleanField(default=False)
    answer_keys = HStoreField(default=None, blank=True)
    feedback_keys = HStoreField(default=None, blank=True) # {"1": "{"type": "mathexpr", "x > 3": "too big"...}"}
    hint_keys = HStoreField(default=None, blank=True) # {"1": "think of ...."}

    class Meta:
        app_label = 'problems_proof_blanks'


    def __str__(self):
        return self.name
    
    def prepareJSON(self):
        """
        Returns serializatin of short answer problem in JSON format.
        """
        content = [self]
        return content

class Submission(AbstractSubmission):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    class Meta:
        app_label = 'problems_proof_blanks'
    # submission needs to be a dictionary / HStoreField object
    def set_score(self, submission):
        var_map = {} # maps instructor variables to student variables
        print(submission)
        self.submission = json.load(submission)
        result = 0
        correct = []
        messages = {}
        for key in self.problem.answer_keys.keys():
            sub_ans = submission[key]
            inst_ans = self.problem.answer_keys[key]
            feedback = json.loads(self.problem.feedback_keys[key])

            if feedback["type"] == "mathexpr":
                new_var = ""
                # map new variables in instructor answer
                for char in inst_ans:
                    if char.isalpha() and char not in var_map: 
                        var_map[char] = None
                        new_var = char

                for char in sub_ans:
                    if char.isalpha() and char not in var_map.values() and new_var != "":
                        var_map[new_var] = char

                for var in var_map:
                    sub_ans = sub_ans.replace(var, var_map[var])

                try:
                    # check if both mathematical expressions are equal
                    if simplify(parse_expr(sub_ans) - parse_expr(inst_ans)) == 0:
                        messages[key] = "correct"
                        # to convert to latex -- sympy.latex()
                    else:
                        messages[key] = _check_feedback(sub_ans, inst_ans)
                except:
                    messages[key] = _check_feedback(sub_ans, inst_ans, feedback)
            else:
                messages[key] = _check_feedback(sub_ans, inst_ans, feedback)
            
            if messages[key] == "correct":
                result += 1
                correct.append(key)

        self.messages = messages
        self.score = result
        self.save()
        self.set_best_submission()
    
    def _check_feedback(sub_ans, inst_ans, feedback):
        
        for (condition, _) in feedback.items:
            try:
                func_verifier = r"lambda . : . (>|<|!|=)=? .+"
                condition_regex = re.compile(condition)
                if re.search(condition_regex, sub_ans):
                    return _

                elif re.search(func_verifier, condition) and eval(condition)(sub_ans):
                    return _
                # default
                else:
                    return "correct" if sub_ans == inst_ans else "incorrect"

            except:
                return "syntax error"