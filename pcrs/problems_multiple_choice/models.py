from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from pcrs.model_helpers import has_changed
from pcrs.models import AbstractSelfAwareModel
from problems.models import AbstractSubmission, ProblemTag, AbstractProblem


class Problem(AbstractProblem):
    """
    A multiple choice problem.
    """

    description = models.TextField(unique=True)


class Submission(AbstractSubmission):
    """
    A multiple choice problem submission.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)


class Option(AbstractSelfAwareModel):
    """
    A multiple choice problem answer option.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer_text

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)
        clear = 'Submissions must be cleared before changing an option.'
        if self.problem.submission_set.all():
            if self.pk and has_changed(self, 'is_correct') or \
               not self.pk and self.is_correct:
                raise ValidationError({'is_correct': [clear]})

    def get_absolute_url(self):
        return '{problem}/option/{pk}'.format(
            problem=self.problem.get_absolute_url(), pk=self.pk)


class OptionSelection(models.Model):
    """
    A multiple choice problem option selection, created on each submission.
    """
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    was_selected = models.BooleanField()
    is_correct = models.BooleanField()


# Signal handlers

@receiver(post_delete, sender=Option)
def option_delete(sender, instance, **kwargs):
    """
    Updates the submission scores to a problem when its option is deleted.
    """
    try:
        problem = instance.problem
        submissions_affected = problem.submission_set.all()
        for submission in submissions_affected:
            submission.score = submission.optionselection_set.\
                filter(is_correct=True).count()
            submission.save()
    except Problem.DoesNotExist:
        # problem no longer exists, submissions will be deleted automatically
        pass