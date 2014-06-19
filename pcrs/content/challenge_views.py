from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.detail import SingleObjectMixin

from content.forms import ChallengeForm
from content.models import *
from pcrs.generic_views import GenericItemListView, GenericItemCreateView, \
    GenericItemUpdateView
from users.views_mixins import ProtectedViewMixin, CourseStaffViewMixin
from problems.forms import ProgrammingSubmissionForm
from problems_multiple_choice.forms import SubmissionForm


class ChallengeView:
    model = Challenge
    form_class = ChallengeForm
    template_name = 'pcrs/item_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()


class ChallengeListView(CourseStaffViewMixin, GenericItemListView):
    model = Challenge
    template_name = 'content/challenge_list.html'


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


class ChallengeStartView(ProtectedViewMixin, DetailView):
    model = Challenge
    template_name = 'content/challenge.html'


class ContentPageView(ProtectedViewMixin, ListView, SingleObjectMixin):
    template_name = "content/content_page.html"
    model = ContentSequenceItem
    object = None

    def get_queryset(self):
        return self.model.objects\
            .filter(content_page=self.object)\
            .prefetch_related('content_object').all()

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
        context['content_page'] = self.object
        context['forms'] = self._get_forms()
        context['best'] = {
            content_type.app_label: content_type.model_class()
                    .get_best_attempts_before_deadlines(self.request.user)
            for content_type in ContentType.objects.filter(Q(model='submission'))
        }
        context['watched'] = WatchedVideo.get_watched_pk_list(self.request.user)
        return context