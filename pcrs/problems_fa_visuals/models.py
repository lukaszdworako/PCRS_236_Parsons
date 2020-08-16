import logging
import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import localtime, utc
from django.contrib.postgres.fields import HStoreField

from pcrs.model_helpers import has_changed
from problems.models import AbstractProblem, AbstractSubmission
from problems_python.python_language import PythonSpecifics

# import pads as fa
# from pads import DFA, _DFAfromNFA
import problems_fa_visuals.automata as fa
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

    def save_dfa(self, obj):
        self.dfa = fa._DFAfromNFA(fa.RegExp(regex))


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
        self.submission = submission
        result = 0

        # visual to dfa conversion
        stu_dfa = fa.DFA()
        lines = submission.split('\n')
        lines = [line.replace('\r', '') for line in lines] 
        lines = [line.replace(' ', '') for line in lines]           
        stu_dfa.alphabet = set(lines[0].split(','))
        stu_dfa.initial = int(lines[1])
        stu_dfa.final = [int(lines[2].split(",")[i]) for i in range (len(lines[2].split(",")))]
        stu_dfa.transitions = {}
        for i in range(3, len(lines)):
            line = lines[i].split(',')
            stu_dfa.transitions[(int(line[0]), line[1])] = int(line[2])
        # raise NameError(stu_dfa.transitions)

        self.problem.dfa = fa._MinimumDFA(fa._DFAfromNFA(fa.RegExp(self.problem.regex)))
        # raise NameError(self.problem.dfa.transitions)
        
        self.score = int(self.problem.dfa == fa._MinimumDFA(stu_dfa))
        # debug line, will remove
        # self.score = 1
        self.save()
        self.set_best_submission()