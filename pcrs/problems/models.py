import re
from hashlib import sha1

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models, IntegrityError
from django.db.models import Max, Q, Count, F
from django.utils import timezone
from django.conf import settings

import content.models
from content.tags import AbstractTaggedObject
from pcrs.models import (AbstractNamedObject, AbstractGenericObjectForeignKey,
                         AbstractSelfAwareModel, get_problem_content_types,
                         get_submission_content_types)
from users.models import PCRSUser, Section, AbstractLimitedVisibilityObject


def get_problem_labels():
    """
    Return the list app_labels of apps that contain a Problem class.
    """
    return [c.app_label for c in get_problem_content_types()]


class AbstractProblem(AbstractSelfAwareModel, AbstractLimitedVisibilityObject,
                      AbstractTaggedObject):
    """
    A base class for all problems.

    All problems have visibility level, and optionally tags, and are self-aware.
    """
    challenge = models.ForeignKey(content.models.Challenge, null=True, blank=True,
        related_name='%(app_label)s_%(class)s_related', on_delete=models.SET_NULL)

    max_score = models.SmallIntegerField(default=0, blank=True)

    class Meta:
        abstract = True

    def get_uri_id(self):
        return '{0}-{1}'.format(self.get_problem_type_name(), self.pk,)

    def get_content_type_name(self):
        return 'problem'

    def serialize(self):
        serialized = {}
        for base in [AbstractSelfAwareModel, AbstractLimitedVisibilityObject,
                     AbstractTaggedObject]:
            serialized.update(base.serialize(self))
        serialized.update(
            {
                'problem_type': self.get_problem_type_name(),
                'submit_url': '{}/run'.format(self.get_absolute_url()),
                'max_score': self.max_score,
                'challenge': self.challenge_id
            }
        )
        return serialized

    def __str__(self):
        description = self.description[:150]
        if len(self.description) > 150:
            description += '...'
        return description

    @classmethod
    def get_problem_type_name(cls):
        return cls.__module__.split('.')[0].replace('problems_', '')

    @classmethod
    def get_module_name(cls):
        return cls.__module__.split('.')[0]

    @classmethod
    def get_challenge_to_problem_number(cls):
        """
        Return a dictionary mapping Challenge pk to the the total number of
        problems of this type in that Challenge.
        """
        problems = cls.objects.values('challenge_id')\
                              .annotate(number=Count('id'))\
                              .order_by()
        return {d['challenge_id']: d['number']for d in problems}

    @classmethod
    def get_base_url(cls):
        """
        Return the url prefix for the problem type.
        """
        return '{site}/problems/{typename}'\
            .format(site=settings.SITE_PREFIX,
                    typename=cls.get_problem_type_name())

    def get_absolute_url(self):
        return '{base}/{pk}'.format(base=self.get_base_url(), pk=self.pk)

    def get_submit_url(self):
        return '{}/run'.format(self.get_absolute_url())

    def get_history_url(self):
        return '{}/history'.format(self.get_absolute_url())

    def get_monitoring_url(self):
        return '{}/monitor'.format(self.get_absolute_url())

    def get_browse_submissions_url(self):
        return '{}/browse_submissions'.format(self.get_absolute_url())

    def best_per_user_before_time(self, deadline=timezone.now()):
        """
        Return a list of dictionaries of the form {user_id: , score:)
        representing the best submissions for every user who submitted a
        solution to this problem BEFORE deadline.

        Used for generating CSV reports and problem analysis.
        """
        return self.submission_set.filter(timestamp__lt=deadline)\
            .values('user_id').annotate(score=Max('score')).order_by()

    def clear_submissions(self):
        """
        Delete all submissions to this problem.
        """
        self.submission_set.all().delete()

    def get_best_submission_per_student_after_time(self, section, time):
        """
        Return the list of best submissions made after time in the section.
        """
        return self.submission_set.all().filter(section=section,
                                                timestamp__gt=time,
                                                has_best_score=True)

    def get_monitoring_data(self, section, time):
        """
        Return data for real-time monitoring.
        """
        correct, incorrect = 0, 0
        s_ids = set()
        max_score = self.max_score

        for submission in self.get_best_submission_per_student_after_time(
                section, time):
            s_ids.add(submission.pk)
            if submission.score == max_score:
                correct += 1
            else:
                incorrect += 1

        data = self.get_testitem_data_for_submissions(s_ids)
        return {
            'submissions': [correct, incorrect],
            # order by the id of related object
            'data': [data[key] for key in sorted(data.keys())]
        }

    def get_submissions_for_conditions(self, conditions, starttime=None,
                                       endtime=None):
        restult = set()
        submissions = self.get_submission_class().objects.filter(problem=self)
        if starttime:
            submissions = submissions.filter(timestamp__gt=starttime)
            submissions = submissions.filter(timestamp__lt=endtime)

        for submission in submissions.prefetch_related('testrun_set').all():
            if all([conditions[testrun.testcase.pk] is None or
                                    testrun.test_passed == conditions[testrun.testcase.pk]
                    for testrun in submission.testrun_set.all()]):
                restult.add(submission)
        return restult

    def get_best_score_before_deadline(self, user):
        return self.get_submission_class()\
            .get_best_score_before_deadline(self, user)


class AbstractProgrammingProblem(AbstractProblem, AbstractNamedObject):
    """
    Base class for programming problems.

    Programming problems may have starter starter code and solution.
    """

    starter_code = models.TextField(blank=True)
    solution = models.TextField(blank=True)

    class Meta:
        abstract = True

    def get_testitem_data_for_submissions(self, s_ids):
        """
        Return a list of tuples summarizing for each testcase how many times it
        passed and failed in submissions with pk in s_ids.
        Each tuple has the form (testcase_id, times_passed, times_failed).
        """
        data = self.get_testrun_class().objects.filter(submission_id__in=s_ids)\
            .values('testcase_id', 'test_passed')\
            .annotate(count=Count('test_passed'))
        results = {}
        # data is a list of dictionaries
        # {test_case_id: '',  test_passed: ', count: ''}
        # every dictionary encodes how many times a testcase passed or failed
        for dict in data:
            opt_id = dict['testcase_id']
            count = dict['count']
            res = results.get(opt_id, [0, 0])
            if dict['test_passed'] is True:
                res[0] = count
            if dict['test_passed'] is False:
                res[1] = count
            results[opt_id] = res
        return results

    def serialize(self):
        serialized = {}
        for base in [AbstractNamedObject, AbstractProblem]:
            serialized.update(base.serialize(self))
        return serialized


class AbstractSubmission(AbstractSelfAwareModel):
    """
    Base submission class.

    Submission is associated with a user and a problem, and optionally
    a section, and has a score, usually out of the total number of testcases
    that the associated problem has.
    """
    user = models.ForeignKey(PCRSUser, to_field='username',
                                on_delete=models.CASCADE,
                                related_name='%(app_label)s_%(class)s_related')
    section = models.ForeignKey(Section, blank=True,  null=True,
                                on_delete=models.SET_NULL,
                                related_name='%(app_label)s_%(class)s_related')
    timestamp = models.DateTimeField(default=timezone.now)
    submission = models.TextField(blank=True, null=True)
    score = models.SmallIntegerField(default=0)
    has_best_score = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ['-timestamp']

    def __str__(self):
        return '{problem} by {user} on {time}'.format(
            problem=self.problem, user=self.user.username,
            time=self.timestamp)

    @classmethod
    def deadline_constraint(self):
        return (
            Q(problem__challenge__quest__sectionquest__due_on__isnull=True) |
            Q(problem__challenge__quest__sectionquest__due_on__gt=F('timestamp'))
        )

    @classmethod
    def get_for_users(cls, active_only):
        if active_only:
            return cls.objects.filter(user__is_active=True)
        else:
            return cls.objects

    @classmethod
    def get_for_students(cls, active_only):
        return cls.get_for_users(active_only).filter(user__is_student=True)

    def get_displayable_submission(self):
        '''Override this method to decorate submission text (e.g. in history)
        '''
        return self.submission

    def set_best_submission(self):
        """
        Update the submission such that the latest submission with highest score
        is marked with has_best_score.
        """
        try:
            current_best = self.__class__.objects.filter(
                user=self.user, problem=self.problem, has_best_score=True).latest('id')
            if self.score >= current_best.score and self.pk != current_best.pk:
                current_best.has_best_score = False
                current_best.save()
                self.has_best_score = True
        except self.__class__.DoesNotExist:
            self.has_best_score = True
        finally:
            self.save()

    def set_score(self):
        """
        Set the score of this submission to the number of testcases that
        the submission passed.
        Create a record of the user completing the problem if the score on
        the submission is the highest score possible on the problem.
        """
        self.score = self.testrun_set.filter(test_passed=True).count()
        self.save()
        self.set_best_submission()

    @classmethod
    def get_completed_for_challenge_before_deadline(cls, user, section=None):
        """
        Return a dictionary mapping challenge_pk to the number of open problems
        the user has completed in each Challenge.
        """
        section = section or user.section
        subs = cls.objects\
            .filter(cls.deadline_constraint(),
                    problem__visibility='open',
                    user=user, score=F('problem__max_score'),
                    problem__challenge__quest__sectionquest__section=section)\
            .values('problem__challenge')\
            .annotate(solved=Count('problem', distinct=True))\
            .order_by()
        return {d['problem__challenge']: d['solved']for d in subs}

    @classmethod
    def get_best_attempts_before_deadlines(cls, user, section=None):
        """
        Return a dictionary mapping problem pk to the user's best score on the
        problem with that pk, before the challenge deadline.
        """
        section = section or user.section
        subs = cls.objects\
            .filter(cls.deadline_constraint(), user=user,
                    problem__challenge__quest__sectionquest__section=section)\
            .values('problem_id')\
            .annotate(best=Max('score'), max_score=Max('problem__max_score'))\
            .order_by()
        return ({d['problem_id']: d['best'] for d in subs},
                {d['problem_id']: d['best'] == d['max_score'] for d in subs})

    @classmethod
    def grade(cls, quest, section, active_only=False):
        return cls.get_for_students(active_only)\
            .filter(cls.deadline_constraint(),
                    problem__challenge__quest=quest, user__section=section,
                    problem__challenge__quest__sectionquest__section=section,
                    problem__visibility='open')\
            .values('user', 'problem').annotate(best=Max('score')).order_by()

    @classmethod
    def get_scores_for_challenge(cls, challenge, section, active_only=False):
        return cls.get_for_students(active_only)\
            .filter(problem__challenge=challenge, user__section=section,
                    problem__challenge__quest__sectionquest__section=section)\
            .values('user', 'problem').annotate(best=Max('score')).order_by()

    @classmethod
    def get_problem_status(cls, user):
        return cls.objects\
            .filter(cls.deadline_constraint(), user=user,
                    problem__challenge__quest__sectionquest__section=user.section)\
            .values('user', 'problem').annotate(best=Max('score')).order_by()

    @classmethod
    def get_best_score_before_deadline(cls, problem, user):
        scores = cls.objects.filter(cls.deadline_constraint())\
                            .filter(user=user, problem=problem)\
                            .values_list('score', flat=True)
        return max(scores) if scores else None


class AbstractTestCase(AbstractSelfAwareModel):
    """
    Base testcase class.

    TestCase is associated with a single problem.
    Each problem type should implement its own TestCase according to the
    problem semantics, as well as define what it means for a testcase to pass.
    """

    description = models.TextField(null=False, blank=True)
    is_visible = models.BooleanField(null=False, default=False,
        verbose_name='Testcase visible to students')

    class Meta:
        abstract = True
        ordering = ['pk']

    def __str__(self):
        return '{problem}: testcase {pk}'.format(
            pk=self.pk, problem=self.problem)

    def display(self):
        return self.description or 'Hidden Test' \
               if not self.is_visible else str(self)

    def get_absolute_url(self):
        return '{problem}/testcase/{pk}'.format(
            problem=self.problem.get_absolute_url(), pk=self.pk)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.pk:
            self.problem.max_score += 1
            self.problem.save()
        super().save(force_insert, force_update, using, update_fields)


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


class AbstractJobScheduler(models.Model):
    """
    Base Job Scheduler class.

    Detailed configuration information about the Job Scheduler System that
    PCRS will communicate to solve code problems.
    """
    protocol = models.CharField(max_length=16, blank=True)
    ip = models.CharField(max_length=16, blank=True)
    dns = models.CharField(max_length=200, blank=True)
    port = models.CharField(max_length=10, blank=True)
    api_url = models.CharField(max_length=100, blank=True)
    user = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(blank=False, default=True)

    class Meta:
        abstract = True


class SubmissionPreprocessorMixin:
    def __init__(self, *args, **kwargs):
        self.hidden_lines_list = []
        super(SubmissionPreprocessorMixin, self).__init__(*args, **kwargs)

    '''
    Helpers for tag preprocessing in Submission classes.
    '''
    def preprocessTags(self):
        self.hidden_lines_list = []

        # if code from editor, just return code -- there were no tags
        if self.problem_id == 9999999:
            if len(self.submission) == 0:
                raise Exception("No code found!")
            return [{
                'name': None,
                'code': self.submission,
            }]

        #Code not from editor, process tags
        code = self.fuseStudentCodeIntoStarterCode()
        # Strip blocked/hidden tags but leave their contents (for compiling)
        code = re.sub(r'\[\/?(hidden|blocked)\]\r?\n?', '', code)

        return self.parseCodeIntoFiles(code) or [{
            # If there were no file tags
            'name': 'StudentCode.java',
            'code': code,
        }]

    def parseCodeIntoFiles(self, code):
        '''Parses this submission into corresponding files

        The file tag format is [file <fileName>][/file]
        Returns:
            A list of name-code file dictionaries.
        '''
        files = []

        startTagRegex = re.compile('[\t ]*\[file ([A-Za-z0-9_\.]+)\][\t ]*\n')
        endTagRegex = re.compile('\n[\t ]*\[\/file\][\t ]*');

        startMatch = startTagRegex.search(code)
        while startMatch:
            endMatch = endTagRegex.search(code)
            files.append({
                'name': startMatch.group(1),
                'code': code[startMatch.end():endMatch.start()],
            })
            code = code[endMatch.end():]
            startMatch = startTagRegex.search(code)
        return files

    def fuseStudentCodeIntoStarterCode(self):
        '''Processes the tags in this submission.

        Returns:
            A string representation of the files (including [file] tags)
        '''
        delim = sha1(str(self.problem_id).encode('utf-8')).hexdigest()
        student_code_list = self._parseStudentCodeChunks(self.submission, delim)

        # The fusion of student code with starter_code (from the database)
        mod_submission = self._emplaceStudentCodeSnippets(student_code_list,
            self.problem.starter_code)

        return mod_submission

    def _parseStudentCodeChunks(self, sub, delim):
        '''Extracts code chunks out of a given submission.

        Note that submissions are sent with a delimiter to seperate
        student code chunks.

        Args:
            sub:   The raw submission from the student.
            delim: The delimiter to extract code around.
        '''
        delim_list = [m.start() for m in re.finditer(delim, sub)]

        # Could not find student code
        if len(delim_list) == 0:
            raise Exception("No student code found!")

        chunks = []
        while len(delim_list) >= 2:
            begin = delim_list[0] + len(delim) + 1
            end =  delim_list[1]
            chunks.append(sub[begin:end])
            del delim_list[0], delim_list[0]

        return chunks

    def _emplaceStudentCodeSnippets(self, student_code_list, starter_code):
        '''Emplaces the given code snippets into the given starter code.
        The [student_code] tags will be replaced appropriately.

        Args:
            student_code_list: A list of student code snippets.
            starter_code:      The starter code - probably from the Problem class.
        Returns:
            The given snippets emplaced into the corresponding code tag positions.
        '''
        emplacementRegex = re.compile('\[student_code\].*?\[\/student_code\]\r?\n?', re.DOTALL)
        while len(student_code_list) > 0 and starter_code.find('[student_code]') != -1:
            student_code = student_code_list.pop(0)
            starter_code = re.sub(emplacementRegex, student_code, starter_code, 1)
        return starter_code

# Signal handlers

def testcase_delete(sender, instance, **kwargs):
    """
    Updates the submission scores to a problem when its testcase is deleted.
    """
    try:
        problem = instance.problem
        problem.max_score -= 1
        problem.save()

        submissions_affected = problem.submission_set.all()
        for submission in submissions_affected:
            submission.set_score()
    except sender.get_problem_class().DoesNotExist:
        # problem no longer exists, submissions will be deleted automatically
        # so no need to update scores
        pass


def problem_delete(sender, instance, **kwargs):
    """
    Deletes the ContentSeequenceItem mapping to the Problem when the Problem
    is deleted.
    """
    content.models.ContentSequenceItem.objects.filter(
        content_type=instance.get_content_type(), object_id=instance.pk)\
        .delete()
