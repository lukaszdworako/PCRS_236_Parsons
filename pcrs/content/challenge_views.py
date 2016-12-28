from collections import defaultdict
import json
import os
from django.http import HttpResponse
from django.views.generic import ListView, FormView, DetailView, View, TemplateView
from content.forms import ChallengeForm
from content.models import *
from pcrs.generic_views import (GenericItemListView, GenericItemCreateView,
                                GenericItemUpdateView)
from problems.models import get_submission_content_types, \
    get_problem_content_types
from users.section_views import SectionViewMixin
from users.views import UserViewMixin
from users.views_mixins import ProtectedViewMixin, CourseStaffViewMixin
from problems.forms import ProgrammingSubmissionForm
from problems_multiple_choice.forms import SubmissionForm as MCSubmissionForm
from problems_rating.forms import SubmissionForm as RatingSubmissionForm
from problems_short_answer.forms import SubmissionForm as ShortAnswerSubmissionForm
from django.core import serializers
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

class ChallengeView():
    model = Challenge
    form_class = ChallengeForm
    template_name = 'pcrs/item_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()


class ChallengeListView(CourseStaffViewMixin, SectionViewMixin,
                        GenericItemListView):
    """
    List all Challenges.
    """
    model = Challenge
    template_name = 'content/challenge_list.html'

    def get_visible_challenges(self):
        section = self.get_section()
        challenges = Challenge.objects.select_related('quest').all()
        if not section.is_master():
            challenges = challenges.filter(
                visibility='open',
                quest__sectionquest__section=section,
                quest__sectionquest__open_on__lt=localtime(now()),
                quest__sectionquest__visibility='open')
        return challenges

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['visible_challenges'] = set(self.get_visible_challenges()
                                            .values_list('id', flat=True))
        return context


class ChallengeCreateView(CourseStaffViewMixin, ChallengeView,
                          GenericItemCreateView):
    """
    Create a new Challenge, its ContentPages and ContentObjects.
    """


class ChallengeUpdateView(CourseStaffViewMixin, ChallengeView,
                          GenericItemUpdateView):
    """
    Update a new Challenge, its ContentPages and ContentObjects.
    """

class ContentPageView(ProtectedViewMixin, UserViewMixin, ListView):
    """
    View a ContentPage.
    """
    template_name = "content/content_page.html"
    model = ContentSequenceItem
    page = None
    queryset = None

    def get_page(self):
        if self.page is None:
            section = self.get_section()
            if section.is_master():
                page_set = ContentPage.objects.select_related('challenge')\

            else:
                page_set = ContentPage.objects.select_related('challenge')\
                    .filter(challenge__visibility='open',
                            challenge__quest__sectionquest__section=section,
                            challenge__quest__sectionquest__open_on__lt=localtime(now()),
                            challenge__quest__sectionquest__visibility='open',
                            challenge__quest__mode='live')
            self.page = page_set.get(
                order=self.kwargs.get('page', None),
                challenge_id=self.kwargs.get('challenge', None))
        return self.page

    def get_queryset(self):
        if self.queryset is None:
            try:
                self.queryset = self.model.objects\
                                    .filter(content_page=self.get_page())\
                                    .prefetch_related('content_object').all()
            except ContentPage.DoesNotExist:
                self.queryset = None
        return self.queryset

    def _get_forms(self):
        forms = defaultdict(dict)
        for item in self.get_queryset():
            classname = item.content_object.__class__.__name__
            if classname == 'Problem':
                problem = item.content_object
                # generate a submission form for this problem
                # based on the problem class
                module, _ = item.content_object.__module__.split('.')
                if module.endswith('multiple_choice'):
                    f = MCSubmissionForm(problem=problem, simpleui=self.request.user.use_simpleui)
                elif module.endswith('rating'):
                    f = RatingSubmissionForm(problem=problem, simpleui=self.request.user.use_simpleui)
                elif module.endswith('short_answer'):
                    f = ShortAnswerSubmissionForm(problem=problem, simpleui=self.request.user.use_simpleui)
                else:
                    f = ProgrammingSubmissionForm(problem=problem, simpleui=self.request.user.use_simpleui)
                forms[module][problem.pk] = f
        return forms

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user, section = self.get_user(), self.get_section()

        context['content_page'] = self.page
        context['best'] = {}

        for content_type in get_submission_content_types():
            best, _ = content_type.model_class()\
                .get_best_attempts_before_deadlines(user, section)
            context['best'][content_type.app_label] = best

        if self.page:
            context['next'] = self.page.next()
            context['num_pages'] = self.page.challenge.contentpage_set.count()
            context['forms'] = self._get_forms()
            context['watched'] = WatchedVideo.get_watched_pk_list(user)
        return context


class ReactiveContentPageView(ContentPageView):
    """
    View a ContentPage, in a mostly reactive way.
    """
    template_name = "content/reactive_content_page.html"
    model = ContentSequenceItem
    page = None
    queryset = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['content_page'] = self.page
        context['best'] = {}

        if self.page:
            context['next'] = self.page.next()
            context['num_pages'] = self.page.challenge.contentpage_set.count()
            context['forms'] = self._get_forms()
        return context


class ReactiveContentPageData(ContentPageView, View):
    """
    Return a JSON object with the data for a reactive content page.
    """
    def get(self, request, *args, **kwargs):
        user, section = self.get_user(), self.get_section()
        page = self.get_page()

        items = [
            item.content_object.serialize()
            for item in ContentSequenceItem.objects.filter(content_page=page)
                        .prefetch_related('content_object').all() if item and item.content_object
        ]

        scores = {}
        for content_type in get_submission_content_types():
            best, _ = content_type.model_class()\
                .get_best_attempts_before_deadlines(user, section)
            scores[content_type.app_label.replace('problems_', '')] = best

        return HttpResponse(
            json.dumps(
                {
                    'items': items,
                    'scores': scores,
                    'watched': WatchedVideo.get_watched_uri_ids(user),
                    'page': {'pk': page.pk, 'challenge': page.challenge_id},
                    'next_url': page.get_next_url(),
                    'prev_url': page.get_previous_url()
                }
            ), mimetype='application/json')


class ChallengeStatsView(CourseStaffViewMixin, DetailView):
    """
    View the graph displaying the numbers of students who did not attempt,
    attempted, or completed the Challenge.
    """
    model = Challenge
    template_name = 'content/challenge_stats.html'


class ChallengeStatsGetData(CourseStaffViewMixin, SectionViewMixin, DetailView):
    """
    Asynchronous data request for getting the data for ChallengeStatsView.
    """
    model = Challenge

    def get_attempt_stats(self, challenge, section, active_only=False):
        results, max_scores = defaultdict(dict), defaultdict(dict)
        completed = 0
        for ctype in get_problem_content_types():
            for problem in ctype.model_class().objects\
                    .filter(challenge=challenge).order_by('id'):
                max_scores[(ctype.app_label, problem.pk)] = problem.max_score

        for ctype in get_submission_content_types():
            grades = ctype.model_class().get_scores_for_challenge(
                challenge=challenge, section=section, active_only=active_only)
            for record in grades:
                problem = (ctype.app_label,
                           record['problem'])
                results[record['user']][problem] = record['best']

        for student_id, score_dict in results.items():
            if score_dict == max_scores:
                completed += 1

        attempted = len(results) - completed
        all_students = PCRSUser.objects.get_students(active_only)\
                                       .filter(section=section).count()
        did_not_attempt = all_students - attempted

        return did_not_attempt, attempted, completed

    def post(self, request, *args, **kwargs):
        active_only = request.POST.get('active_only', False)
        results = self.get_attempt_stats(
            self.get_object(), self.get_section(), active_only)
        return HttpResponse(json.dumps({'status': 'ok', 'results': results}),
                            mimetype='application/json')


class ChallengeCompletionForUserView(CourseStaffViewMixin, UserViewMixin,
                                     DetailView):
    """
    Asynchronous data request for getting the information about how many
    problems the user has completed in each Challenge, as we as the total
    number of problems in that Challenge.
    """
    model = Challenge

    def get(self, request, *args, **kwargs):
        user, section = self.get_user(), self.get_section()

        data = self.model.get_challenge_problem_data(user, section)

        return HttpResponse(json.dumps({
            challenge.pk: (
                    data['challenge_to_completed'].get(challenge.pk, 0),
                    data['challenge_to_total'].get(challenge.pk, 0)
            )
            for challenge in self.model.objects.all()
        }),  mimetype='application/json')


class ChallengeGraphView(ProtectedViewMixin, TemplateView):
    """
    View the challenge dependency graph.
    """
    template_name = 'content/challenge_graph.html'


class ChallengeGraphGenViewHorizontal(CourseStaffViewMixin, UserViewMixin, View):
    """
    Return the svg needed to display the horizontal dependency graph.
    """
    model = Challenge

    def get(self, request, *args, **kwargs):
        svg = os.path.join(os.getcwd(),
                           'resources/challenge_graph/ui/graph_gen_horizontal.svg')
        return HttpResponse(open(svg, 'r').read().replace('\\n', ''),
                            mimetype='text')


class ChallengeGraphGenViewVertical(CourseStaffViewMixin, UserViewMixin, View):
    """
    Return the svg needed to display the vertical dependency graph.
    """
    model = Challenge

    def get(self, request, *args, **kwargs):
        svg = os.path.join(os.getcwd(),
                           'resources/challenge_graph/ui/graph_gen_vertical.svg')
        return HttpResponse(open(svg, 'r').read().replace('\\n', ''),
                            mimetype='text')


class ChallengeExportView(DetailView):
    template_name = 'content/challenge_list.html'

    def post(self, request, pk):
        package = self.get_object().prepareJSON()
        json = serializers.serialize('json', package)
        response = HttpResponse(json, content_type="application/json")
        response["Content-Disposition"] = "attachment; filename={}.json".format(self.get_object().name)
        return response