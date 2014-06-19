import json
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.timezone import now
from django.views.generic import CreateView, FormView, ListView

from content.forms import QuestForm, QuestSectionForm
from content.models import Quest, SectionQuest, Challenge, WatchedVideo
from pcrs.generic_views import (GenericItemListView, GenericItemCreateView,
                                GenericItemUpdateView)
from users.models import Section
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


class QuestsView(ProtectedViewMixin, ListView):
    """
    List all available Quests and their Challenges for the user in the section.
    """
    template_name = "content/quests.html"
    model = SectionQuest

    @classmethod
    def sum_dict_values(cls, *args):
        total = {}
        for arg in args:
            for key, value in arg.items():
                existing = total.get(key, 0)
                new = existing + value
                total[key] = new
        return total

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        challenge_to_total, challenge_to_completed = [], []
        best = {}

        for content_type in ContentType.objects.filter(Q(model='problem')):
            problem_class = content_type.model_class()
            submission_class = problem_class.get_submission_class()
            challenge_to_total = problem_class.get_challenge_to_problem_number()
            challenge_to_completed.append(
                submission_class.get_completed_for_challenge_before_deadline(self.request.user))

            best[content_type.app_label] = submission_class\
                .get_best_attempts_before_deadlines(self.request.user)

        context['watched'] = WatchedVideo.get_watched_pk_list(self.request.user)
        context['best'] = best
        context['challenge_to_completed'] = self.sum_dict_values(*challenge_to_completed)
        context['challenge_to_total'] = self.sum_dict_values(*challenge_to_total)

        return context

    def get_queryset(self):
        section = (self.request.session.get('section', None) or
                   self.request.user.section)
        return SectionQuest.objects\
            .filter(visibility='open', section=section, open_on__lt=now())\
            .prefetch_related('quest', 'quest__challenge_set')