from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group

from content.tags import Tag
from .models import *


# Unregistrations placed here because everyone will load this admin.py
admin.site.unregister(Site)
admin.site.unregister(Group)


# And now registrations for this app
admin.site.register(Tag)

admin.site.register(Video)
admin.site.register(WatchedVideo)
admin.site.register(TextBlock)

admin.site.register(Challenge)
admin.site.register(ContentPage)
admin.site.register(ContentSequenceItem)

admin.site.register(Quest)
admin.site.register(SectionQuest)
