from collections import defaultdict
import csv
from django.http import HttpResponse
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from pcrs.generic_views import (GenericItemListView, GenericItemCreateView,
                                GenericItemUpdateView)
from problems.models import get_problem_content_types
from users.forms import SectionForm, QuestGradeForm, SectionSelectionForm
from users.models import Section
from users.views_mixins import CourseStaffViewMixin


class SectionViewMixin:
    def get_section(self):
        return (self.request.session.get('section', None) or
                self.request.user.section)


class ChangeSectionView(CourseStaffViewMixin, SectionViewMixin, FormView):
    template_name = 'pcrs/crispy_form.html'
    form_class = SectionSelectionForm

    def form_valid(self, form):
        self.request.session['section'] = form.cleaned_data['section']
        return self.form_invalid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial['section'] = self.get_section()
        return initial


class SectionListView(CourseStaffViewMixin, GenericItemListView):
    model = Section
    template_name = 'pcrs/section_list.html'


class SectionCreateView(CourseStaffViewMixin, GenericItemCreateView):
    model = Section
    form_class = SectionForm

    def get_success_url(self):
        return self.object.get_manage_section_quests_url()


class SectionUpdateView(CourseStaffViewMixin, GenericItemUpdateView):
    model = Section
    form_class = SectionForm


class SectionReportsView(CourseStaffViewMixin, SingleObjectMixin, FormView):
    model = Section
    form_class = QuestGradeForm
    template_name = 'pcrs/crispy_form.html'
    object = None

    def get_initial(self):
        initial = super().get_initial()
        initial['section'] = self.get_object()
        return initial

    def form_valid(self, form):
        # return a csv file
        section, quest = form.cleaned_data['section'], form.cleaned_data['quest']
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=report.csv'
        writer = csv.writer(response)

        problems, names, max_scores = [], []
        for ctype in get_problem_content_types():
            for problem in ctype.model_class().object.filter(challenge__quest=quest):
                problems.append((problem.get_problem_type(), problem.pk))

                names.append((problem.get_problem_type(),
                              problem.name if hasattr(problem, 'name')
                              else problem.description))
                max_scores.append(problem.max_score)

        results = defaultdict(dict)
        for ctype in get_problem_content_types():
            grades = ctype.model_class().grade(quest=quest, section=section)
            for record in grades:
                results[record['user']][ctype.model_class().get_problem_type(), record['problem']] = record['best']

        for student_id, score_dict in results:
            writer.writerow(student_id, [score_dict.get(problem) for problem in problems])
        # return response