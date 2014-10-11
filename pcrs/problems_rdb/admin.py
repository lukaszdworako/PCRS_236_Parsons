from django.contrib import admin

from problems_rdb.models import Dataset, Schema


admin.site.register(Schema)
admin.site.register(Dataset)