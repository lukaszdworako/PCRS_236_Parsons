from django.contrib import admin
from .models import *

admin.site.register(Problem)
admin.site.register(Submission)
admin.site.register(TestCase)
admin.site.register(TestRun)