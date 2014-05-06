from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView

from users.views_mixins import ProtectedViewMixin, CourseStaffViewMixin


class CourseStaffProblemView(CourseStaffViewMixin):
    def get_queryset(self):
        if self.request.user.is_student:
            return self.model.objects.filter(visibility='open')
        if self.request.user.is_ta:
            return self.model.objects.exclude(visibility='closed')
        else:
            return self.model.objects.all()


class ProblemListView(ProtectedViewMixin, ListView):
    """
    List all problems.
    """
    template_name = 'problems/problem_list.html'

    def get_queryset(self):
        if self.request.user.is_student:
            return self.model.objects.filter(visibility='open')
        if self.request.user.is_ta:
            return self.model.objects.exclude(visibility='closed')
        else:
            return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '{} problems'.format(
            self.model.type_name.replace('_', ' ').capitalize())
        return context


class ProblemCreateView(CourseStaffProblemView, CreateView):
    """
    Create a new problem.
    """
    template_name = 'problems/problem_form.html'

    def get_success_url(self):
        return self.model.get_base_url() + '/list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'New {} problem'.format(
            self.model.type_name.replace('_', ' '))
        return context


class ProblemCreateAndAddTCView(ProblemCreateView):
    """
    Create a new problem and add testcases.
    """
    def get_success_url(self):
        return '{}/testcase'.format(self.object.get_absolute_url())


class ProblemUpdateView(CourseStaffProblemView, UpdateView):
    """
    Update a problem.
    """
    template_name = 'problems/problem_form.html'

    def get_success_url(self):
        return self.model.get_base_url() + '/list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit'
        return context


class ProblemDeleteView(CourseStaffProblemView, DeleteView):
    """
    Delete a problem.
    """
    template_name = 'problems/problem_check_delete.html'

    def get_success_url(self):
        return self.model.get_base_url() + '/list'


class ProblemClearView(CourseStaffProblemView, DetailView):
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


class SubmissionViewMixin:
    def get_section(self):
        return (self.request.session.get('section', None) or
                self.request.user.section)

    def get_problem(self):
        return get_object_or_404(self.model.get_problem_class(),
                                 pk=self.kwargs.get('problem'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.get_problem()
        return context