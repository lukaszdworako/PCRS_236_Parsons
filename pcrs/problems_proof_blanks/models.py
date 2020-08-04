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
from pcrs.models import AbstractSelfAwareModel
from problems.models import AbstractProblem, AbstractSubmission
from problems_python.python_language import PythonSpecifics

# TODO -- add to required imports
from sympy import simplify
from sympy.parsing.sympy_parser import parse_expr
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
    answer_keys = HStoreField(default=None, null=True, blank=True)

    class Meta:
        app_label = 'problems_proof_blanks'

    def save(self, *args, **kwargs):
        self.max_score = len(self.answer_keys)
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        return self.name
    
    def prepareJSON(self):
        """
        Returns serializatin of short answer problem in JSON format.
        """
        content = [self]
        return content

class Feedback(AbstractSelfAwareModel):
    """
    A coding problem testcase.

    A testcase has an input and expected output and an optional description.
    The test input and expected output may or may not be visible to students.
    This is controlled by is_visible flag.
    """
    problem = models.OneToOneField(Problem, on_delete=models.CASCADE,
                                null=False, blank=False, primary_key=True)
    feedback_keys = HStoreField(default=None, null=True, blank=True) # {"1": "{"type": "mathexpr", "x > 3": "too big"...}"}
    hint_keys = HStoreField(default=None, null=True, blank=True) # {"1": "think of ...."}

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return "Feedback: {}\n Hints: {}\n".format(self.feedback_keys, self.hint_keys)

    def get_absolute_url(self):
        return '{problem}/feedback/{pk}'.format(
            problem=self.problem.get_absolute_url(), pk=self.pk)



class Submission(AbstractSubmission):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    class Meta:
        app_label = 'problems_proof_blanks'
    # submission needs to be a dictionary / HStoreField object
    def set_score(self, submission):
        var_map = {} # maps instructor variables to student variables
        print(submission)
        self.submission = submission
        result = 0
        correct = []
        messages = {}
        self.incomplete_proof = self.problem.incomplete_proof
        for key in self.problem.answer_keys.keys():
            # submitted answer for question
            sub_ans = self.submission.get(key, None)

            # instructor answer for question
            inst_ans = self.problem.answer_keys[key]
            print(sub_ans)
            print("Feedback ")
            if hasattr(self.problem, "feedback"):
                # replace single quotes with double quotes else JSON errors 
                self.problem.feedback.feedback_keys[key] = self.problem.feedback.feedback_keys[key].replace("'", '"')
                print(self.problem.feedback.feedback_keys[key])
                feedback = json.loads(self.problem.feedback.feedback_keys[key])
            else:
                feedback = {}

            if feedback.get("type", None) == "mathexpr":
                new_var = ""
                # map new variables in instructor answer
                if feedback.get("autocheck", False) == "True":
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
                        messages[key] = self._check_feedback(sub_ans, inst_ans, feedback)
                except:
                    messages[key] = self._check_feedback(sub_ans, inst_ans, feedback)
            else:
                messages[key] = self._check_feedback(sub_ans, inst_ans, feedback)
            
            if messages[key] == "correct":
                result += 1
                self.incomplete_proof = self.incomplete_proof.replace("{{{}}}".format(key), "<strong> {} </strong>".format(sub_ans))
                correct.append(key)
                print(key)
                print("{{{}}}".format(key))
                print(self.incomplete_proof)

        self.messages = messages
        self.score = result
        print("###Score: {} ####".format(self.score))

        self.save()
        self.set_best_submission()
        return {"message": self.messages, "score": self.score}, None
    
    def _check_feedback(self, sub_ans, inst_ans, feedback):
        print("##IN HERE##")
        print(type(feedback))
        
        for (condition, _) in feedback.items():
            try:
                blanks = None # SET TO COPY OF SUBMISSION BLANKS
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
