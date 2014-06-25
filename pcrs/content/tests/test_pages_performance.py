from django.core.urlresolvers import reverse
from django.db import connection
from django.test import TransactionTestCase
from django.utils.timezone import now

from content.models import *
from problems_code.models import Problem, Submission
from tests.ViewTestMixins import ProtectedViewTestMixin, UsersMixin


class TestQuestsPageDatabaseHits(ProtectedViewTestMixin, TransactionTestCase):
    """
    Test the number of database hits when loading the quests page.

    Should be kept constant.
    """
    db_hits = 16
    url = reverse('quests')
    template = 'content/quests.html'

    def test_no_quests(self):
        with self.assertNumQueries(self.db_hits):
            response = self.client.get(self.url)

    def test_quests_only(self):
        num_quests = 20

        for i in range(num_quests):
            Quest.objects.create(name=str(i), description='c')
        SectionQuest.objects.update(open_on=now(), visibility='open')

        self.assertEqual(num_quests, Quest.objects.count())
        self.assertEqual(num_quests, SectionQuest.objects.count())

        with self.assertNumQueries(self.db_hits):
            response = self.client.get('/content/quests')

    def test_quests_and_challenges(self):
        num_quests = 10
        num_challenges = 10

        for i in range(num_quests):
            q = Quest.objects.create(name=str(i))
            for j in range(num_challenges):
                Challenge.objects.create(name=str(i)+'_'+str(j),
                                         visibility='open', quest=q)
        SectionQuest.objects.update(open_on=now(), visibility='open')

        self.assertEqual(num_quests, Quest.objects.count())
        self.assertEqual(num_quests, SectionQuest.objects.count())
        self.assertEqual(num_quests*num_challenges, Challenge.objects.count())
        with self.assertNumQueries(self.db_hits):
            response = self.client.get('/content/quests')

    def test_quests_challenges_objects(self):
        num_quests = 10
        num_c = 5
        num_pages = 5
        num_objects = 5
        for i in range(num_quests):
            q = Quest.objects.create(name=str(i), description='c')
            for j in range(num_c):
                c = Challenge.objects.create(name=str(i)+'_'+str(j),
                                             visibility='open', quest=q)
                c2 = Challenge.objects.create(name=str(i)+'_'+str(j)+'p',
                                              visibility='open', quest=q)

                for k in range(num_pages):
                    page1 = ContentPage.objects.create(challenge=c, order=k)
                    page2 = ContentPage.objects.create(challenge=c2, order=k)

                    for l in range(num_objects):
                        name = '{0}_{1}_{2}_{3}'.format(i, j, k, l)
                        v = Video.objects.create(name=name, link='l',
                                                 thumbnail='l', download='l')

                        p1 = Problem.objects.create(name=name, challenge=c,
                                                    visibility='open')

                        p2 = Problem.objects.create(name=name+'p', challenge=c2,
                                                    visibility='open')
                        ContentSequenceItem.objects.bulk_create(
                            [ContentSequenceItem(
                                content_object=item, content_page=page)
                             for page in [page1, page2] for item in [v, p1, p2]
                            ]
                        )

        SectionQuest.objects.update(open_on=now(), visibility='open')

        self.assertEqual(num_quests, Quest.objects.count())
        self.assertEqual(num_quests, SectionQuest.objects.count())
        self.assertEqual(num_quests*num_c*2, Challenge.objects.count())
        self.assertEqual(num_quests*(num_c*2)*(num_pages)*(num_objects*3),
                         ContentSequenceItem.objects.count())
        with self.assertNumQueries(self.db_hits):
            response = self.client.get('/content/quests')

    def test_quests_problem_sets_problems_submissions(self):
        num_quests = 5
        num_c = 5
        num_pages = 5
        num_objects = 5
        num_sub = 5

        for i in range(num_quests):
            q = Quest.objects.create(name=str(i), description='c')

            for j in range(num_c):
                c = Challenge.objects.create(name=str(i)+'_'+str(j),
                                             visibility='open', quest=q)
                for k in range(num_pages):
                    page = ContentPage.objects.create(challenge=c, order=k)
                    for l in range(num_objects):
                        name = '{0}_{1}_{2}_{3}'.format(i, j, k, l)
                        v = Video.objects.create(name=name, link='l',
                                                 thumbnail='l', download='l')
                        ContentSequenceItem.objects.create(
                            content_object=v, content_page=page, order=l)
                        p = Problem.objects.create(name=name, challenge=c,
                                                   visibility='open')
                        ContentSequenceItem.objects.create(content_object=p,
                                                           content_page=page)
                        for m in range(num_sub):
                            Submission.objects.bulk_create(
                                [Submission(problem=p, user=user, score=1)
                                 for user in [self.student, self.instructor, self.ta]
                                ])


        SectionQuest.objects.update(open_on=now(), visibility='open')

        self.assertEqual(num_quests, Quest.objects.count())
        self.assertEqual(num_quests, SectionQuest.objects.count())
        self.assertEqual(num_quests*num_c, Challenge.objects.count())
        self.assertEqual(num_quests*num_c*num_pages*num_objects*2,
                         ContentSequenceItem.objects.count())

        self.client.login(username=self.student.username)
        with self.assertNumQueries(self.db_hits):
            response = self.client.get('/content/quests')


class TestContentPageDatabaseHits(UsersMixin, TransactionTestCase):
    """
    Test the number of database hits when loading a page for a Challenge.

    Should be kept constant.
    """
    db_hits = 18
    template = 'content/content_page.html'

    def test_quests_challenges_objects(self):
        num_quests = 5
        num_c = 5
        num_pages = 5
        num_objects = 10
        for i in range(num_quests):
            q = Quest.objects.create(name=str(i), description='c')
            for j in range(num_c):
                c = Challenge.objects.create(name=str(i)+'_'+str(j),
                                             visibility='open', quest=q)
                c2 = Challenge.objects.create(name=str(i)+'_'+str(j)+'p',
                                              visibility='open', quest=q)

                for k in range(num_pages):
                    page1 = ContentPage.objects.create(challenge=c, order=k)
                    page2 = ContentPage.objects.create(challenge=c2, order=k)

                    for l in range(num_objects):
                        name = '{0}_{1}_{2}_{3}'.format(i, j, k, l)
                        v = Video.objects.create(name=name, link='l',
                                                 thumbnail='l', download='l')

                        p1 = Problem.objects.create(name=name, challenge=c,
                                                    visibility='open')

                        p2 = Problem.objects.create(name=name+'p', challenge=c2,
                                                    visibility='open')
                        ContentSequenceItem.objects.bulk_create(
                            [ContentSequenceItem(
                                content_object=item, content_page=page)
                             for page in [page1, page2] for item in [v, p1, p2]
                            ]
                        )

        SectionQuest.objects.update(open_on=now(), visibility='open')

        self.assertEqual(num_quests, Quest.objects.count())
        self.assertEqual(num_quests, SectionQuest.objects.count())
        self.assertEqual(num_quests*num_c*2, Challenge.objects.count())
        self.assertEqual(num_quests*(num_c*2)*(num_pages)*(num_objects*3),
                         ContentSequenceItem.objects.count())

        c = Challenge.objects.all()[0]
        url = reverse('challenge_page', kwargs={'challenge': c.pk, 'page': 0})
        self.client.login(username=self.student.username)
        with self.assertNumQueries(self.db_hits):
            response = self.client.get(url)

    def test_quests_problem_sets_problems_submissions(self):
        num_quests = 5
        num_c = 5
        num_pages = 5
        num_objects = 5
        num_sub = 5

        for i in range(num_quests):
            q = Quest.objects.create(name=str(i), description='c')

            for j in range(num_c):
                c = Challenge.objects.create(name=str(i)+'_'+str(j),
                                             visibility='open', quest=q)
                for k in range(num_pages):
                    page = ContentPage.objects.create(challenge=c, order=k)
                    for l in range(num_objects):
                        name = '{0}_{1}_{2}_{3}'.format(i, j, k, l)
                        v = Video.objects.create(name=name, link='l',
                                                 thumbnail='l', download='l')
                        ContentSequenceItem.objects.create(
                            content_object=v, content_page=page, order=l)
                        p = Problem.objects.create(name=name, challenge=c,
                                                   visibility='open')
                        ContentSequenceItem.objects.create(content_object=p,
                                                           content_page=page)
                        for m in range(num_sub):
                            Submission.objects.bulk_create(
                                [Submission(problem=p, user=user, score=1)
                                 for user in [self.student, self.instructor, self.ta]
                                ])

        SectionQuest.objects.update(open_on=now(), visibility='open')

        self.assertEqual(num_quests, Quest.objects.count())
        self.assertEqual(num_quests, SectionQuest.objects.count())
        self.assertEqual(num_quests*num_c, Challenge.objects.count())
        self.assertEqual(num_quests*num_c*num_pages*num_objects*2,
                         ContentSequenceItem.objects.count())

        c = Challenge.objects.all()[0]
        url = reverse('challenge_page', kwargs={'challenge': c.pk, 'page': 0})
        self.client.login(username=self.student.username)
        with self.assertNumQueries(self.db_hits):
            response = self.client.get(url)
            print(connection.queries)

    def test_quests_problem_sets_problems_submissions_prerequisites(self):
        num_quests = 2
        num_c = 5
        num_pages = 5
        num_objects = 5
        num_sub = 5

        for i in range(num_quests):
            q = Quest.objects.create(name=str(i), description='c')

            for j in range(num_c):
                c = Challenge.objects.create(name=str(i)+'_'+str(j),
                                             visibility='open', quest=q)
                for k in range(num_pages):
                    page = ContentPage.objects.create(challenge=c, order=k)
                    for l in range(num_objects):
                        name = '{0}_{1}_{2}_{3}'.format(i, j, k, l)
                        v = Video.objects.create(name=name, link='l',
                                                 thumbnail='l', download='l')
                        ContentSequenceItem.objects.create(
                            content_object=v, content_page=page, order=l)
                        p = Problem.objects.create(name=name, challenge=c,
                                                   visibility='open')
                        ContentSequenceItem.objects.create(content_object=p,
                                                           content_page=page)
                        for m in range(num_sub):
                            Submission.objects.bulk_create(
                                [Submission(problem=p, user=user, score=1)
                                 for user in [self.student, self.instructor, self.ta]
                                ])

        SectionQuest.objects.update(open_on=now(), visibility='open')

        self.assertEqual(num_quests, Quest.objects.count())
        self.assertEqual(num_quests, SectionQuest.objects.count())
        self.assertEqual(num_quests*num_c, Challenge.objects.count())
        self.assertEqual(num_quests*num_c*num_pages*num_objects*2,
                         ContentSequenceItem.objects.count())

        c = Challenge.objects.all()[0]
        url = reverse('challenge_page', kwargs={'challenge': c.pk, 'page': 0})
        c.prerequisites.add(*Challenge.objects.exclude(pk=1)
            .values_list('id', flat=True))
        c.save()

        self.client.login(username=self.student.username)
        with self.assertNumQueries(10):
            response = self.client.get(url)