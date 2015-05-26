from django.conf import settings
from django.contrib import admin

from .models import *


if 'problems_rating' in settings.INSTALLED_PROBLEM_APPS:
    admin.site.register(Problem)
    admin.site.register(Submission)
