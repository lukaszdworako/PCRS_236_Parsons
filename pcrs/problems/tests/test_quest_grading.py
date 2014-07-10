from django import test
from django.core.urlresolvers import reverse
from django.utils.timezone import now, timedelta, localtime

from content.models import SectionQuest, Quest, Challenge
from problems_code.models import Problem, Submission
from problems_multiple_choice.models import Problem as MCProblem
from users.models import Section, PCRSUser


class GradesTestWithDeadlineMixin:
    def setUp(self):
        master = Section.objects.create(section_id='master', location='BA', lecture_time='10-11')
        self.s1 = Section.objects.create(section_id='001', location='BA', lecture_time='10-11')
        self.s2 = Section.objects.create(section_id='002', location='BA', lecture_time='11-12')

        self.student1 = PCRSUser.objects.create(username='student1', section=self.s1)
        self.student2 = PCRSUser.objects.create(username='student2', section=self.s2)

        self.instructor = PCRSUser.objects.create(username='instructor',
                                                  is_instructor=True,
                                                  section=master)

        self.quest1 = Quest.objects.create(name='q1', description='q1')
        self.quest2 = Quest.objects.create(name='q2', description='q2')

        SectionQuest.objects.filter(section=self.s1)\
                            .update(due_on=localtime(now()) + timedelta(days=7))
        SectionQuest.objects.filter(section=self.s2)\
                            .update(due_on=localtime(now()) - timedelta(days=7))


        self.c1 = Challenge.objects.create(name='1', description='1', quest=self.quest1)
        self.c2 = Challenge.objects.create(name='2', description='2', quest=self.quest2)


class TestQuestGrading(GradesTestWithDeadlineMixin, test.TestCase):
    problem_class = Problem
    submission_class = Submission

    def test_no_deadline(self):
        """
        Test a single problem in challenge.
        """
        SectionQuest.objects.update(due_on=None)

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
        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student1,4', lines)

        expected = [{'user': 'student2', 'best': 4, 'problem': 1}]
        actual = self.submission_class.grade(quest=self.quest1, section=self.s2)
        self.assertListEqual(expected, list(actual))

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s2.section_id}),
            {'quest': self.quest1.pk, 'section': self.s2.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student2,4', lines)

    def test_multiple_sub_to_one_problem(self):
        """
        Test a single problem in challenge.
        """
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
        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student1,4', lines)

        # for section2 the deadline passed, submissions made now do not count
        actual = self.submission_class.grade(quest=self.quest1, section=self.s2)
        self.assertListEqual([], list(actual))

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s2.section_id}),
            {'quest': self.quest1.pk, 'section': self.s2.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student2,', lines)


    def test_multiple_sub_to_one_problem_some_after(self):
        """
        Test a single problem in challenge, with submissions after the
        deadline.
        """
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

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student1,4', lines)

        # for section2 the deadline passed, submissions made now do not count
        expected = [{'user': 'student2', 'best': 3, 'problem': 1}]
        actual = self.submission_class.grade(quest=self.quest1, section=self.s2)
        self.assertListEqual(expected, list(actual))

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s2.section_id}),
            {'quest': self.quest1.pk, 'section': self.s2.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student2,3', lines)

    def test_multiple_sub_to_multiple_problems_some_after(self):
        """
        Test multiple problems in one challenge, with submissions after the
        deadline.
        """
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
        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test,test2', lines)
        self.assertIn(b'0,0', lines)
        self.assertIn(b'student1,4,6', lines)

        # for section2 the deadline passed, submissions made now do not count
        expected = [{'user': 'student2', 'best': 3, 'problem': 2},
                    {'user': 'student2', 'best': 2, 'problem': 1}]
        actual = self.submission_class.grade(quest=self.quest1, section=self.s2)
        self.assertListEqual(expected, list(actual))
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s2.section_id}),
            {'quest': self.quest1.pk, 'section': self.s2.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test,test2', lines)
        self.assertIn(b'0,0', lines)
        self.assertIn(b'student2,2,3', lines)

    def test_multiple_sub_to_multiple_problems_challenges_some_after(self):
        """
        Test two quests having different deadlines for sections, with some
        submissions after the appropriate deadline.
        """
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

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student1,4', lines)

        # for section2 the deadline passed, submissions made now do not count
        expected = [{'user': 'student2', 'best': 2, 'problem': 1}]
        actual = self.submission_class.grade(quest=self.quest1, section=self.s2)
        self.assertListEqual(expected, list(actual))
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s2.section_id}),
            {'quest': self.quest1.pk, 'section': self.s2.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student2,2', lines)

        # quest 2
        expected = [{'user': 'student1', 'best': 6, 'problem': 2}]
        actual = self.submission_class.grade(quest=self.quest2, section=self.s1)
        self.assertListEqual(expected, list(actual))
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest2.pk, 'section': self.s1.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test2', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student1,6', lines)

        # for section2 the deadline passed, submissions made now do not count
        expected = [{'user': 'student2', 'best': 3, 'problem': 2}]
        actual = self.submission_class.grade(quest=self.quest2, section=self.s2)
        self.assertListEqual(expected, list(actual))
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s2.section_id}),
            {'quest': self.quest2.pk, 'section': self.s2.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test2', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student2,3', lines)

    def test_multiple_sub_to_multiple_problems_quests(self):
        """
        Test two quests having different deadlines that are the same
        for both section.
        """
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

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student1,4', lines)

        expected = [{'user': 'student2', 'best': 5, 'problem': 1}]
        actual = self.submission_class.grade(quest=self.quest1, section=self.s2)
        self.assertListEqual(expected, list(actual))
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s2.section_id}),
            {'quest': self.quest1.pk, 'section': self.s2.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student2,5', lines)

        # quest 2
        expected = [{'user': 'student1', 'best': 3, 'problem': 2}]
        actual = self.submission_class.grade(quest=self.quest2, section=self.s1)
        self.assertListEqual(expected, list(actual))

        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest2.pk, 'section': self.s1.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test2', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student1,3', lines)

        # for section2 the deadline passed, submissions made now do not count
        expected = [{'user': 'student2', 'best': 3, 'problem': 2}]
        actual = self.submission_class.grade(quest=self.quest2, section=self.s2)
        self.assertListEqual(expected, list(actual))

        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s2.section_id}),
            {'quest': self.quest2.pk, 'section': self.s2.section_id})
        self.assertEqual(200, response.status_code)
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test2', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student2,3', lines)


class TestGradeReports(GradesTestWithDeadlineMixin, test.TestCase):

    def test_headers(self):
        """
        Test that the csv file contains the two header lines that are the
        problem sting representation and problem maximum scores.
        """
        problem1 = Problem.objects.create(
            pk=1, name='test', description='test', challenge=self.c1, max_score=4)
        problem2 = MCProblem.objects.create(
            pk=2, name='test2', description='test', challenge=self.c1, max_score=3)

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test,test2: test', lines)
        self.assertIn(b'4,3', lines)
        self.assertIn(b'student1,,', lines)

    def test_no_submissions_one_problem(self):
        """
        Test grade report with one student in section who made no submissions to
        a single problem in the quest, and that problems in a different quest
        do not appear in the grades file.
        """
        problem1 = Problem.objects.create(
            pk=1, name='test', description='test', challenge=self.c1)
        problem2 = MCProblem.objects.create(
            pk=2, name='test2', description='test', challenge=self.c2)

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test', lines)
        self.assertIn(b'0', lines)
        self.assertIn(b'student1,', lines)

    def test_no_submissions_one_type_problems(self):
        """
        Test multiple problems of one type in a challenge, with no submissions.
        """
        problem1 = Problem.objects.create(
            pk=1, name='test', description='test', challenge=self.c1)
        problem2 = Problem.objects.create(
            pk=2, name='test2', description='test', challenge=self.c1)

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test,test2', lines)
        self.assertIn(b'0,0', lines)
        self.assertIn(b'student1,,', lines)

    def test_no_submissions(self):
        """
        Test multiple problems of different types in a challenge,
        with no submissions.
        """
        problem1 = Problem.objects.create(
            pk=1, name='test', description='test', challenge=self.c1)
        problem2 = MCProblem.objects.create(
            pk=2, name='test2', description='test', challenge=self.c1)

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test,test2: test', lines)
        self.assertIn(b'0,0', lines)
        self.assertIn(b'student1,,', lines)

    def test_with_all_submissions(self):
        """
        Test multiple problems of different types in a challenge,
        with submissions to all problems.
        """
        problem1 = Problem.objects.create(
            pk=1, name='test', description='test', challenge=self.c1)
        problem2 = MCProblem.objects.create(
            pk=2, name='test2', description='test', challenge=self.c1)

        for problem in [problem1, problem2]:
            for score in [2, 1, 0, 1]:
                for student in [self.student1, self.student2]:
                    s = problem.get_submission_class().objects.create(
                        problem=problem, user=student, score=score)

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test,test2: test', lines)
        self.assertIn(b'0,0', lines)
        self.assertIn(b'student1,2,2', lines)

    def test_with_some_submissions(self):
        """
        Test multiple problems of different types in a challenge,
        with submissions to one problem.
        """
        problem1 = Problem.objects.create(
            pk=1, name='test', description='test', challenge=self.c1)
        problem2 = MCProblem.objects.create(
            pk=2, name='test2', description='test', challenge=self.c1)

        for score in [2, 1, 0, 1]:
            for student in [self.student1, self.student2]:
                s = problem1.get_submission_class().objects.create(
                    problem=problem1, user=student, score=score)

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test,test2: test', lines)
        self.assertIn(b'0,0', lines)
        self.assertIn(b'student1,2,', lines)

    def test_with_some_submissions2(self):
        """
        Test multiple problems of different types in a challenge,
        with submissions to one problem, that is the second problem.
        """
        problem1 = Problem.objects.create(
            pk=1, name='test', description='test', challenge=self.c1)
        problem2 = MCProblem.objects.create(
            pk=2, name='test2', description='test', challenge=self.c1)

        for score in [2, 1, 0, 1]:
            for student in [self.student1, self.student2]:
                s = problem2.get_submission_class().objects.create(
                    problem=problem2, user=student, score=score)

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test,test2: test', lines)
        self.assertIn(b'0,0', lines)
        self.assertIn(b'student1,,2', lines)

    def test_with_many_submissions(self):
        """
        Test multiple problems of different types in a challenge,
        with multiple submissions to all problems.
        """
        problem1 = Problem.objects.create(
            pk=1, name='test', description='test', challenge=self.c1)
        problem2 = MCProblem.objects.create(
            pk=2, name='test2', description='test', challenge=self.c1)

        for score in [2, 1, 3, 1]:
            for student in [self.student1, self.student2]:
                s = problem1.get_submission_class().objects.create(
                    problem=problem1, user=student, score=score)

        for score in [2, 1, 0, 1]:
            for student in [self.student1, self.student2]:
                s = problem2.get_submission_class().objects.create(
                    problem=problem2, user=student, score=score)

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test,test2: test', lines)
        self.assertIn(b'0,0', lines)
        self.assertIn(b'student1,3,2', lines)

    def test_no_dealine(self):
        SectionQuest.objects.update(due_on=None)
        problem1 = Problem.objects.create(
            pk=1, name='test', description='test', challenge=self.c1)
        problem2 = MCProblem.objects.create(
            pk=2, name='test2', description='test', challenge=self.c1)

        for score in [2, 1, 3, 1]:
            for student in [self.student1, self.student2]:
                s = problem1.get_submission_class().objects.create(
                    problem=problem1, user=student, score=score)

        for score in [2, 1, 0, 1]:
            for student in [self.student1, self.student2]:
                s = problem2.get_submission_class().objects.create(
                    problem=problem2, user=student, score=score)

        self.client.login(username=self.instructor)
        response = self.client.post(
            reverse('section_reports', kwargs={'pk': self.s1.section_id}),
            {'quest': self.quest1.pk, 'section': self.s1.section_id})
        lines = response.content.splitlines()
        self.assertEqual(3, len(lines))
        self.assertIn(b'test,test2: test', lines)
        self.assertIn(b'0,0', lines)
        self.assertIn(b'student1,3,2', lines)