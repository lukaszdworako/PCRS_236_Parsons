import json
from django.http import HttpResponse
from django.views.generic import DetailView, TemplateView
from problems_code.models import Problem
from users.views import UserViewMixin
from users.views_mixins import CourseStaffViewMixin, ProtectedViewMixin


class InclassProblems(ProtectedViewMixin, UserViewMixin, DetailView):
    """
    Return a list of open problems.
    """
    model = Problem

    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps([
            problem.serialize() for problem in self.model.objects.filter(visibility='open').all()
        ]),  mimetype='application/json')


class InclassProblemsView(ProtectedViewMixin, TemplateView):
    template_name = 'content/inclass_problems.html'