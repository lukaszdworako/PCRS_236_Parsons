from django.conf import settings
from django.contrib import admin

from .models import *


if 'problems_timed' in settings.INSTALLED_PROBLEM_APPS:
    admin.site.register(Problem)
    admin.site.register(Submission)
    admin.site.register(Page)
