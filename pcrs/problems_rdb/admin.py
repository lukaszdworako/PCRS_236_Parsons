from django.conf import settings
from django.contrib import admin

from problems_rdb.models import Dataset, Schema


if 'problems_rdb' in settings.INSTALLED_PROBLEM_APPS:
    admin.site.register(Schema)
    admin.site.register(Dataset)
