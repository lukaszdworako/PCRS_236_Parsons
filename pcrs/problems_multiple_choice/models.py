from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from content.models import contentsequenceitem_delete

from pcrs.model_helpers import has_changed
from pcrs.models import AbstractSelfAwareModel
from problems.models import AbstractProblem, AbstractSubmission, problem_delete


class Problem(AbstractProblem):
    """
    A multiple choice problem.
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()

    class Meta:
        unique_together = ['name', 'description']

    def get_testitem_data_for_submissions(self, s_ids):
        """
        Return a list of tuples summarizing for each option how many times it
        was correctly or incorrectly in submissions with pk in s_ids.
        """
        data = OptionSelection.objects.filter(submission_id__in=s_ids)\
            .values('option_id', 'is_correct')\
            .annotate(count=Count('is_correct'))
        results = {}
        # data is a list of dictionaries
        # {test_case_id: '',  test_passed: ', count: ''}
        # every dictionary encodes how many times a testcase passed or failed
        for dict in data:
            opt_id = dict['option_id']
            count = dict['count']
            res = results.get(opt_id, [0, 0])
            if dict['is_correct'] is True:
                res[0] = count
            if dict['is_correct'] is False:
                res[1] = count
            results[opt_id] = res
        return results


class Submission(AbstractSubmission):
    """
    A multiple choice problem submission.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    def set_score(self):
        """
        Set the score of this submission to the number of option that
        were correctly selected and correctly not select.
        """
        self.score = self.optionselection_set.filter(is_correct=True).count()
        self.save()
        self.set_best_submission()


class Option(AbstractSelfAwareModel):
    """
    A multiple choice problem answer option.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ['pk']

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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.pk:
            self.problem.max_score += 1
            self.problem.save()
        super().save(force_insert, force_update, using, update_fields)


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
        problem.max_score -= 1
        problem.save()

        submissions_affected = problem.submission_set.all()
        for submission in submissions_affected:
            submission.score = submission.optionselection_set.\
                filter(is_correct=True).count()
            submission.save()
    except Problem.DoesNotExist:
        # problem no longer exists, submissions will be deleted automatically
        pass


post_delete.connect(problem_delete, sender=Problem)