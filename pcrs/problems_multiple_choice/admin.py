from django.contrib import admin
from .models import *

admin.site.register(Problem)
admin.site.register(Submission)
admin.site.register(Option)
admin.site.register(OptionSelection)