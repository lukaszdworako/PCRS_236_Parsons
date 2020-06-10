import json
import datetime
import logging

from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import (DetailView, UpdateView, DeleteView, FormView, View)
from django.views.generic.detail import SingleObjectMixin
from django.utils.timezone import localtime
from pcrs.generic_views import (GenericItemCreateView, GenericItemListView,
                                GenericItemUpdateView)
from users.section_views import SectionViewMixin
from users.views import UserViewMixin
from users.views_mixins import ProtectedViewMixin

from problems.forms import EditorForm
from problems.views import DateEncoder
from problems_rdb.forms import EditorForm as RDBEditorForm

import problems_c.models as c_models
import problems_python.models as python_models
import problems_ra.models as ra_models
import problems_sql.models as sql_models
import problems_java.models as java_models
import problems_r.models as r_models


class EditorViewMixin:
    def get_section(self):
        return None

    def get_problem(self):
        '''Return the Problem object for the submission.
        '''
        pClass = self.model.get_problem_class()
        editorId = pClass.editor_problem_id()

        if self.pType == 'ra':
            # TODO: This relies on the existence of specific schema.
            # Using schema 10 (HR) from 343 and the Extended Grammar.
            return self.get_or_create_problem(pClass,
                name='blank', starter_code='',
                description='', grammar='Extended Grammar', semantics='set',
                id=editorId, schema_id=10)
        elif self.pType == 'sql':
            # TODO: This relies on the existence of specific schema.
            # Using schema 10 (HR) from 343.
            return self.get_or_create_problem(pClass,
                name='blank', starter_code='',
                description='', id=editorId, schema_id=10)

        return self.get_or_create_problem(pClass,
            name='blank', starter_code='',
            id=editorId, language=self.pType)

    def get_or_create_problem(self, problemClass, **kwargs):
        '''Get or create a problem with the given parameters.

        Normally with get_or_create, something trivial such as a name change
        will cause an integrity error. The function _only_ cares about the id.

        Params:
            kwargs: Must include id. Other options are problems type specific.
        Return:
            The problem object.
        '''
        problemId = kwargs['id']
        if problemClass.objects.filter(id=problemId).exists():
            return problemClass.objects.get(id=problemId)
        p, created = problemClass.objects.get_or_create(**kwargs)
        return p

    def get_starter_code(self):
        '''The code to display when initially going to the editor.
        '''
        if self.pType == 'c':
            return (
                '#include <stdio.h>\n'
                'int main() {\n'
                '    return 0;\n'
                '}\n'
            )
        elif self.pType == 'java':
            return (
                '[file Code.java]\n'
                'public class Code {\n'
                '    public static void main(String args[]) {\n'
                '    }\n'
                '}\n'
                '[/file]\n'
            )
        return ''

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['problem'] = self.get_problem()
        kwargs['simpleui'] = True
        kwargs['initial_code'] = self.get_starter_code()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.get_problem()
        return context

    def record_submission(self, request):
        """
        Record the submission and return the results of running the testcases.
        """
        submission_code = request.POST.get('submission', '')
        results, error = [], None
        if submission_code:
            if self.pType == 'python':
            	submission = python_models.Submission(
                    user=request.user, problem=self.get_problem(),
                    section=self.get_section(), submission=submission_code)
            elif self.pType == 'c':
            	submission = c_models.Submission(
                    user=request.user, problem=self.get_problem(),
                    section=self.get_section(), submission=submission_code)
            elif self.pType == 'ra':
                submission = ra_models.Submission(
                    user=request.user, problem=self.get_problem(),
                    section=self.get_section(), submission=submission_code)
            elif self.pType == 'sql':
                submission = sql_models.Submission(
                    user=request.user, problem=self.get_problem(),
                    section=self.get_section(), submission=submission_code)
            elif self.pType == 'java':
                submission = java_models.Submission(
                    user=request.user, problem=self.get_problem(),
                    section=self.get_section(), submission=submission_code)
            elif self.pType == 'r':
                submission = r_models.Submission(
                    user=request.user, problem=self.get_problem(),
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
    form_class = EditorForm
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
        content_type='application/json')
