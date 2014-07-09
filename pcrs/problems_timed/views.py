from django.core.urlresolvers import reverse

from django.views.generic import (UpdateView, DeleteView, FormView)
from django.views.generic.detail import SingleObjectMixin

from problems_timed.models import Term, Submission
from problems_timed.forms import TermForm, SubmissionForm

from problems.views import TestCaseView, SubmissionView, SubmissionViewMixin
from pcrs.generic_views import GenericItemCreateView
from users.views_mixins import ProtectedViewMixin

class TermView(TestCaseView):
    model = Term
    form_class = TermForm
    template_name = 'problems_timed/term_form.html'

    def get_success_url(self):
        return reverse('timed_add_term',
                       kwargs={'problem': self.object.problem.pk})

class TermCreateView(TermView, GenericItemCreateView):

    def get_success_url(self):
        return reverse('timed_update',
                       kwargs={'pk': self.object.problem.pk})

# necessary for "save and add another" button to function properly
class TermsCreateView(TermView, GenericItemCreateView):
    pass

class TermUpdateView(TermView, UpdateView):
    template_name = 'problems_timed/term_update.html'
    
    def get_success_url(self):
        return reverse('timed_update',
                       kwargs={'pk': self.object.problem.pk})

class TermDeleteView(TermView, DeleteView):
    template_name = 'problems_timed/term_delete.html'

    def get_success_url(self):
        return reverse('timed_update',
                       kwargs={'pk': self.kwargs.get('problem')})

class SubmissionViewMixinTimed(SubmissionViewMixin, FormView):
    model = Submission
    form_class = SubmissionForm
    template_name = 'problems_timed/submission.html'

    def record_submission(self, request):
        problem = self.get_problem()
        self.submission = self.model.objects.create(
            problem=problem, user=request.user, section=self.get_section())

        self.submission.set_score(request.REQUEST['submission'])
        return []

class SubmissionView(ProtectedViewMixin, SubmissionViewMixinTimed,
                     SingleObjectMixin):
    form_class = SubmissionForm
    object = None

    def get_success_url(self):
        return reverse('timed_list')
    
    def post(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        results = self.record_submission(request)
        return self.render_to_response(
            self.get_context_data(form=form, results=results,
                                  submission=self.submission))
