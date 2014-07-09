import json
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.utils.timezone import localtime, now

from content.forms import ChallengeForm
from content.models import *
from pcrs.generic_views import (GenericItemListView, GenericItemCreateView,
                                GenericItemUpdateView)
from problems.models import get_submission_content_types, \
    get_problem_content_types
from users.section_views import SectionViewMixin
from users.views_mixins import ProtectedViewMixin, CourseStaffViewMixin
from problems.forms import ProgrammingSubmissionForm
from problems_multiple_choice.forms import SubmissionForm


class IncompletePrerequisites(Exception):
    pass


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
        if section.is_master():
            return Challenge.objects.all()
        else:
            return Challenge.objects.filter(
                visibility='open',
                quest__sectionquest__section=section,
                quest__sectionquest__open_on__lt=localtime(now()),
                quest__sectionquest__visibility='open')

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


class ContentPageView(ProtectedViewMixin, SectionViewMixin, ListView):
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
            self.queryset = self.model.objects\
                .filter(content_page=self.get_page())\
                .prefetch_related('content_object').all()
        return self.queryset

    def _get_forms(self):
        forms = {}
        for item in self.get_queryset():
            classname = item.content_object.__class__.__name__
            if classname == 'Problem':
                problem = item.content_object
                # generate a submission form for this problem
                # based on the problem class
                module, _ = item.content_object.__module__.split('.')
                f = SubmissionForm(problem=problem) \
                    if module.endswith('multiple_choice') \
                    else ProgrammingSubmissionForm(problem=problem)
                try:
                    forms[module][problem.pk] = f
                except:
                    forms[module] = {}
                    forms[module][problem.pk] = f
        return forms

    def _check_prerequisites(self, challenge, problem_to_completed):
        """
        Check that every problem in challenge has been completed.
        """
        if self.get_section().is_master():
            return
        required = {
            (p.content_type.app_label, p.object_id)
            for p in ContentSequenceItem.objects
            .filter(content_type__name='problem',
            content_page__challenge__in=challenge.prerequisites.all())
            .select_related('content_type')
        }
        actual = {
            (p_type, pk)
            for p_type, problems in problem_to_completed.items()
            for pk, user_completed in problems.items() if user_completed
        }
        if not required.issubset(actual):
            raise IncompletePrerequisites()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['content_page'] = self.page

        context['best'], type_to_completed_status = {}, {}
        for content_type in get_submission_content_types():
            best, completed = content_type.model_class()\
                .get_best_attempts_before_deadlines(self.request.user, self.get_section())
            context['best'][content_type.app_label] = best
            type_to_completed_status[content_type.app_label] = completed

        if self.page.challenge.enforce_prerequisites:
            self._check_prerequisites(
                self.page.challenge, type_to_completed_status)

        context['next'] = self.page.next()
        context['num_pages'] = self.page.challenge.contentpage_set.count()
        context['forms'] = self._get_forms()
        context['watched'] = WatchedVideo.get_watched_pk_list(self.request.user)
        return context

    def get(self, request, *args, **kwargs):
        try:
            self.object_list = self.get_queryset()
            context = self.get_context_data(object_list=self.object_list)
            return self.render_to_response(context)
        except IncompletePrerequisites as e:
            return redirect('challenge_missing_prerequisites',
                            pk=self.page.challenge.pk)


class IncompletePrerequisitesView(ProtectedViewMixin, TemplateView):
    """
    A view to notify the user that they have not completed some prerequisite
    for a Challenge that enforces prerequisites.
    """
    template_name = 'content/missing_prerequisited.html'


class ChallengeStatsView(CourseStaffViewMixin, DetailView):
    """
    View the graph displaying the numbers of students who did not attemt,
    attempted, or completed the Challenge.
    """
    model = Challenge
    template_name = 'content/challenge_stats.html'


class ChallengeStatsGetData(CourseStaffViewMixin, SectionViewMixin, DetailView):
    """
    Asynchronous data request for getting the data for ChallengeStatsView.
    """
    model = Challenge

    def get_attempt_stats(self, challenge, section):
        results, max_scores = defaultdict(dict), defaultdict(dict)
        completed = 0
        for ctype in get_problem_content_types():
            for problem in ctype.model_class().objects\
                    .filter(challenge=challenge).order_by('id'):
                max_scores[(ctype.app_label, problem.pk)] = problem.max_score

        for ctype in get_submission_content_types():
            grades = ctype.model_class().get_scores_for_challenge(
                challenge=challenge, section=section)
            for record in grades:
                problem = (ctype.app_label,
                           record['problem'])
                results[record['user']][problem] = record['best']

        for student_id, score_dict in results.items():
            if score_dict == max_scores:
                completed += 1

        attempted = len(results) - completed
        did_not_attempt = PCRSUser.objects.get_students()\
                              .filter(section=section).count() - attempted

        return did_not_attempt, attempted, completed

    def get(self, request, *args, **kwargs):
        results = self.get_attempt_stats(
            challenge=self.get_object(), section=self.get_section())
        return HttpResponse(json.dumps({'status': 'ok', 'results': results}),
                                mimetype='application/json')