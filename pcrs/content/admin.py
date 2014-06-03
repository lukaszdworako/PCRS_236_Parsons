from django.contrib import admin

from .models import *


admin.site.register(Tag)

admin.site.register(Video)
admin.site.register(TextBlock)

admin.site.register(ContentPage)
admin.site.register(ContentSequenceItem)
admin.site.register(Challenge)

admin.site.register(Container)
admin.site.register(SectionContainer)

admin.site.register(ProblemSet)
admin.site.register(ContainerProblem)
admin.site.register(ContainerAttempt)
