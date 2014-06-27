from collections import defaultdict
import json
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.timezone import now
from django.views.generic import CreateView, FormView, ListView

from content.forms import QuestForm, QuestSectionForm
from content.models import Quest, SectionQuest, Challenge, WatchedVideo, \
    ContentPage, ContentSequenceItem
from pcrs.generic_views import (GenericItemListView, GenericItemCreateView,
                                GenericItemUpdateView)
from problems.models import get_problem_content_types
from users.models import Section
from users.section_views import SectionViewMixin
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


class QuestsView(ProtectedViewMixin, SectionViewMixin, ListView):
    """
    List all available Quests and their Challenges for the user in the section.
    """
    template_name = "content/quests.html"
    model = Quest

    @classmethod
    def sum_dict_values(cls, *args):
        total = {}
        for arg in args:
            for key, value in arg.items():
                existing = total.get(key, 0)
                new = existing + value
                total[key] = new
        return total

    @classmethod
    def get_completed_challenges(cls, completed, total):
        return {challenge.pk for challenge in Challenge.objects.all()
                if completed.get(challenge.pk, None) == total.get(challenge.pk, 0)}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        challenge_to_total, challenge_to_completed = [], []
        best = {}

        for content_type in get_problem_content_types():  # 1 query
            problem_class = content_type.model_class()
            submission_class = problem_class.get_submission_class()
            challenge_to_total.append(problem_class.get_challenge_to_problem_number())
            challenge_to_completed.append(
                submission_class.get_completed_for_challenge_before_deadline(self.request.user))

            best[content_type.app_label], _ = submission_class\
                .get_best_attempts_before_deadlines(self.request.user)
        context['watched'] = WatchedVideo.get_watched_pk_list(self.request.user)
        context['best'] = best
        context['challenge_to_completed'] = self.sum_dict_values(*challenge_to_completed)
        context['challenge_to_total'] = self.sum_dict_values(*challenge_to_total)
        context['challenges_completed'] = self.get_completed_challenges(
            context['challenge_to_completed'], context['challenge_to_total'])

        # 1 query
        context['watched'] = WatchedVideo.get_watched_pk_list(self.request.user)

        # 2 queries
        context['challenges'] = {
            q.pk: q.challenge_set.all() #.order_by('order')
            for q in Quest.objects.prefetch_related('challenge_set').all()
        }

        # 3 queries
        context['pages'], context['prerequisites'], context['prerequisites_set'] = {}, {}, {}
        for c in Challenge.objects.all().prefetch_related('contentpage_set', 'prerequisites'):
            context['pages'][c.pk] = c.contentpage_set.all()
            context['prerequisites_set'][c.pk] = c.get_prerequisite_pks_set()
            context['prerequisites'][c.pk] = c.prerequisites.all()

        # 2 queries
        context['items'] = {
            page.pk: page.contentsequenceitem_set.all()
            for page in ContentPage.objects.prefetch_related('contentsequenceitem_set').all()
        }

        # 2 queries
        context['content_objects'] = {
            item.pk: item.content_object
            for item in ContentSequenceItem.objects.prefetch_related('content_object').all()
        }

        return context

    def get_queryset(self):
        return SectionQuest.objects\
            .filter(section=self.get_section())\
            .filter(visibility='open', open_on__lt=now())\
            .select_related('quest')