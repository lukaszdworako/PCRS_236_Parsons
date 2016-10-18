from collections import defaultdict
import csv, zipfile, io
import time

from django.http import HttpResponse
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
from django.utils.html import strip_tags
from django.contrib.contenttypes.models import ContentType

from pcrs.generic_views import (GenericItemListView, GenericItemCreateView,
                                GenericItemUpdateView)
from problems.models import (get_problem_content_types,
                             get_submission_content_types)
from users.forms import SectionForm, QuestGradeForm, SectionSelectionForm
from users.models import Section, PCRSUser, MASTER_SECTION_ID
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'View pages as section'
        return context


class SectionListView(CourseStaffViewMixin, GenericItemListView):
    model = Section
    template_name = 'pcrs/section_list.html'

    def get_queryset(self):
        return Section.objects.exclude(section_id=MASTER_SECTION_ID)


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
        quests = form.cleaned_data['quests']

        if len(quests) == 1:
            return self.singleQuestResponse(form.cleaned_data)
        return self.multipleQuestResponse(form.cleaned_data)

    def multipleQuestResponse(self, data):
        quests = data['quests']
        section = data['section']

        response = HttpResponse(mimetype='application/zip')
        response['Content-Disposition'] = 'attachment; filename='\
            + self._generateZipName(section)

        # Generate a zip file with all the quest data

        with zipfile.ZipFile(response, 'w') as zippy:
            for quest in quests:
                fileName = self._generateCsvName(section, quest)
                csvOut = io.StringIO()
                self.writeQuestCsvDataToBuffer(csvOut, quest, data)
                zippy.writestr(fileName, csvOut.getvalue())

        return response

    def singleQuestResponse(self, data):
        quest = data['quests'][0]
        section = data['section']

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename='\
            + self._generateCsvName(section, quest)

        self.writeQuestCsvDataToBuffer(response, quest, data)

        return response

    def _cleanName(self, name):
        newname = []
        for ch in name:
            if ch.isspace():
                newname.append('_')
            elif ch.isalpha() or ch.isdigit():
                newname.append(ch)
        if not newname:
            newname = ["anon"]
        return "".join(newname)

    def _generateCsvName(self, section, quest):
        section_name = self._cleanName(str(section).split("@")[0].strip())
        quest_name = self._cleanName(quest.name)
        return '{0}-{1}-{2}.csv'.format(section_name, quest_name, time.strftime("%m%d%y"))

    def _generateZipName(self, section):
        section_name = self._cleanName(str(section).split("@")[0].strip())
        return '{0}-{1}.zip'.format(section_name, time.strftime("%m%d%y"))

    def writeQuestCsvDataToBuffer(self, buf, quest, data):
        section = data['section']
        active_only = data['active']
        for_credit = data['for_credit']

        # return a csv file
        writer = csv.writer(buf)

        # collect the problem ids, names, and max_scores, and for_credit
        problems = []
        problemTypes = dict()
        names = ['problem name (url)']
        max_scores = ['max_scores']
        for_credit_row = ['for credit?']
        for problem in self._getSortedSectionProblems(quest):
            # include for_credit and/or not for_credit problems
            is_graded = problem.challenge.is_graded
            if ('fc' in for_credit and is_graded) or \
                    ('nfc' in for_credit and not is_graded):
                typeName = 'problems_' + problem.get_problem_type_name()
                problemTypes[typeName] = problemTypes.get(typeName, 0) + 1
                problems.append((typeName, problem.pk))
                names.append(self._formatProblemTitle(problem))
                max_scores.append(problem.max_score)
                for_credit_row.append(is_graded)
        problemTypeNames = problemTypes.keys()

        studentGrades = self._getBestStudentSubmissions(
            section, quest, active_only)
        studentRows = self._generateStudentRows(
            section, studentGrades, problems, max_scores, problemTypes, active_only)

        # The attempted and solved summary columns
        for t in problemTypeNames:
            names += [t + '_attempted', t + '_solved']
            max_scores += [problemTypes[t]] * 2 # The same max for each
        for_credit_row += [False] * len(problemTypeNames) * 2

        # Write all the data to the CSV file
        writer.writerow(names)
        writer.writerow(max_scores)
        writer.writerow(for_credit_row)
        for row in studentRows:
            writer.writerow(row)

    def _generateStudentRows(self, section, grades,
            problems, maxScores, problemTypes, active_only):
        rows = []

        # Removing "maxScores" from the front of the list to make it parallel with problems
        maxScores = maxScores[1:]

        for studentId, scoreDict in grades.items():
            scores = []
            problemsAttempted = dict()
            problemsSolved = dict()

            for index, problem in enumerate(problems):
                score = scoreDict.get(problem, '')
                scores.append(score)
                problemType, problemName = problem
                maxScore = maxScores[index]

                if problemType not in problemsAttempted:
                    # If it isn't in one, it isn't in the other.
                    problemsAttempted[problemType] = 0
                    problemsSolved[problemType] = 0
                if not score == '':
                    problemsAttempted[problemType] += 1
                if score == maxScore:
                    problemsSolved[problemType] += 1

            for t in problemTypes.keys():
                problemTypeCount = problemTypes[t]
                scores.append(problemsAttempted[t])
                scores.append(problemsSolved[t])

            rows.append([studentId] + scores)

        # Collect students in the section who have not submitted anything

        students = PCRSUser.objects.get_students(active_only=active_only)\
            .filter(section=section)\
            .exclude(username__in=grades.keys())
        for student in students:
            rows.append([student.username] +
                [''] * len(problems) + [0] * len(problemTypes) * 2)
        return rows

    def _getSortedSectionProblems(self, quest):
        '''Retrieves the given problems in sorted (displayed) order.
        '''
        problemIds = self._getProblemIdsInQuest(quest)
        pages = [page
            for page_list in [
                challenge.contentpage_set.all()
                    for challenge in quest.challenge_set.all()
            ] for page in page_list
        ]
        return [seq_item.content_object
            for item_list in [
                page.contentsequenceitem_set.all()
                    for page in pages
            ] for seq_item in item_list
                if "problem" in seq_item.content_object.get_pretty_name() and \
                    seq_item.content_object.pk in problemIds
        ]

    def _formatProblemTitle(self, problem):
        name = problem.name or "[{0}]".format(problem.get_pretty_name().title())
        url = problem.get_base_url() + '/' + str(problem.pk)
        return "{0} ({1})".format(name, url)

    def _getProblemIdsInQuest(self, quest):
        '''Retrieves problem IDs in the given quest.
        '''
        problemIds = []
        for contentType in get_problem_content_types():
            problems = contentType.model_class().objects\
                .select_related('challenge')\
                .filter(challenge__quest=quest, visibility='open')
            for problem in problems:
                problemIds.append(problem.pk)
        return problemIds

    def _getBestStudentSubmissions(self, section, quest, active_only):
        '''Collect best submissions grades for each student.
        '''
        studentGrades = defaultdict(dict)
        for contentType in get_submission_content_types():
            grades = contentType.model_class().grade(
                quest=quest, section=section, active_only=active_only)
            for record in grades:
                problem = (contentType.app_label,
                           record['problem'])
                studentGrades[record['user']][problem] = record['best']
        return studentGrades

