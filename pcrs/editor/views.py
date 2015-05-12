import json
import datetime
import logging

from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import (DetailView, UpdateView, DeleteView, FormView, View)
from django.views.generic.detail import SingleObjectMixin
from django.utils.timezone import localtime
from problems.forms import ProgrammingSubmissionForm
from pcrs.generic_views import (GenericItemCreateView, GenericItemListView,
                                GenericItemUpdateView)
from users.section_views import SectionViewMixin
from users.views import UserViewMixin
from users.views_mixins import ProtectedViewMixin
import problems_c.models as c_models
import problems_python.models as python_models

# Helper class to encode datetime objects
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

class EditorViewMixin:
    def get_section(self):
        return None

    def get_problem(self):
        """
        Return the Problem object for the submission.
        """
        if self.pType == 'c':
        	p, created = self.model.get_problem_class().objects.get_or_create(name="blank", starter_code="", id=9999999, language="c")
        elif self.pType == 'python':
        	p, created = self.model.get_problem_class().objects.get_or_create(name="blank", starter_code="", id=9999999, language="python")
       	logging.info(p.name)
        return p

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['problem'] = self.get_problem()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        problem = self.get_problem()
        context['problem'] = problem
        return context

    def record_submission(self, request):
        """
        Record the submission and return the results of running the testcases.
        """
        submission_code = request.POST.get('submission', '')
        results, error = [], None
        if submission_code:
            logging.info(submission_code)
            if self.pType == 'python':
            	submission = python_models.Submission(user=request.user, problem=self.get_problem(),
                    section=self.get_section(), submission=submission_code)
            elif self.pType == 'c':
            	submission = c_models.Submission(user=request.user, problem=self.get_problem(),
                    section=self.get_section(), submission=submission_code)
            results, error = submission.run_testcases(request)
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

class EditorView(ProtectedViewMixin, EditorViewMixin, SingleObjectMixin,
                     FormView, UserViewMixin):
    """
    Create a submission for a problem.
    """
    pType = None
    form_class = ProgrammingSubmissionForm
    object = None

class EditorAsyncView(EditorViewMixin, SingleObjectMixin,
                          SectionViewMixin, View):
    """
    Create a submission for a problem asynchronously.
    """
    pType = None
    def post(self, request, *args, **kwargs):
        results = self.record_submission(request)
        problem = self.get_problem()
        pType = problem.language
        user, section = self.request.user, self.get_section()

        logger = logging.getLogger('activity.logging')
        logger.info(str(localtime(self.object.timestamp)) + " | " +
                    str(user) + " | Submit " +
                    str(problem.get_problem_type_name()) + " " +
                    str(problem.pk))
        deadline = False

        return HttpResponse(json.dumps({
            'results': results,
            'score': self.object.score,
            'sub_pk': self.object.pk,
            'best': self.object.has_best_score,
            'past_dead_line': deadline and self.object.timestamp > deadline,
            'max_score': self.object.problem.max_score}, cls=DateEncoder),
        mimetype='application/json')