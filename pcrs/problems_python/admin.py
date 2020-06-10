from django.conf import settings
from django.contrib import admin

from problems.admin import ProblemAdmin, SubmissionAdmin
from .models import *


if 'problems_python' in settings.INSTALLED_PROBLEM_APPS:
    admin.site.register(Problem, ProblemAdmin)
    admin.site.register(Submission, SubmissionAdmin)
    admin.site.register(TestCase)
    admin.site.register(TestRun)
