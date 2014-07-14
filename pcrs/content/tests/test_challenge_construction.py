from django.core.urlresolvers import reverse
from django.test import TestCase

from content.models import Challenge, ContentPage, Video, ContentSequenceItem, \
    TextBlock
from problems_multiple_choice.models import Problem
from tests import UsersMixin


class TestPageCreation(UsersMixin, TestCase):
    """
    Test creating challenge pages.
    """

    url = reverse('page_create', kwargs={'challenge': 1})

    def setUp(self):
        UsersMixin.setUp(self)
        self.client.login(username='instructor')

    def test_adding_first_page(self):
        Challenge.objects.create(pk=1, name='fire', description='hot')

        response = self.client.post(self.url, {})
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, ContentPage.objects.count())
        content_page = ContentPage.objects.all()[0]
        self.assertEqual(1, content_page.challenge.pk)
        self.assertEqual(1, content_page.order)

    def test_adding_second_page(self):
        challenge = Challenge.objects.create(pk=1, name='fire', description='hot')
        ContentPage.objects.create(challenge=challenge, order=0)

        response = self.client.post(self.url, {})
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, ContentPage.objects.count())
        page1, page2 = ContentPage.objects.order_by('order')
        self.assertEqual(1, page1.challenge.pk)
        self.assertEqual(1, page1.order)
        self.assertEqual(1, page2.challenge.pk)
        self.assertEqual(2, page2.order)


class TestPageDeletion(UsersMixin, TestCase):
    """
    Test deleting challenge pages.
    """

    def setUp(self):
        UsersMixin.setUp(self)
        self.client.login(username='instructor')

    def test_delete_only_page(self):
        challenge = Challenge.objects.create(pk=1, name='fire', description='hot')
        page = ContentPage.objects.create(challenge=challenge, order=0)

        url = reverse('page_delete', kwargs={'challenge': 1, 'pk': page.pk})
        response = self.client.post(url, {})
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, ContentPage.objects.count())

    def test_delete_first_page(self):
        challenge = Challenge.objects.create(pk=1, name='fire', description='hot')
        page1 = ContentPage.objects.create(challenge=challenge, order=1)
        page2 = ContentPage.objects.create(challenge=challenge, order=2)

        url = reverse('page_delete', kwargs={'challenge': 1, 'pk': page1.pk})
        response = self.client.post(url, {})
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, ContentPage.objects.count())
        page = ContentPage.objects.all()[0]
        self.assertEqual(1, page.order)

    def test_delete_middle_page(self):
        challenge = Challenge.objects.create(pk=1, name='fire', description='hot')
        page1 = ContentPage.objects.create(pk=1, challenge=challenge, order=1)
        page2 = ContentPage.objects.create(pk=2, challenge=challenge, order=2)
        page3 = ContentPage.objects.create(pk=3, challenge=challenge, order=3)
        page4 = ContentPage.objects.create(pk=4, challenge=challenge, order=4)

        url = reverse('page_delete', kwargs={'challenge': 1, 'pk': page2.pk})
        response = self.client.post(url, {})
        self.assertEqual(200, response.status_code)

        self.assertEqual(3, ContentPage.objects.count())
        pages = ContentPage.objects.order_by('pk')
        self.assertEqual(1, pages[0].order)
        self.assertEqual(2, pages[1].order)
        self.assertEqual(3, pages[2].order)

    def test_delete_last_page(self):
        challenge = Challenge.objects.create(pk=1, name='fire', description='hot')
        page1 = ContentPage.objects.create(pk=1, challenge=challenge, order=1)
        page2 = ContentPage.objects.create(pk=2, challenge=challenge, order=2)

        url = reverse('page_delete', kwargs={'challenge': 1, 'pk': page2.pk})
        response = self.client.post(url, {})
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, ContentPage.objects.count())
        page = ContentPage.objects.all()[0]
        self.assertEqual(1, page.order)

    def test_delete_page_with_video(self):
        challenge = Challenge.objects.create(pk=1, name='fire', description='hot')
        page = ContentPage.objects.create(pk=1, challenge=challenge, order=1)
        video = Video.objects.create(link='link', thumbnail='t', download='d')
        ContentSequenceItem.objects.create(content_object=video, content_page=page)
        self.assertEqual(1, ContentSequenceItem.objects.count())

        url = reverse('page_delete', kwargs={'challenge': 1, 'pk': page.pk})
        response = self.client.post(url, {})
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, Video.objects.count())
        self.assertEqual(0, ContentPage.objects.count())
        self.assertEqual(0, ContentSequenceItem.objects.count())

    def test_delete_page_with_text(self):
        challenge = Challenge.objects.create(pk=1, name='fire', description='hot')
        page = ContentPage.objects.create(pk=1, challenge=challenge, order=1)
        text = TextBlock.objects.create(text='text')
        ContentSequenceItem.objects.create(content_object=text, content_page=page)
        self.assertEqual(1, ContentSequenceItem.objects.count())

        url = reverse('page_delete', kwargs={'challenge': 1, 'pk': page.pk})
        response = self.client.post(url, {})
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, ContentPage.objects.count())
        self.assertEqual(0, ContentSequenceItem.objects.count())
        self.assertEqual(0, TextBlock.objects.count())

    def test_delete_page_with_problem(self):
        challenge = Challenge.objects.create(pk=1, name='fire', description='hot')
        page = ContentPage.objects.create(pk=1, challenge=challenge, order=1)
        problem = Problem.objects.create(description='mc')
        ContentSequenceItem.objects.create(content_object=problem, content_page=page)
        self.assertEqual(1, ContentSequenceItem.objects.count())

        url = reverse('page_delete', kwargs={'challenge': 1, 'pk': page.pk})
        response = self.client.post(url, {})
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, Problem.objects.count())
        self.assertEqual(0, ContentPage.objects.count())
        self.assertEqual(0, ContentSequenceItem.objects.count())
