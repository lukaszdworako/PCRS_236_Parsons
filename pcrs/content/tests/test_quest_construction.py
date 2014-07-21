import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from content.models import Quest, Challenge
from ViewTestMixins import UsersMixin


class TestQuestConstruction(UsersMixin, TestCase):
    """
    Test constructing Quests.
    """

    url = reverse('quest_list_save_challenges')

    def setUp(self):
        UsersMixin.setUp(self)
        self.client.login(username='instructor')

    def test_adding_challenge_to_empty_quest(self):
        Quest.objects.create(pk=1, name='Holy Grail',
            description='crusade', mode='live')
        Challenge.objects.create(pk=1, name='fire', description='hot')
        Challenge.objects.create(pk=2, name='water', description='cold')

        post_data = {
            'quests': json.dumps(
                {1: {'order': 0,
                     'challenge_ids': ['1']}
                })
        }

        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, Quest.objects.get(pk=1).challenge_set.count())
        self.assertEqual(1, Challenge.objects.get(pk=1).quest.pk)
        self.assertEqual(0, Challenge.objects.get(pk=1).order)
        self.assertIsNone(Challenge.objects.get(pk=2).quest)

    def test_adding_multiple_challenges_to_empty_quest(self):
        Quest.objects.create(pk=1, name='Holy Grail',
            description='crusade', mode='live')
        Challenge.objects.create(pk=1, name='fire', description='hot')
        Challenge.objects.create(pk=2, name='water', description='cold')
        Challenge.objects.create(pk=3, name='faith', description='invisible')

        post_data = {
            'quests': json.dumps(
                {1: {'order': 0,
                     'challenge_ids': ['1', '3']}
                })
        }

        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, Quest.objects.get(pk=1).challenge_set.count())
        self.assertEqual(1, Challenge.objects.get(pk=1).quest.pk)
        self.assertEqual(0, Challenge.objects.get(pk=1).order)

        self.assertEqual(1, Challenge.objects.get(pk=3).quest.pk)
        self.assertEqual(1, Challenge.objects.get(pk=3).order)

        self.assertIsNone(Challenge.objects.get(pk=2).quest)

    def test_removing_challenges_to_empty_quest(self):
        quest = Quest.objects.create(pk=1, name='Holy Grail',
            description='crusade', mode='live')
        Challenge.objects.create(pk=1, name='fire', description='hot',
            quest=quest)

        post_data = {
            'quests': json.dumps(
                {1: {'order': 0,
                     'challenge_ids': []}
                })
        }

        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, Quest.objects.get(pk=1).challenge_set.count())
        self.assertIsNone(Challenge.objects.get(pk=1).quest)

    def test_removing_challenge(self):
        quest = Quest.objects.create(pk=1, name='Holy Grail',
            description='crusade', mode='live')
        Challenge.objects.create(pk=1, name='fire', description='hot',
            quest=quest, order=0)
        Challenge.objects.create(pk=2, name='water', description='cold',
            quest=quest, order=1)
        Challenge.objects.create(pk=3, name='faith', description='hard',
            quest=quest, order=2)

        post_data = {
            'quests': json.dumps(
                {1: {'order': 0,
                     'challenge_ids': [1, 3]}
                })
        }

        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, Quest.objects.get(pk=1).challenge_set.count())
        self.assertEqual(1, Challenge.objects.get(pk=1).quest.pk)
        self.assertEqual(0, Challenge.objects.get(pk=1).order)
        self.assertEqual(1, Challenge.objects.get(pk=3).quest.pk)
        self.assertEqual(1, Challenge.objects.get(pk=3).order)
        self.assertIsNone(Challenge.objects.get(pk=2).quest)
        self.assertEqual(0, Challenge.objects.get(pk=2).order)

    def test_reorder_challenge(self):
        quest = Quest.objects.create(pk=1, name='Holy Grail',
            description='crusade', mode='live')
        Challenge.objects.create(pk=1, name='fire', description='hot',
            quest=quest, order=0)
        Challenge.objects.create(pk=2, name='water', description='cold',
            quest=quest, order=1)

        post_data = {
            'quests': json.dumps(
                {1: {'order': 0,
                     'challenge_ids': [2, 1]}
                })
        }

        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, Quest.objects.get(pk=1).challenge_set.count())
        self.assertEqual(1, Challenge.objects.get(pk=1).quest.pk)
        self.assertEqual(1, Challenge.objects.get(pk=1).order)
        self.assertEqual(1, Challenge.objects.get(pk=2).quest.pk)
        self.assertEqual(0, Challenge.objects.get(pk=2).order)

    def test_reorder_quests(self):
        quest1 = Quest.objects.create(pk=1, name='Holy Grail',
            description='crusade', mode='live', order=0)
        quest2 = Quest.objects.create(pk=2, name='Lost Arc',
            description='crusade', mode='live', order=1)

        post_data = {
            'quests': json.dumps(
                {
                    1: {'order': 1,
                        'challenge_ids': []},
                    2: {'order': 0,
                        'challenge_ids': []}

                },
            )
        }

        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, Quest.objects.get(pk=1).order)
        self.assertEqual(0, Quest.objects.get(pk=2).order)

    def test_move_challenge_between_quests(self):
        quest1 = Quest.objects.create(pk=1, name='Holy Grail',
            description='crusade', mode='live', order=0)
        quest2 = Quest.objects.create(pk=2, name='Lost Arc',
            description='crusade', mode='live', order=1)

        Challenge.objects.create(pk=1, name='fire', description='hot',
            quest=quest1, order=0)
        Challenge.objects.create(pk=2, name='water', description='cold',
            quest=quest2, order=1)

        post_data = {
            'quests': json.dumps(
                {
                    1: {'order': 0,
                        'challenge_ids': [1, 2]},
                    2: {'order': 1,
                        'challenge_ids': []}

                },
            )
        }

        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, Quest.objects.get(pk=1).order)
        self.assertEqual(1, Challenge.objects.get(pk=1).quest.pk)
        self.assertEqual(1, Quest.objects.get(pk=2).order)
        self.assertEqual(1, Challenge.objects.get(pk=2).quest.pk)
