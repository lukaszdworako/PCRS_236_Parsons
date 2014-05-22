import json
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import (ListView, DetailView, CreateView, UpdateView,
                                  DeleteView, FormView, View)
from django.views.generic.detail import SingleObjectMixin
from pcrs.generic_views import GenericItemCreateView, GenericItemListView

from problems.forms import ProgrammingSubmissionForm
from users.views_mixins import ProtectedViewMixin, CourseStaffViewMixin


class ProblemView:
    """
    Base class for Problem views.
    """
    def get_queryset(self):
        """
        Return the Problems the user is allowed to access.
        """
        if self.request.user.is_student:
            return self.model.objects.filter(visibility='open')
        if self.request.user.is_ta:
            return self.model.objects.exclude(visibility='closed')
        else:
            return self.model.objects.all()

    def get_problem_type_name(self):
        return self.model.get_problem_type_name().replace('_', ' ').capitalize()


class ProblemListView(ProtectedViewMixin, ProblemView, GenericItemListView):
    """
    List all problems.
    """
    template_name = 'problems/problem_list.html'


class ProblemCreateView(CourseStaffViewMixin, ProblemView,
                        GenericItemCreateView):
    """
    Create a new problem.
    """
    template_name = 'problems/problem_form.html'

    def get_success_url(self):
        return self.model.get_base_url() + '/list'


class ProblemCloneView(ProblemCreateView):
    """
    Create a new problem.
    """
    template_name = 'problems/problem_form.html'

    def get_initial(self):
        return self.get_object()

    def get(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        return redirect(self.get_context_data(form=form))


class ProblemCreateAndAddTCView(ProblemCreateView):
    """
    Create a new problem and add testcases.
    """
    def get_success_url(self):
        return '{}/testcase'.format(self.object.get_absolute_url())


class ProblemUpdateView(CourseStaffViewMixin, ProblemView, UpdateView):
    """
    Update a problem.
    """
    template_name = 'problems/problem_form.html'

    def get_success_url(self):
        return self.model.get_base_url() + '/list'


class ProblemDeleteView(CourseStaffViewMixin, ProblemView, DeleteView):
    """
    Delete a problem.
    """
    template_name = 'problems/problem_check_delete.html'

    def get_success_url(self):
        return self.model.get_base_url() + '/list'


class ProblemClearView(CourseStaffViewMixin, ProblemView, DetailView):
    """
    Clear all submissions to a problem.
    """
    template_name = 'problems/submission_check_delete.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.clear_submissions()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return self.object.get_absolute_url()


class TestCaseView(CourseStaffViewMixin):
    """
    Base view for creating and updating testcases for a problem.
    """
    template_name = 'problems/testcase_form.html'

    def get_problem(self):
        return get_object_or_404(self.model.get_problem_class(),
                                 pk=self.kwargs.get('problem'))

    def get_initial(self):
        return {
            'problem': self.get_problem(),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.get_problem()
        return context

    def get_queryset(self):
        visible_problems = self.get_visible_problems(self.request)
        return self.model.objects.filter(problem__in=visible_problems)

    def get_success_url(self):
        return self.get_problem().get_absolute_url()


class TestCaseCreateManyView(TestCaseView, GenericItemCreateView):
    """
    Create multiple new testcases for a problem.
    """
    def get_success_url(self):
        return '{}/testcase'.format(self.object.problem.get_absolute_url())


class TestCaseCreateView(TestCaseView, GenericItemCreateView):
    """
    Create a new testcase for a problem.
    """


class TestCaseUpdateView(TestCaseView, UpdateView):
    """
    Update an existing testcase for a problem.
    """


class TestCaseDeleteView(TestCaseView, DeleteView):
    """
    Delete a testcase.
    """
    template_name = 'problems/testcase_check_delete.html'


class SubmissionViewMixin:
    def get_section(self):
        return (self.request.session.get('section', None) or
                self.request.user.section)

    def get_problem(self):
        """
        Return the Problem object for the submission.
        """
        if self.request.user.is_student:
            return get_object_or_404(self.model.get_problem_class(),
                                     pk=self.kwargs.get('problem'),
                                     visibility='open')
        if self.request.user.is_ta:
            return get_object_or_404(self.model.get_problem_class(),
                                     pk=self.kwargs.get('problem'),
                                     visibility__in=['open', 'draft'])
        else:
            return get_object_or_404(self.model.get_problem_class(),
                                     pk=self.kwargs.get('problem'))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['problem'] = self.get_problem()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        problem = self.get_problem()
        context['problem'] = problem
        context['submissions'] = self.model.get_submission_class().objects\
            .filter(student=self.request.user, problem=problem).all()
        return context

    def record_submission(self, request):
        """
        Record the submission and return the results of running the testcases.
        """
        submission_model = self.model.get_submission_class()
        submission_code = request.POST.get('submission', '')
        results, error = [], None
        if submission_code:
            submission = submission_model.objects.create(
                student=request.user, problem=self.get_problem(),
                section=self.get_section(), submission=submission_code)
            results, error = submission.run_testcases(request)
            submission.set_score()
            self.object = submission
        return results, error

    def post(self, request, *args, **kwargs):
        """
        Record the submission and redisplay the problem submission page,
        with latest submission prefilled.
        """
        form = self.get_form(self.get_form_class())
        results, error = self.record_submission(request)
        return self.render_to_response(
            self.get_context_data(form=form, results=results, error=error,
                                  submission=self.object))


class SubmissionView(ProtectedViewMixin, SubmissionViewMixin, SingleObjectMixin,
                     FormView):
    """
    Create a submission for a problem.
    """
    form_class = ProgrammingSubmissionForm
    object = None


class SubmissionAsyncView(SubmissionViewMixin, SingleObjectMixin, View):
    """
    Create a submission for a problem asynchronously.
    """
    def post(self, request, *args, **kwargs):
        results = self.record_submission(request)
        return HttpResponse(json.dumps(results), mimetype='application/json')