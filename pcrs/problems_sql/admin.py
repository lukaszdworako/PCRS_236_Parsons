from django.contrib import admin
from problems.admin import ProblemAdmin, SubmissionAdmin
from .models import *


class SQLProblemAdmin(ProblemAdmin):
    list_filter = ( 'visibility', 'challenge' )


admin.site.register(Problem, SQLProblemAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(TestCase)
admin.site.register(TestRun)
