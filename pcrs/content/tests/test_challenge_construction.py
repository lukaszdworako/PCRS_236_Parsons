import json
from django.core.urlresolvers import reverse
from django.test import TestCase

from content.models import Challenge, ContentPage, Video, ContentSequenceItem, \
    TextBlock
from problems_multiple_choice.models import Problem
from problems_code.models import Problem as CodeProblem
from ViewTestMixins import UsersMixin


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
        ContentPage.objects.create(challenge=challenge, order=1)

        response = self.client.post(self.url, {})
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, ContentPage.objects.count())
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


class TestPageConstruction(UsersMixin, TestCase):
    """
    Test deleting challenge pages.
    """

    url = reverse('page_manage_objects', kwargs={'pk': 1})

    def setUp(self):
        UsersMixin.setUp(self)
        self.challenge = Challenge.objects.create(
            pk=1, name='fire', description='hot')
        self.client.login(username='instructor')

    def test_add_item_to_only_page(self):
        ContentPage.objects.create(pk=1, challenge=self.challenge, order=1)
        TextBlock.objects.create(pk=1, text='text')

        post_data = {'page_object_list': json.dumps([
            ['textblock-1']
        ])}
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        page = ContentPage.objects.get(pk=1)
        self.assertEqual(1, page.contentsequenceitem_set.count())
        item = page.contentsequenceitem_set.all()[0]
        self.assertEqual(1, item.object_id)
        self.assertEqual('text block', str(item.content_type))
        self.assertEqual(0, item.order)

    def test_add_item_to_middle_page(self):
        ContentPage.objects.create(pk=1, challenge=self.challenge, order=1)
        ContentPage.objects.create(pk=2, challenge=self.challenge, order=2)
        ContentPage.objects.create(pk=3, challenge=self.challenge, order=3)
        TextBlock.objects.create(pk=1, text='text')

        post_data = {'page_object_list': json.dumps([
            [], ['textblock-1'], []
        ])}
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        page = ContentPage.objects.get(pk=2)
        self.assertEqual(1, page.contentsequenceitem_set.count())
        item = page.contentsequenceitem_set.all()[0]
        self.assertEqual(1, item.object_id)
        self.assertEqual('text block', str(item.content_type))
        self.assertEqual(0, item.order)

    def test_add_multiple_items(self):
        ContentPage.objects.create(pk=1, challenge=self.challenge, order=1)
        TextBlock.objects.create(pk=1, text='text')
        TextBlock.objects.create(pk=2, text='text')
        TextBlock.objects.create(pk=3, text='text')

        post_data = {'page_object_list': json.dumps([
            ['textblock-1', 'textblock-3', 'textblock-2']
        ])}
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        page = ContentPage.objects.get(pk=1)
        self.assertEqual(3, page.contentsequenceitem_set.count())

        item1, item2, item3 = page.contentsequenceitem_set.order_by('order').all()
        self.assertEqual(1, item1.object_id)
        self.assertEqual(0, item1.order)
        self.assertEqual(3, item2.object_id)
        self.assertEqual(1, item2.order)
        self.assertEqual(2, item3.object_id)
        self.assertEqual(2, item3.order)

    def test_remove_only_item(self):
        page = ContentPage.objects.create(pk=1, challenge=self.challenge, order=1)
        text = TextBlock.objects.create(pk=1, text='text')
        ContentSequenceItem.objects.create(content_object=text, content_page=page)
        self.assertEqual(1, ContentPage.objects.get(pk=1)
            .contentsequenceitem_set.count())

        post_data = {'page_object_list': json.dumps([
            []
        ])}
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, ContentPage.objects.get(pk=1)
            .contentsequenceitem_set.count())

    def test_remove_item_from_middle(self):
        page = ContentPage.objects.create(pk=1, challenge=self.challenge, order=1)
        for i in [1, 2, 3]:
            text = TextBlock.objects.create(pk=i, text='text')
            ContentSequenceItem.objects.create(content_object=text,
                                               content_page=page, order=i)
        self.assertEqual(3, ContentPage.objects.get(pk=1)
            .contentsequenceitem_set.count())

        post_data = {'page_object_list': json.dumps([
            ['textblock-1', 'textblock-2']
        ])}
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, ContentPage.objects.get(pk=1)
            .contentsequenceitem_set.count())
        self.assertEqual(2, ContentSequenceItem.objects.count())
        item1, item2 = ContentPage.objects.get(pk=1).contentsequenceitem_set\
            .all().order_by('order')
        self.assertEqual(1, item1.object_id)
        self.assertEqual(0, item1.order)
        self.assertEqual(2, item2.object_id)
        self.assertEqual(1, item2.order)
        # dangling text object was cleaned up
        self.assertEqual(2, TextBlock.objects.count())

    def test_reorder_items(self):
        page = ContentPage.objects.create(pk=1, challenge=self.challenge, order=1)
        for i in [1, 2, 3]:
            text = TextBlock.objects.create(pk=i, text='text')
            ContentSequenceItem.objects.create(content_object=text,
                                               content_page=page, order=i)
        self.assertEqual(3, ContentPage.objects.get(pk=1)
            .contentsequenceitem_set.count())

        post_data = {'page_object_list': json.dumps([
            ['textblock-2', 'textblock-1', 'textblock-3']
        ])}
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(3, ContentPage.objects.get(pk=1)
            .contentsequenceitem_set.count())
        item1, item2, item3 = ContentSequenceItem.objects.order_by('id')

        self.assertEqual(1, item1.object_id)
        self.assertEqual(1, item1.order)

        self.assertEqual(2, item2.object_id)
        self.assertEqual(0, item2.order)

        self.assertEqual(3, item3.object_id)
        self.assertEqual(2, item3.order)

    def test_move_items(self):
        page = ContentPage.objects.create(pk=1, challenge=self.challenge, order=1)
        page2 = ContentPage.objects.create(pk=2, challenge=self.challenge, order=2)
        for i in [1, 2, 3]:
            text = TextBlock.objects.create(pk=i, text='text')
            ContentSequenceItem.objects.create(content_object=text,
                                               content_page=page, order=i)
        self.assertEqual(3, ContentPage.objects.get(pk=1)
            .contentsequenceitem_set.count())

        post_data = {'page_object_list': json.dumps([
            ['textblock-2'], ['textblock-1', 'textblock-3']
        ])}
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, ContentPage.objects.get(pk=1)
            .contentsequenceitem_set.count())
        self.assertEqual(2, ContentPage.objects.get(pk=2)
            .contentsequenceitem_set.count())
        self.assertEqual(3, ContentSequenceItem.objects.count())

        item1, item2, item3 = ContentSequenceItem.objects.order_by('id')

        self.assertEqual(2, item2.object_id)
        self.assertEqual(0, item2.order)
        self.assertEqual(1, item2.content_page.pk)

        self.assertEqual(1, item1.object_id)
        self.assertEqual(0, item1.order)
        self.assertEqual(2, item1.content_page.pk)

        self.assertEqual(3, item3.object_id)
        self.assertEqual(1, item3.order)
        self.assertEqual(2, item3.content_page.pk)

    def test_add_problem(self):
        ContentPage.objects.create(pk=1, challenge=self.challenge, order=1)
        Problem.objects.create(pk=1, name='name', description='d')
        Problem.objects.create(pk=2, name='name2', description='d2')

        post_data = {'page_object_list': json.dumps([
            ['problems_multiple_choice-1']
        ])}
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        page = ContentPage.objects.get(pk=1)
        self.assertEqual(1, page.contentsequenceitem_set.count())
        item = page.contentsequenceitem_set.all()[0]
        self.assertEqual(1, item.object_id)
        self.assertEqual(0, item.order)
        self.assertEqual(1, item.content_page.pk)
        self.assertEqual(self.challenge, item.content_object.challenge)
        self.assertIsNone(Problem.objects.get(pk=2).challenge)

    def test_add_problems(self):
        ContentPage.objects.create(pk=1, challenge=self.challenge, order=1)
        Problem.objects.create(pk=1, name='name', description='d')
        Problem.objects.create(pk=2, name='name2', description='d2')

        post_data = {'page_object_list': json.dumps([
            ['problems_multiple_choice-2', 'problems_multiple_choice-1']
        ])}
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        page = ContentPage.objects.get(pk=1)
        self.assertEqual(2, page.contentsequenceitem_set.count())
        item1, item2 = page.contentsequenceitem_set.all().order_by('order')

        self.assertEqual(2, item1.object_id)
        self.assertEqual(0, item1.order)
        self.assertEqual(1, item1.content_page.pk)
        self.assertEqual(self.challenge, item1.content_object.challenge)

        self.assertEqual(1, item2.object_id)
        self.assertEqual(1, item2.order)
        self.assertEqual(1, item2.content_page.pk)
        self.assertEqual(self.challenge, item2.content_object.challenge)

    def test_add_problems_to_multiple_pages(self):
        ContentPage.objects.create(pk=1, challenge=self.challenge, order=1)
        ContentPage.objects.create(pk=2, challenge=self.challenge, order=2)
        Problem.objects.create(pk=1, name='name', description='d')
        Problem.objects.create(pk=2, name='name2', description='d2')
        Problem.objects.create(pk=3, name='name3', description='d3')

        post_data = {'page_object_list': json.dumps([
            ['problems_multiple_choice-2', 'problems_multiple_choice-1'],
            ['problems_multiple_choice-3']
        ])}
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(2,
            ContentPage.objects.get(pk=1).contentsequenceitem_set.count())
        self.assertEqual(1,
            ContentPage.objects.get(pk=2).contentsequenceitem_set.count())
        item1, item2, item3 = ContentSequenceItem.objects\
            .order_by('content_page', 'order')

        self.assertEqual(2, item1.object_id)
        self.assertEqual(0, item1.order)
        self.assertEqual(1, item1.content_page.pk)
        self.assertEqual(self.challenge, item1.content_object.challenge)

        self.assertEqual(1, item2.object_id)
        self.assertEqual(1, item2.order)
        self.assertEqual(1, item2.content_page.pk)
        self.assertEqual(self.challenge, item2.content_object.challenge)

        self.assertEqual(3, item3.object_id)
        self.assertEqual(0, item3.order)
        self.assertEqual(2, item3.content_page.pk)
        self.assertEqual(self.challenge, item3.content_object.challenge)

    def test_move_problem(self):
        page = ContentPage.objects.create(pk=1, challenge=self.challenge, order=1)
        page2 = ContentPage.objects.create(pk=2, challenge=self.challenge, order=2)
        for i in [1, 2, 3]:
            problem = Problem.objects.create(pk=i, name=str(i), description=str(i))
            ContentSequenceItem.objects.create(content_object=problem,
                                               content_page=page, order=i)
        self.assertEqual(3, ContentPage.objects.get(pk=1)
            .contentsequenceitem_set.count())

        post_data = {'page_object_list': json.dumps([
            ['problems_multiple_choice-2', 'problems_multiple_choice-1'],
            ['problems_multiple_choice-3']
        ])}
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(2,
            ContentPage.objects.get(pk=1).contentsequenceitem_set.count())
        self.assertEqual(1,
            ContentPage.objects.get(pk=2).contentsequenceitem_set.count())
        item1, item2, item3 = ContentSequenceItem.objects\
            .order_by('content_page', 'order')

        self.assertEqual(2, item1.object_id)
        self.assertEqual(0, item1.order)
        self.assertEqual(1, item1.content_page.pk)
        self.assertEqual(self.challenge, item1.content_object.challenge)

        self.assertEqual(1, item2.object_id)
        self.assertEqual(1, item2.order)
        self.assertEqual(1, item2.content_page.pk)
        self.assertEqual(self.challenge, item2.content_object.challenge)

        self.assertEqual(3, item3.object_id)
        self.assertEqual(0, item3.order)
        self.assertEqual(2, item3.content_page.pk)
        self.assertEqual(self.challenge, item3.content_object.challenge)

    def test_add_problems_many_types(self):
        page = ContentPage.objects.create(pk=1, challenge=self.challenge, order=1)

        Problem.objects.create(pk=1, name='1', description='1')
        CodeProblem.objects.create(pk=1, name='1', description='1')

        post_data = {'page_object_list': json.dumps([
            ['problems_multiple_choice-1', 'problems_code-1'],
        ])}
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(2,
            ContentPage.objects.get(pk=1).contentsequenceitem_set.count())

        item1, item2 = ContentSequenceItem.objects\
            .order_by('content_page', 'order')

        self.assertEqual(1, item1.object_id)
        self.assertEqual(0, item1.order)
        self.assertEqual(1, item1.content_page.pk)
        self.assertEqual(self.challenge, item1.content_object.challenge)
        self.assertEqual('problems_multiple_choice',
            item1.content_object.get_app_label())

        self.assertEqual(1, item2.object_id)
        self.assertEqual(1, item2.order)
        self.assertEqual(1, item2.content_page.pk)
        self.assertEqual(self.challenge, item2.content_object.challenge)
        self.assertEqual('problems_code', item2.content_object.get_app_label())

    def test_remove_problem(self):
        page = ContentPage.objects.create(pk=1, challenge=self.challenge, order=1)
        page2 = ContentPage.objects.create(pk=2, challenge=self.challenge, order=2)
        for i in [1, 2, 3]:
            problem = Problem.objects.create(pk=i, name=str(i), description=str(i))
            ContentSequenceItem.objects.create(content_object=problem,
                                               content_page=page, order=i)
        self.assertEqual(3, ContentPage.objects.get(pk=1)
            .contentsequenceitem_set.count())

        post_data = {'page_object_list': json.dumps([
            ['problems_multiple_choice-2'],
            ['problems_multiple_choice-3']
        ])}
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, ContentPage.objects.count())

        self.assertEqual(1,
            ContentPage.objects.get(pk=1).contentsequenceitem_set.count())
        self.assertEqual(1,
            ContentPage.objects.get(pk=2).contentsequenceitem_set.count())
        item1, item2 = ContentSequenceItem.objects\
            .order_by('content_page', 'order')

        self.assertEqual(2, item1.object_id)
        self.assertEqual(0, item1.order)
        self.assertEqual(1, item1.content_page.pk)
        self.assertEqual(self.challenge, item1.content_object.challenge)

        self.assertEqual(3, item2.object_id)
        self.assertEqual(0, item2.order)
        self.assertEqual(2, item2.content_page.pk)
        self.assertEqual(self.challenge, item2.content_object.challenge)

        problem = Problem.objects.get(pk=1)
        self.assertIsNone(problem.challenge)