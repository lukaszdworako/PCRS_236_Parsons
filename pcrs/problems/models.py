from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Max, Q
from django.utils import timezone
from content.models import AbstractTaggedObject

from pcrs.models import (AbstractNamedObject, AbstractGenericObjectForeignKey,
                         AbstractSelfAwareModel)
from users.models import PCRSUser, Section, AbstractLimitedVisibilityObject


def get_problem_labels():
    """
    Return the list app_labels of apps that contain a Problem class.
    """
    return [c.app_label for c in ContentType.objects.filter(Q(model='problem'))]


class AbstractProblem(AbstractSelfAwareModel, AbstractLimitedVisibilityObject,
                      AbstractTaggedObject):
    """
    A base class for all problems.

    All problems have visibility level, and optionally tags, and are self-aware.
    """
    class Meta:
        abstract = True

    def __str__(self):
        description = self.description[:150]
        if len(self.description) > 150:
            description += '...'
        return description

    @classmethod
    def get_problem_type_name(cls):
        return cls.get_app_label().replace('problems_', '')

    @classmethod
    def get_base_url(cls):
        """
        Return the url prefix for the problem type.
        """
        return '/problems/{}'.format(cls.get_problem_type_name())

    def get_absolute_url(self):
        return '{base}/{pk}'.format(base=self.get_base_url(), pk=self.pk)

    def best_per_student_before_time(self, deadline=timezone.now()):
        """
        Return a list of dictionaries of the form {student_id: , score:)
        representing the best submissions for every student who submitted a
        solution to this problem BEFORE deadline.

        Used for generating CSV reports and problem analysis.
        """
        return self.submission_set.filter(timestamp__lt=deadline)\
            .values('student_id').annotate(score=Max('score')).order_by()

    def clear_submissions(self):
        """
        Delete all submissions to this problem.
        """
        self.submission_set.all().delete()


class AbstractProgrammingProblem(AbstractProblem):
    """
    Base class for programming problems.

    Programming problems may have starter starter code and solution.
    """

    starter_code = models.TextField(blank=True)
    solution = models.TextField(blank=True)

    class Meta:
        abstract = True

    @property
    def max_score(self):
        return self.testcase_set.count()


class AbstractNamedProblem(AbstractNamedObject, AbstractProgrammingProblem):
    """
    A problem extended to have a required name and description.
    """
    class Meta:
        abstract = True


class CompletedProblem(AbstractGenericObjectForeignKey):
    #TODO: add docstring
    objects = models.Q(model='problem')
    user = models.ForeignKey(PCRSUser)

    @classmethod
    def get_completed(cls, user):
        return {problem.content_object
                for problem in cls.objects.filter(user=user)}


class AbstractSubmission(AbstractSelfAwareModel):
    """
    Base submission class.

    Submission is associated with a student and a problem, and optionally
    a section, and has a score, usually out of the total number of testcases
    that the associated problem has.
    """
    student = models.ForeignKey(PCRSUser, to_field='username',
                                on_delete=models.CASCADE,
                                related_name='%(app_label)s_%(class)s_related')
    section = models.ForeignKey(Section, blank=True,  null=True,
                                on_delete=models.SET_NULL,
                                related_name='%(app_label)s_%(class)s_related')
    timestamp = models.DateTimeField(default=timezone.now)
    submission = models.TextField(blank=True, null=True)
    score = models.SmallIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ['-timestamp']

    def __str__(self):
        return '{problem} by {student} on {time}'.format(
            problem=self.problem, student=self.student.username,
            time=self.timestamp)

    def set_score(self):
        """
        Set the score of this submission to the number of testcases that
        the submission passed.
        Create a record of the student completing the problem if the score on
        the submission is the highest score possible on the problem.
        """
        self.score = self.testrun_set.filter(test_passed=True).count()
        self.save(update_fields=['score'])

        #
        problem_type = ContentType.objects.get_for_model(self.problem)

        if self.score == self.problem.max_score:
            if not CompletedProblem.objects.filter(content_type=problem_type.id,
                                                   object_id=self.problem.pk):
                CompletedProblem(content_object=self.problem,
                                 user=self.student).save()


class AbstractTestCase(AbstractSelfAwareModel):
    """
    Base testcase class.

    TestCase is associated with a single problem.
    Each problem type should implement its own TestCase according to the
    problem semantics, as well as define what it means for a testcase to pass.
    """

    class Meta:
        abstract = True

    def __str__(self):
        return '{problem}: testcase {pk}'.format(
            pk=self.pk, problem=self.problem)

    def get_absolute_url(self):
        return '{problem}/testcase/{pk}'.format(
            problem=self.problem.get_absolute_url(), pk=self.pk)


class AbstractTestRun(models.Model):
    """
    Base testrun class.

    A testrun is associated with a single submission, and a single TestCase,
    and records whether that testcase for that submission has passed.
    """
    test_passed = models.BooleanField()

    class Meta:
        abstract = True

    def __str__(self):
        return '{submission}: testcase {pk}'.format(
            submission=self.submission, pk=self.testcase.pk)


# Signal handlers

def testcase_delete(sender, instance, **kwargs):
    """
    Updates the submission scores to a problem when its testcase is deleted.
    """
    try:
        problem = instance.problem
        submissions_affected = problem.submission_set.all()
        for submission in submissions_affected:
            submission.set_score()
    except sender.get_problem_class().DoesNotExist:
        # problem no longer exists, submissions will be deleted automatically
        # so no need to update scores
        pass