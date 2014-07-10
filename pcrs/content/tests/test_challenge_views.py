from datetime import timedelta
from unittest import skip
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import now

from content.models import (Quest, Challenge, ContentPage, SectionQuest,
                            ContentSequenceItem)
from problems_code.models import Problem, Submission
from tests import UsersMixin


class TestContentPage(UsersMixin, TestCase):
    url = reverse('challenge_page', kwargs={'challenge': 2, 'page': 1})

    def setUp(self):
        UsersMixin.setUp(self)
        q = Quest.objects.create(name='q', description='q', mode='live')
        SectionQuest.objects.update(open_on=now(), visibility='open')
        self.c1 = Challenge.objects.create(pk=1, name='c', visibility='open', quest=q)
        self.c2 = Challenge.objects.create(pk=2, name='c2', visibility='open', quest=q)
        self.c1_page = ContentPage.objects.create(challenge=self.c1, order=1)
        self.c2_page = ContentPage.objects.create(challenge=self.c2, order=1)
        for i in range(3):
            p = Problem.objects.create(name=str(i), challenge=self.c1,
                                       visibility='open', max_score=5)
            ContentSequenceItem.objects.create(content_page=self.c1_page,
                                               content_object=p)
            p = Problem.objects.create(name=str(i)+'x', challenge=self.c2,
                                       visibility='open', max_score=5)
            ContentSequenceItem.objects.create(content_page=self.c2_page,
                                               content_object=p)

        self.client.login(username=self.student.username)

    def test_no_prereqs(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_prereqs_not_enforced(self):
        self.c2.prerequisites.add(self.c1)
        self.c2.enforce_prerequisites = False
        self.c2.save()

        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_prereqs_enforced(self):
        self.c2.prerequisites.add(self.c1)
        self.c2.enforce_prerequisites = True
        self.c2.save()

        self.assertEqual([self.c1], list(self.c2.prerequisites.all()))

        response = self.client.get(self.url)
        self.assertRedirects(response,
            reverse('challenge_missing_prerequisites', kwargs={'pk': 2}))

    def test_prereqs_enforced_and_completed(self):
        self.c2.prerequisites.add(self.c1)
        self.c2.enforce_prerequisites = True
        self.c2.save()

        for content_object in ContentSequenceItem.objects.filter(
                content_page__challenge=self.c1):
            Submission.objects.create(user=self.student,
                problem=content_object.content_object, submission='s', score=5)

        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_prereqs_enforced_and_completed_before_deadline(self):
        SectionQuest.objects.update(open_on=now(), visibility='open',
            due_on=now()+timedelta(days=7))

        self.c2.prerequisites.add(self.c1)
        self.c2.enforce_prerequisites = True
        self.c2.save()

        for content_object in ContentSequenceItem.objects.filter(
                content_page__challenge=self.c1):
            Submission.objects.create(user=self.student,
                problem=content_object.content_object, submission='s', score=5)

        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    @skip('needs to be implemented')
    def test_prereqs_enforced_and_completed_after_deadline(self):
        SectionQuest.objects.update(open_on=now(), visibility='open',
            due_on=now()-timedelta(days=7))

        self.c2.prerequisites.add(self.c1)
        self.c2.enforce_prerequisites = True
        self.c2.save()

        for content_object in ContentSequenceItem.objects.filter(
                content_page__challenge=self.c1):
            Submission.objects.create(user=self.student,
                problem=content_object.content_object, submission='s', score=5)

        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)