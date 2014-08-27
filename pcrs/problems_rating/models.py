from django.db import models
from django.utils import timezone
from problems.models import AbstractProblem, AbstractSubmission


SCALE_TYPES = (
    ('LIK', 'Likert'),
    ('SLI', 'slider'),
    ('STA', 'star')
)

class Problem(AbstractProblem):
    
    name = models.CharField(max_length=150)
    description = models.TextField()
    scale_type = models.CharField(choices=SCALE_TYPES, max_length=3)
    options = models.TextField(blank=True, null=True)
    minimum = models.IntegerField(blank=True, null=True)
    maximum = models.IntegerField(blank=True, null=True)
    increment = models.FloatField(blank=True, null=True)
    extra = models.NullBooleanField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    def get_options(self):
        opts = []
        for opt in self.options.splitlines():
            opts.append(opt.strip())
        return opts

class Submission(AbstractSubmission):
    
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    
    def set_score(self, rating):
        self.timestamp = timezone.now()
        self.has_best_score = True
        self.submission = rating
        self.score = 1
        self.save()

    def set_best_submission(self):
        pass
