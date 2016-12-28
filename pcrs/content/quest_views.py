from collections import defaultdict
import json
from io import TextIOWrapper
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db import models, IntegrityError, DatabaseError, transaction
from django.contrib.contenttypes.models import ContentType
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import now, localtime
from django.views.generic import CreateView, FormView, ListView, View, DetailView, \
    TemplateView
from django.views.generic.detail import SingleObjectMixin
from content.forms import QuestForm, QuestSectionForm, QuestImportForm
from content.models import Quest, SectionQuest, Challenge, WatchedVideo, \
    ContentPage, ContentSequenceItem
from pcrs.generic_views import (GenericItemListView, GenericItemCreateView,
                                GenericItemUpdateView)
from pcrs.models import get_problem_content_types, get_problem_labels, \
    get_submission_content_types
from pcrs.settings import INSTALLED_PROBLEM_APPS
from users.models import Section, PCRSUser
from users.views import UserViewMixin
from users.views_mixins import CourseStaffViewMixin, ProtectedViewMixin

from .analytics_helper import QuestAnalyticsHelper

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


class QuestAnalyticsView(CourseStaffViewMixin, UserViewMixin,
        SingleObjectMixin, View):
    """
    Displays problem analytics for a given quest.
    """
    model = Quest
    template_name = 'content/quest_analytics.html'

    def get(self, request, *args, **kwargs):
        users = self._getActiveUsersInCurrentSection()
        quest = self.get_object()

        helper = QuestAnalyticsHelper(quest, users)
        return render(request, self.template_name, {
            'questName': quest.name,
            'userCount': len(users),
            'problems': helper.computeAllProblemInfo(),
        })

    def _getActiveUsersInCurrentSection(self):
        return PCRSUser.objects.filter(
            is_active=True,
            section=self.get_section()
        )


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
            for form in formset:
                form.save()
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
            q.pk: q.challenge_set.all()
            for q in Quest.objects.prefetch_related('challenge_set').all()
        }

        # 2 queries
        context['pages'] = {
            c.pk: c.contentpage_set.all()
            for c in Challenge.objects.prefetch_related('contentpage_set').all()
        }

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
        all_quests = SectionQuest.objects
        if not self.get_section().is_master():
            all_quests = all_quests.filter(section=self.get_section()) \
                                   .filter(visibility='open', open_on__lt=now())
        return all_quests.select_related('quest')


class ReactiveQuestsView(ProtectedViewMixin, TemplateView):
    """
    List all available Quests and their Challenges for the user in the section.

    Do live updates.
    """
    template_name = "content/quests_live.html"


class ReactiveQuestsDataView(ProtectedViewMixin, View, UserViewMixin):
    """
    Return the data required to generate a live-updated quests page.
    """
    def get(self, request, *args, **kwargs):
        user, section = self.get_user(), self.get_section()
        data = {
            'quests':  [],
            'challenges': defaultdict(list),
            'pages':  defaultdict(list),
            'item_lists': defaultdict(list),
            'items': {},
            'watched': WatchedVideo.get_watched_uri_ids(user),
            'scores': {}
        }
        # 1
        quests = SectionQuest.objects \
            .filter(section=self.get_section()) \
            .filter(visibility='open', open_on__lt=now()) \
            .select_related('quest')
        data['quests'] = [quest.serialize() for quest in quests]

        # 1
        for c in Challenge.objects.all():
            data['challenges'][c.quest_id].append(c.serialize())

        # 1
        for p in ContentPage.objects.all():
            data['pages'][p.challenge_id].append(p.serialize())

        # 2
        for item in ContentSequenceItem.objects.prefetch_related('content_object').all():
            id = item.content_object.get_uri_id()
            data['item_lists'][item.content_page_id].append(id)
            data['items'][id] = item.content_object.serialize()

        info = Challenge.get_challenge_problem_data(user, section)
        data['challenge_to_completed'] = info['challenge_to_completed']
        data['challenge_to_total'] = info['challenge_to_total']

        for content_type in get_submission_content_types():
            best, _ = content_type.model_class()\
                .get_best_attempts_before_deadlines(user, section)
            data['scores'][content_type.app_label.replace('problems_', '')] = best

        return HttpResponse(json.dumps(data))

class QuestExportView(DetailView):
    template_name = 'content/quest_list.html'

    def post(self, request, pk):
        package = self.get_object().prepareJSON()
        json = serializers.serialize('json', package)
        response = HttpResponse(json, content_type="application/json")
        response["Content-Disposition"] = "attachment; filename={}.json".format(self.get_object().name)
        return response

class QuestImportView(FormView):
    form_class = QuestImportForm
    template_name = "content/import.html"

    def post(self, request):
        f = TextIOWrapper(request.FILES["json_file"].file, encoding='utf-8')
        with f as json_str:
            json_data = json.loads(r'{}'.format(json_str.read()))

        # Store foreign key field objects by pk
        pk_to_quest = {}
        pk_to_challenge = {}
        pk_to_contentpage = {}
        pk_to_contenttype = {}
        pk_to_problem = {}
        pk_to_video = {}
        pk_to_textblock = {}
        new_pk = {} # Store {old_pk:new_pk} pairs by content type id

        for item in json_data:
            model_field = item['model'].split('.')
            model = ContentType.objects.get(app_label=model_field[0], model=model_field[1]).model_class()
            # Replace foreign key integers in JSON with actual objects
            # and parse JSON according to model type
            old_fields = item["fields"].copy()
            for field in old_fields:
                if field not in [f.name for f in model._meta.fields]:
                    item["fields"].pop(field)
            if model_field[1]=="challenge":
                if len(pk_to_quest)==0: # If the challenge belongs to a quest
                    item["fields"].pop("prerequisites", None)
                    item["fields"].pop("quest", None)
                else:
                    item["fields"]["quest"] = pk_to_quest[item["fields"]["quest"]]
            if model_field[1]=="contentpage":
                item["fields"]["challenge"] = pk_to_challenge[item["fields"]["challenge"]]
            if model_field[1]=="problem":
                item["fields"]["challenge"] = pk_to_challenge[item["fields"]["challenge"]]
                if "max_score" in item["fields"]:
                    item["fields"].pop("max_score")
            if model_field[1]=="contentsequenceitem":
                item["fields"]["object_id"] = new_pk[item["fields"]["content_type"]][item["fields"]["object_id"]]
                item["fields"]["content_page"] = pk_to_contentpage[item["fields"]["content_page"]]
                item["fields"]["content_type"] = pk_to_contenttype[item["fields"]["content_type"]]
            if model_field[1] in ("testcase", "option"):
                item["fields"]["problem"] = pk_to_problem[item["fields"]["problem"]]
            # Get/create object from prepared JSON
            if model_field[1]=="contenttype":
                obj = model.objects.get(pk=item["pk"])
                pk_to_contenttype[item["pk"]] = obj
                if obj.pk not in new_pk:
                    new_pk[obj.pk] = {}
            else:
                try:
                    obj = model.objects.get_or_create(**item["fields"])[0]
                except IntegrityError as e:
                    # There may be existing problems that are not in any challenge,
                    # or existing challenges that are not in any quest
                    # If so, modify existing objects.
                    if model_field[1]=="problem":
                        fields_without_challenge = item["fields"].copy()
                        fields_without_challenge.pop("challenge", None)
                        obj = model.objects.get(**fields_without_challenge)
                        obj.challenge = pk_to_challenge[old_fields["challenge"]]
                        obj.save()
                    if model_field[1]=="challenge":
                        fields_without_quest = item["fields"].copy()
                        fields_without_quest.pop("quest", None)
                        obj = model.objects.get(**fields_without_quest)
                        obj.quest = pk_to_quest[old_fields["quest"]]
                        obj.save()
                except DatabaseError as e:
                    transaction.rollback_unless_managed()
                    try:
                        obj = model.objects.get_or_create(**item["fields"])[0]
                    except IntegrityError as e:
                        # There may already be identical problems that are not in any challenge
                        # If so, add the problem to the challenge.
                        if model_field[1]=="problem":
                            fields_without_challenge = item["fields"].copy()
                            fields_without_challenge.pop("challenge", None)
                            obj = model.objects.get(**fields_without_challenge)
                            obj.challenge = pk_to_challenge[old_fields["challenge"]]
                            obj.save()

            if model_field[1] in ("problem","video","textblock"):
                new_pk[obj.get_content_type_id()][item["pk"]] = obj.pk
            if model_field[1] == "problem":
                pk_to_problem[item["pk"]] = obj
            if model_field[1] == "challenge":
                pk_to_challenge[item["pk"]] = obj
            if model_field[1] == "contentpage":
                pk_to_contentpage[item["pk"]] = obj
            if model_field[1] == "quest":
                pk_to_quest[item["pk"]] = obj

        return HttpResponseRedirect('/')