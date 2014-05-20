from django.contrib import admin

from problems_ra.models import *


admin.site.register(Problem)
admin.site.register(TestCase)
admin.site.register(Submission)
admin.site.register(TestRun)