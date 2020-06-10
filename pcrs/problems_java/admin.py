from django.conf import settings
from django.contrib import admin

from problems.admin import ProblemAdmin, SubmissionAdmin
from .models import *


if 'problems_java' in settings.INSTALLED_PROBLEM_APPS:
    admin.site.register(Problem, ProblemAdmin)
    admin.site.register(Submission, SubmissionAdmin)
    admin.site.register(TestRun)
