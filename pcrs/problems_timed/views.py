import json
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views.generic import (CreateView, UpdateView, DeleteView, FormView)
from django.views.generic.detail import SingleObjectMixin

from problems_timed.models import Problem, Page, Submission
from problems_timed.forms import PageForm, SubmissionForm

from problems.views import ProblemListView, TestCaseView, SubmissionView, SubmissionViewMixin
from pcrs.generic_views import GenericItemCreateView

from users.views import UserViewMixin
from users.views_mixins import ProtectedViewMixin, CourseStaffViewMixin
from users.section_views import SectionViewMixin

class ProblemListView(ProblemListView):
    template_name = 'problems_timed/problem_list.html'

class ProblemCreateRedirectView(CourseStaffViewMixin, CreateView):
    model = Problem

    def get_success_url(self):
        return reverse('timed_add_page',
                       kwargs={'problem': self.object.pk})

class PageView(TestCaseView):
    model = Page
    form_class = PageForm
    template_name = 'problems_timed/page_form.html'
    object = None

    def get_success_url(self):
        return reverse('timed_add_page',
                       kwargs={'problem': self.object.problem.pk})

class PageCreateView(PageView, GenericItemCreateView):

    def get_success_url(self):
        return reverse('timed_update',
                       kwargs={'pk': self.object.problem.pk})

class PagesCreateView(PageView, GenericItemCreateView):
    pass

class PageUpdateView(PageView, UpdateView):
    template_name = 'problems_timed/page_update.html'
    
    def get_success_url(self):
        return reverse('timed_update',
                       kwargs={'pk': self.object.problem.pk})

class PageDeleteView(PageView, DeleteView):
    template_name = 'problems_timed/page_delete.html'

    def get_success_url(self):
        return reverse('timed_update',
                       kwargs={'pk': self.kwargs.get('problem')})

class SubmissionViewMixinTimed(SubmissionViewMixin, FormView):
    model = Submission
    form_class = SubmissionForm
    template_name = 'problems_timed/submission.html'

    def record_submission(self, request):
        user = request.user
        section = request.user.section
        problem = self.get_problem()
        self.submission = Submission.objects.filter(user=user, section=section, problem=problem).order_by('-pk')[:1][0]
        if self.submission.timestamp_complete:
            return HttpResponseForbidden()
        self.submission.set_score(request.POST['submission'])
        return []

class SubmissionView(ProtectedViewMixin, SubmissionViewMixinTimed,
                     SingleObjectMixin, UserViewMixin):
    form_class = SubmissionForm
    object = None

    def get_success_url(self):
        return reverse('timed_list')
    
    def get_request_info(self, request):
        info = {'user': request.user, 'section': request.user.section, 'problem': self.get_problem()}
        return info
    
    def get(self, request, *args, **kwargs):
        info = self.get_request_info(request)
        total = Submission.objects.filter(user=info['user'], section=info['section'], problem=info['problem']).count()
        
        show_button = 1
        if total >= info['problem'].attempts:
            show_button = 0
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(form=form)
        context['show_button'] = show_button
        context['total_submissions'] = total
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        info = self.get_request_info(request)
        submission = Submission.objects.filter(user=info['user'], section=info['section'], problem=info['problem']).order_by('-pk')[:1][0]
        
        if submission.timestamp_complete:
            return HttpResponseForbidden()
        
        submission.set_score(request.POST['submission'])
        
        return HttpResponseRedirect('/content/quests')
