from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.utils.timezone import localtime, now

from content.forms import ChallengeForm
from content.models import *
from pcrs.generic_views import (GenericItemListView, GenericItemCreateView,
                                GenericItemUpdateView)
from problems.models import get_submission_content_types
from users.section_views import SectionViewMixin
from users.views_mixins import ProtectedViewMixin, CourseStaffViewMixin
from problems.forms import ProgrammingSubmissionForm
from problems_multiple_choice.forms import SubmissionForm


class IncompletePrerequisites(Exception):
    pass


class PrerequisitesRequiredViewMixin:
    def check_prerequisites(self, challenge, problem_to_completed):
        if self.get_section().is_master:
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


class ChallengeView():
    model = Challenge
    form_class = ChallengeForm
    template_name = 'pcrs/item_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()


class ChallengeListView(CourseStaffViewMixin, SectionViewMixin,
                        GenericItemListView):
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


class ContentPageView(ProtectedViewMixin, SectionViewMixin, ListView,
                      PrerequisitesRequiredViewMixin):
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
                            challenge__quest__sectionquest__visibility='open')
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['content_page'] = self.page

        context['best'], type_to_completed_status = {}, {}
        for content_type in get_submission_content_types():
            best, completed = content_type.model_class()\
                .get_best_attempts_before_deadlines(self.request.user)
            context['best'][content_type.app_label] = best
            type_to_completed_status[content_type.app_label] = completed

        self.check_prerequisites(self.page.challenge, type_to_completed_status)
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
    template_name = 'content/missing_prerequisited.html'