from django.db import models
from problems.models import AbstractProblem, AbstractSubmission


class Problem(AbstractProblem):
    
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
class Submission(AbstractSubmission):
    
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    
    def set_score(self, answer):
        self.submission = answer
        self.score = 1
        self.save()

    def set_best_submission(self):
        pass
