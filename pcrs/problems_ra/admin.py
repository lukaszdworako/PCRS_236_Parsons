from django.conf import settings
from django.contrib import admin

from problems.admin import ProblemAdmin, SubmissionAdmin
from .models import *


class RAProblemAdmin(ProblemAdmin):
    list_filter = ( 'visibility', 'challenge' )

if 'problems_ra' in settings.INSTALLED_PROBLEM_APPS:
    admin.site.register(Problem, RAProblemAdmin)
    admin.site.register(Submission, SubmissionAdmin)
    admin.site.register(TestCase)
    admin.site.register(TestRun)

