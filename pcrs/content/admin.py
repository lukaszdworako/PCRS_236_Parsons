from django.contrib import admin

from .models import *


admin.site.register(Video)
admin.site.register(TextBlock)
admin.site.register(ContentProblem)

admin.site.register(ContentPage)
admin.site.register(ContentSequenceItem)
admin.site.register(Challenge)

admin.site.register(Container)
admin.site.register(OrderedContainerItem)


admin.site.register(ProblemSet)
admin.site.register(ProblemSetProblem)
