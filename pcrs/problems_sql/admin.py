from django.contrib import admin
from problems_sql.models import *

admin.site.register(Problem)
admin.site.register(TestCase)
admin.site.register(TestRun)
admin.site.register(Submission)
