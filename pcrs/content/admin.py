from django.contrib import admin
from content.tags import Tag

from .models import *


admin.site.register(Tag)

admin.site.register(Video)
admin.site.register(WatchedVideo)
admin.site.register(TextBlock)

admin.site.register(Challenge)
admin.site.register(ContentPage)
admin.site.register(ContentSequenceItem)

admin.site.register(Quest)
admin.site.register(SectionQuest)