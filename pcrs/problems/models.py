from django.db import models
from django.db.models import Max

from django.utils import timezone
from pcrs.models import AbstractNamedObject

from users.models import PCRSUser, Section, AbstractLimitedVisibilityObject


class ProblemTag(models.Model):
    """
    Tags for problems.
    """
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class AbstractProblem(AbstractLimitedVisibilityObject):
    """
    Base class for problems.

    A problem has a description, and optionally tags and solution and
    may no be visible to students.
    """
    type_name = None  # the name of the problem type to use in urls

    description = models.TextField()
    solution = models.TextField(blank=True)
    tags = models.ManyToManyField(ProblemTag, null=True, blank=True,
                                  related_name='%(app_label)s_%(class)s_related')

    class Meta:
        abstract = True

    def __str__(self):
        description = self.description[:150]
        if len(self.description) > 150:
            description += '...'
        return description

    def clear_submissions(self):
        """
        Delete all submissions to this problem.
        """
        self.submission_set.all().delete()

    @classmethod
    def get_base_url(cls):
        """
        Return the url prefix for the problem type.
        """
        return '/problems/{}'.format(cls.type_name)

    def get_absolute_url(self):
        return '{base}/{pk}'.format(base=self.get_base_url(), pk=self.pk)

    def best_per_student_before_time(self, deadline=timezone.now()):
        """
        Return a list of dictionaries of the form {student_id: , score:)
        representing the best submissions for every student who submitted a
        solution to this problem BEFORE deadline.

        Used for generating CSV reports and problem analysis.
        """
        return self.submission_set.filter(problem=self, timestamp__lt=deadline)\
            .values('student_id').annotate(score=Max('score'))


class AbstractNamedProblem(AbstractNamedObject, AbstractProblem):
    """
    A problem extended to have a required name.
    """
    class Meta:
        abstract = True


class AbstractSubmission(models.Model):
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

    def __str__(self):
        return '{problem} by {student} on {time}'.format(
            problem=self.problem, student=self.student.username,
            time=self.timestamp)


class AbstractTestCase(models.Model):
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

    @classmethod
    def get_problem_class(cls):
        raise NotImplementedError('Must be implemented by subclasses.')


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