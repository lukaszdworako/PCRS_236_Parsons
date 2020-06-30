import logging
import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import localtime, utc
from django.contrib.postgres.fields import HStoreField

from pcrs.model_helpers import has_changed
from problems.models import AbstractProblem, AbstractSubmission
from problems_python.python_language import PythonSpecifics

# import pads
# from problems_fa_visuals import Automata

# class dfa (Automata.DFA):
#     transitions = {}
#     finals = []

#     def transition (state, symbol):
#         return transitions[(state, symbol)]
    
#     def is_final(state):
#         return state in finals

class Problem(AbstractProblem):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    regex = models.CharField(max_length=80)
    dfa = None

    # def save_dfa(obj):
    #     self.dfa = Automata._DFAfromNFA(Automata.RegExp(regex))


    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)
        clear = 'Submissions must be cleared before changing the solution. (Please copy the new solution to your clipboard, as it will be lost when you clear submissions.)'
        
    class Meta:
        app_label = 'problems_fa_visuals'

    def __str__(self):
        return self.name

    def prepareJSON(self):
        """
        Returns serialization of short answer problem in JSON format.
        """
        content = [self]
        return content

Problem._meta.get_field('max_score').default = 1
Problem._meta.get_field('max_score').blank = False


class Submission(AbstractSubmission):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    class Meta:
        app_label = 'problems_fa_visuals'

    
    def set_score(self, submission):
    #     self.submission = submission
    #     result = 0

    #     # visual to dfa conversion
    #     stu_dfa = dfa
    #     lines = self.submission.split('\n')
    #     stu_dfa.alphabet = lines[0].split(',')
    #     stu_dfa.initial = int(lines[1])
    #     stu_dfa.finals = [int(lines[2].split(",")[i]) for i in range (len(lines[2].split(",")))]
    #     for i in range(3, len(lines)):
    #         line = lines[i].split(',')
    #         stu_dfa.transitions[(int(line[0]), line[1])] = int(line[2])


    #     self.problem.dfa.asDFA(self.problem.regex)

        
    #     self.score = int(self.problem.dfa == stu_dfa)
        self.score = 1
        self.save()
        self.set_best_submission()