from django.contrib import admin
from problems.admin import ProblemAdmin, SubmissionAdmin
from .models import *


admin.site.register(Problem, ProblemAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(TestCase)
admin.site.register(TestRun)
