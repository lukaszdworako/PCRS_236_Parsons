from django import test
from django.utils.timezone import now, timedelta, localtime

from content.models import SectionQuest, Quest, Challenge
from problems_code.models import Problem, Submission
from users.models import Section, PCRSUser


class TestQuestGrading(test.TestCase):
    problem_class = Problem
    submission_class = Submission

    def setUp(self):
        self.s1 = Section.objects.create(section_id='001', location='BA', lecture_time='10-11')
        self.s2 = Section.objects.create(section_id='002', location='BA', lecture_time='11-12')

        self.student1 = PCRSUser.objects.create(username='student1', section=self.s1)
        self.student2 = PCRSUser.objects.create(username='student2', section=self.s2)

        self.quest1 = Quest.objects.create(name='q1', description='q1')
        self.quest2 = Quest.objects.create(name='q2', description='q2')

        SectionQuest.objects.filter(section=self.s1)\
                            .update(due_on=localtime(now()) + timedelta(days=7))
        SectionQuest.objects.filter(section=self.s2)\
                            .update(due_on=localtime(now()) - timedelta(days=7))


        self.c1 = Challenge.objects.create(name='1', description='1', quest=self.quest1)
        self.c2 = Challenge.objects.create(name='2', description='2', quest=self.quest2)

    def test_multiple_sub_to_one_problem(self):
        problem = self.problem_class.objects.create(pk=1, name='test',
            description='test', challenge=self.c1)
        for score in [2, 1, 0, 4]:
            for student in [self.student1, self.student2]:
                self.submission_class.objects.create(
                    problem=problem, user=student, score=score
                )
        expected = [{'user': 'student1', 'best': 4, 'problem': 1}]
        actual = self.submission_class.grade(quest=self.quest1, section=self.s1)
        self.assertListEqual(expected, list(actual))

        # for section2 the deadline passed, submissions made now do not count
        actual = self.submission_class.grade(quest=self.quest1, section=self.s2)
        self.assertListEqual([], list(actual))

    def test_multiple_sub_to_one_problem_some_after(self):
        problem = self.problem_class.objects.create(pk=1, name='test',
            description='test', challenge=self.c1)
        for score in [2, 1, 0, 3]:
            for student in [self.student1, self.student2]:
                self.submission_class.objects.create(
                    problem=problem, user=student, score=score)
        Submission.objects.update(timestamp=localtime(now()) - timedelta(days=10))

        self.submission_class.objects.create(
                    problem=problem, user=self.student1, score=4)
        self.submission_class.objects.create(
                    problem=problem, user=self.student2, score=5)
        # the latest submission counts only for student1 whose deadline has
        # not passed
        expected = [{'user': 'student1', 'best': 4, 'problem': 1}]
        actual = self.submission_class.grade(quest=self.quest1, section=self.s1)
        self.assertListEqual(expected, list(actual))

        # for section2 the deadline passed, submissions made now do not count
        expected = [{'user': 'student2', 'best': 3, 'problem': 1}]
        actual = self.submission_class.grade(quest=self.quest1, section=self.s2)
        self.assertListEqual(expected, list(actual))

    def test_multiple_sub_to_multiple_problems_some_after(self):
        problem1 = self.problem_class.objects.create(pk=1, name='test',
            description='test', challenge=self.c1)
        problem2 = self.problem_class.objects.create(pk=2, name='test2',
            description='test', challenge=self.c1)

        for score in [2, 1, 0, 1]:
            for student in [self.student1, self.student2]:
                s = self.submission_class.objects.create(
                    problem=problem1, user=student, score=score)
                s.timestamp = localtime(now()) - timedelta(days=10)
                s.save()

        for score in [1, 3, 3, 2]:
            for student in [self.student1, self.student2]:
                s = self.submission_class.objects.create(
                    problem=problem2, user=student, score=score)
                s.timestamp = localtime(now()) - timedelta(days=10)
                s.save()

        self.submission_class.objects.create(
                    problem=problem1, user=self.student1, score=4)
        self.submission_class.objects.create(
                    problem=problem1, user=self.student2, score=5)
        self.submission_class.objects.create(
                    problem=problem2, user=self.student1, score=6)
        self.submission_class.objects.create(
                    problem=problem2, user=self.student2, score=7)

        # the latest submission counts only for student1 whose deadline has
        # not passed
        expected = [{'user': 'student1', 'best': 6, 'problem': 2},
                    {'user': 'student1', 'best': 4, 'problem': 1}]
        actual = self.submission_class.grade(quest=self.quest1, section=self.s1)
        self.assertListEqual(expected, list(actual))

        # for section2 the deadline passed, submissions made now do not count
        expected = [{'user': 'student2', 'best': 3, 'problem': 2},
                    {'user': 'student2', 'best': 2, 'problem': 1}]
        actual = self.submission_class.grade(quest=self.quest1, section=self.s2)
        self.assertListEqual(expected, list(actual))

    def test_multiple_sub_to_multiple_problems_challenges_some_after(self):
        problem1 = self.problem_class.objects.create(pk=1, name='test',
            description='test', challenge=self.c1)
        problem2 = self.problem_class.objects.create(pk=2, name='test2',
            description='test', challenge=self.c2)

        for score in [2, 1, 0, 1]:
            for student in [self.student1, self.student2]:
                s = self.submission_class.objects.create(
                    problem=problem1, user=student, score=score)
                s.timestamp = localtime(now()) - timedelta(days=10)
                s.save()

        for score in [1, 3, 3, 2]:
            for student in [self.student1, self.student2]:
                s = self.submission_class.objects.create(
                    problem=problem2, user=student, score=score)
                s.timestamp = localtime(now()) - timedelta(days=10)
                s.save()

        self.submission_class.objects.create(
                    problem=problem1, user=self.student1, score=4)
        self.submission_class.objects.create(
                    problem=problem1, user=self.student2, score=5)
        self.submission_class.objects.create(
                    problem=problem2, user=self.student1, score=6)
        self.submission_class.objects.create(
                    problem=problem2, user=self.student2, score=7)

        # quest 1
        # the latest submission counts only for student1 whose deadline has
        # not passed
        expected = [{'user': 'student1', 'best': 4, 'problem': 1}]
        actual = self.submission_class.grade(quest=self.quest1, section=self.s1)
        self.assertListEqual(expected, list(actual))

        # for section2 the deadline passed, submissions made now do not count
        expected = [{'user': 'student2', 'best': 2, 'problem': 1}]
        actual = self.submission_class.grade(quest=self.quest1, section=self.s2)
        self.assertListEqual(expected, list(actual))

        # quest 2
        expected = [{'user': 'student1', 'best': 6, 'problem': 2}]
        actual = self.submission_class.grade(quest=self.quest2, section=self.s1)
        self.assertListEqual(expected, list(actual))

        # for section2 the deadline passed, submissions made now do not count
        expected = [{'user': 'student2', 'best': 3, 'problem': 2}]
        actual = self.submission_class.grade(quest=self.quest2, section=self.s2)
        self.assertListEqual(expected, list(actual))

    def test_multiple_sub_to_multiple_problems_quests(self):
        SectionQuest.objects.filter(quest=self.quest1)\
                            .update(due_on=localtime(now()) + timedelta(days=7))
        SectionQuest.objects.filter(quest=self.quest2)\
                            .update(due_on=localtime(now()) - timedelta(days=7))

        problem1 = self.problem_class.objects.create(pk=1, name='test',
            description='test', challenge=self.c1)
        problem2 = self.problem_class.objects.create(pk=2, name='test2',
            description='test', challenge=self.c2)

        for score in [2, 1, 0, 1]:
            for student in [self.student1, self.student2]:
                s = self.submission_class.objects.create(
                    problem=problem1, user=student, score=score)
                s.timestamp = localtime(now()) - timedelta(days=10)
                s.save()

        for score in [1, 3, 3, 2]:
            for student in [self.student1, self.student2]:
                s = self.submission_class.objects.create(
                    problem=problem2, user=student, score=score)
                s.timestamp = localtime(now()) - timedelta(days=10)
                s.save()

        self.submission_class.objects.create(
                    problem=problem1, user=self.student1, score=4)
        self.submission_class.objects.create(
                    problem=problem1, user=self.student2, score=5)
        self.submission_class.objects.create(
                    problem=problem2, user=self.student1, score=6)
        self.submission_class.objects.create(
                    problem=problem2, user=self.student2, score=7)

        # quest 1

        expected = [{'user': 'student1', 'best': 4, 'problem': 1}]
        actual = self.submission_class.grade(quest=self.quest1, section=self.s1)
        self.assertListEqual(expected, list(actual))

        expected = [{'user': 'student2', 'best': 5, 'problem': 1}]
        actual = self.submission_class.grade(quest=self.quest1, section=self.s2)
        self.assertListEqual(expected, list(actual))

        # quest 2
        expected = [{'user': 'student1', 'best': 3, 'problem': 2}]
        actual = self.submission_class.grade(quest=self.quest2, section=self.s1)
        self.assertListEqual(expected, list(actual))

        # for section2 the deadline passed, submissions made now do not count
        expected = [{'user': 'student2', 'best': 3, 'problem': 2}]
        actual = self.submission_class.grade(quest=self.quest2, section=self.s2)
        self.assertListEqual(expected, list(actual))