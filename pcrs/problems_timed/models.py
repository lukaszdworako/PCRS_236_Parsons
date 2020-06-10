from django.db import models
from django.utils import timezone

from pcrs.models import AbstractSelfAwareModel
from problems.models import AbstractProblem, AbstractSubmission
from users.models import PCRSUser, Section


class Problem(AbstractProblem):
    """
    A timed problem.
    """
    
    name = models.CharField(max_length=150)
    problem_description = models.TextField(blank=True)
    submission_description = models.TextField(blank=True)
    delay = models.PositiveIntegerField(default=5)
    attempts = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name

    def prepareJSON(self):
        """
        Returns serializatin of problem and its pages set in JSON format.
        """
        content = [self]+[p for p in self.page_set.all()]
        return content

class Page(AbstractSelfAwareModel):
    """
    A timed problem page.
    """
    class Meta:
        ordering = ['id']
    
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    term_list = models.TextField(blank=True)
    
    def __str__(self):
        return self.term_list
    
    def get_absolute_url(self):
        return '{problem}/page/{pk}'.format(
            problem=self.problem.get_absolute_url(), pk=self.pk)
    
    def clean_text(self):
        self.text = self.text.replace('"', "'")
    
    def save(self, *args, **kwargs):
        self.clean_text()
        super(Page, self).save(*args, **kwargs)

class Submission(AbstractSubmission):
    """
    A timed problem submission.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    attempt = models.PositiveIntegerField(null=True)
    
    timestamp_complete = models.DateTimeField(null=True)
    score_max = models.SmallIntegerField(null=True)
    percent = models.DecimalField(max_digits=5, decimal_places=4, null=True)
    
    # allowing use of null=True as it indicates that the submission was not completed
    terms_list_problem = models.TextField(null=True)
    terms_list_student = models.TextField(null=True)
    terms_match = models.TextField(null=True)
    terms_miss = models.TextField(null=True)
    
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
        self.timestamp_complete = timezone.now()
        
        count, total, index = 0, 0, 0
        problem_list, match_list, miss_list = [], [], []
        student_list = submission_text.splitlines()
        
        for term in student_list:
            student_list[index] = term.strip().lower()
            index += 1
        
        for page in self.problem.page_set.all() :
            if page.term_list:
                problem_list += page.term_list.split(",")
        for term in problem_list:
            problem_list[total] = term.strip().lower()
            total += 1
        
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
        
        self.percent = 0
        if total != 0:
            self.percent = count/total
        
        self.save()
        self.set_best_submission()
