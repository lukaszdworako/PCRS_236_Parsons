from django.db import models

from pcrs.models import AbstractSelfAwareModel
from problems.models import AbstractProblem, AbstractSubmission


class Problem(AbstractProblem):
    """
    A timed problem.
    """
    
    description = models.TextField(unique=True)
    delay = models.PositiveIntegerField(default=10)

class Term(AbstractSelfAwareModel):
    """
    A timed problem term or phrase.
    """
    
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    text = models.CharField(max_length=50)
    
    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return '{problem}/term/{pk}'.format(
            problem=self.problem.get_absolute_url(), pk=self.pk)

class Submission(AbstractSubmission):
    """
    A timed problem submission.
    """
    
    score_max = models.SmallIntegerField(default=0)
    percent = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    
    terms_list_problem = models.TextField(blank=True)
    terms_list_student = models.TextField(blank=True)
    terms_match = models.TextField(blank=True)
    terms_miss = models.TextField(blank=True)

    
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    
    def set_best_submission(self):
        # from AbstractSubmission.set_best_submission()
        # modified to set best submission based on percent
        try:
            current_best = self.__class__.objects.get(
                user=self.user, problem=self.problem, has_best_score=True)
            if self.percent >= current_best.percent and self.pk != current_best.pk:
                current_best.has_best_score = False
                current_best.save()
                self.has_best_score = True
        except self.__class__.DoesNotExist:
            self.has_best_score = True
        finally:
            self.save()

    
    def set_score(self, submission_text):
        count = 0
        total = self.problem.term_set.count()
        problem_list = []
        student_list = submission_text.splitlines()
        match_list = []
        miss_list = []
        
        for term in self.problem.term_set.all() :
            problem_list.append(str(term))
        
        self.terms_list_problem = str(problem_list)
        self.terms_list_student = str(student_list)
        
        for term in problem_list:
            if term in student_list:
                match_list.append(term)
                count += 1
            else:
                miss_list.append(term)
        
        self.terms_match = str(match_list)
        self.terms_miss = str(miss_list)
        
        self.submission = submission_text
        self.score_max = total
        self.score = count

        if total != 0:
            self.percent = count/total
        
        self.save()
        self.set_best_submission()

