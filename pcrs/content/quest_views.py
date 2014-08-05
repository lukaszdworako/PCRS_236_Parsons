from collections import defaultdict
import json

from django.forms.models import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views.generic import CreateView, FormView, ListView, View, \
    TemplateView

from content.forms import QuestForm, QuestSectionForm
from content.models import Quest, SectionQuest, Challenge, WatchedVideo, \
    ContentPage, ContentSequenceItem
from pcrs.generic_views import (GenericItemListView, GenericItemCreateView,
                                GenericItemUpdateView)
from pcrs.models import get_problem_content_types
from users.models import Section
from users.views import UserViewMixin
from users.views_mixins import CourseStaffViewMixin, ProtectedViewMixin


class QuestView:
    model = Quest
    form_class = QuestForm
    template_name = 'pcrs/item_form.html'

    def get_success_url(self):
        return '{}/list'.format(self.object.get_base_url())


class QuestListView(CourseStaffViewMixin, GenericItemListView):
    """
    Manage Challenges within Quests.
    """
    model = Quest
    template_name = 'content/quest_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['challenges'] = Challenge.objects.filter(quest__isnull=True)
        return context


class QuestCreateView(CourseStaffViewMixin, QuestView, GenericItemCreateView):
    """
    Create a new Quest.
    """


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
        Challenge.objects.update(quest=None, order=0)

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


class QuestSectionListView(CourseStaffViewMixin, FormView):
    """
    Update the attributes of Quest for a Section.
    """
    model = Section
    form_class = inlineformset_factory(Section, SectionQuest,
        form=QuestSectionForm,
        extra=0, can_delete=False)
    template_name = 'content/section_quest_list.html'

    def get_section(self):
        return get_object_or_404(Section, pk=self.kwargs.get('section'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quests'] = {q.pk: q for q in Quest.objects.all()}
        context['section'] = self.get_section()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': self.get_section()})
        return kwargs

    def get_success_url(self):
        return '{section}/list'.format(section=Section.get_base_url())

    def post(self, request, *args, **kwargs):
        formset = self.form_class(request.POST, instance=self.get_section())
        if formset.is_valid():
            formset.save()
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)


class QuestsView(ProtectedViewMixin, UserViewMixin, ListView):
    """
    List all available Quests and their Challenges for the user in the section.
    """
    template_name = "content/quests.html"
    model = Quest

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user, section = self.get_user(), self.get_section()
        context.update(Challenge.get_challenge_problem_data(user, section))

        # 1 query
        context['watched'] = WatchedVideo.get_watched_pk_list(user)

        # 2 queries
        context['challenges'] = {
            q.pk: q.challenge_set.all()  # .order_by('order')
            for q in Quest.objects.prefetch_related('challenge_set').all()
        }

        # 2 queries
        context['pages'] = {
            c.pk: c.contentpage_set.all()
            for c in Challenge.objects.all().prefetch_related('contentpage_set')
        }

        # 2 queries
        context['items'] = {
            page.pk: page.contentsequenceitem_set.all()
            for page in ContentPage.objects.prefetch_related(
            'contentsequenceitem_set').all()
        }

        # 2 queries
        context['content_objects'] = {
            item.pk: item.content_object
            for item in
            ContentSequenceItem.objects.prefetch_related('content_object').all()
        }

        return context

    def get_queryset(self):
        return SectionQuest.objects \
            .filter(section=self.get_section()) \
            .filter(visibility='open', open_on__lt=now()) \
            .select_related('quest')


class QuestsViewLive(ProtectedViewMixin, TemplateView):
    template_name = "content/quests_live.html"


class QuestsViewLiveQuestData(ProtectedViewMixin, View, UserViewMixin):
    def get(self, request, *args, **kwargs):
        user, section = self.get_user(), self.get_section()
        data = {
            'quests':  [],
            'challenges': defaultdict(list),
            'pages':  defaultdict(list),
            'problem_lists': defaultdict(list),
            'problems': defaultdict(dict),
            'problems_attempted': defaultdict(dict),
            'problems_completed': defaultdict(dict),
        }
        # 1
        quests = SectionQuest.objects \
            .filter(section=self.get_section()) \
            .filter(visibility='open', open_on__lt=now()) \
            .select_related('quest')
        data['quests'] = [
            {
                'pk': quest.quest.pk,
                'name': quest.quest.name,
                'deadline': quest.due_on.isoformat() if quest.due_on else None
            }
            for quest in quests]

        # 1
        for c in Challenge.objects.all():
            data['challenges'][c.quest_id].append(
                {'pk': c.pk, 'name': c.name, 'graded': c.is_graded})

        # 1
        for p in ContentPage.objects.all():
            data['pages'][p.challenge_id].append({'pk': p.pk, 'order': p.order})

        # 2
        for item in ContentSequenceItem.objects.prefetch_related('content_object').all():
            ptype = item.content_type.model_class().get_problem_type_name()
            pk = item.object_id
            problem_id = '{ptype}-{pk}'.format(pk=pk, ptype=ptype)
            data['problem_lists'][item.content_page_id].append(problem_id)
            data['problems'][ptype][pk] = item.content_object.serialize()

        info = Challenge.get_challenge_problem_data(user, section)
        data['challenge_to_completed'] = info['challenge_to_completed']
        data['challenge_to_total'] = info['challenge_to_total']

        for key, d in info['best'].items():
            _, ptype = key.split('problems_')
            for problem, score in d.items():
                data['problems_attempted'][ptype][problem] = True

        for key, d in info['problems_completed'].items():
            _, ptype = key.split('problems_')
            for problem, status in d.items():
                data['problems_completed'][ptype][problem] = status

        return HttpResponse(json.dumps(data))