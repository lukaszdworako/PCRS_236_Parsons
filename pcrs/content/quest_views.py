import json
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import CreateView

from content.forms import QuestForm
from content.models import Quest, SectionQuest, Challenge
from pcrs.generic_views import (GenericItemListView, GenericItemCreateView,
                                GenericItemUpdateView)
from users.models import Section
from users.views_mixins import CourseStaffViewMixin


class QuestView:
    model = Quest
    form_class = QuestForm
    template_name = 'pcrs/item_form.html'

    def get_success_url(self):
            return '{}/list'.format(self.object.get_base_url())


class QuestListView(CourseStaffViewMixin, GenericItemListView):
    model = Quest
    template_name = 'content/quest_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['challenges'] = Challenge.objects.filter(quest__isnull=True)
        return context


class QuestCreateView(CourseStaffViewMixin, QuestView, GenericItemCreateView):
    """
    Create a new Quest, its and add it to all Sections.
    """

    def form_valid(self, form):
        self.object = form.save()
        for section in Section.objects.all():
            SectionQuest.objects.create(quest=self.object, section=section)
        return redirect(self.get_success_url())


class QuestUpdateView(CourseStaffViewMixin, QuestView, GenericItemUpdateView):
    """
    Update a Quest.
    """


class QuestSaveChallengesView(CourseStaffViewMixin, CreateView):
    """
    Record the Challenges in the Quests, and their order.
    """
    def post(self, request, *args, **kwargs):
        quests = json.loads(request.POST.get('quests'))
        # destroy all quest-challenge relationships
        Challenge.objects.update(quest=None)
        for quest_id, quest_info in quests.items():
            quest = Quest.objects.get(pk=quest_id)

            quest.order = quest_info['order']
            quest.save()
            for i in range(len(quest_info['challenge_ids'])):
                challenge_id = quest_info['challenge_ids'][i]
                challenge = Challenge.objects.get(pk=challenge_id)
                challenge.quest = quest
                challenge.order = i
                challenge.save()
        return HttpResponse(json.dumps({'status': 'ok'}))