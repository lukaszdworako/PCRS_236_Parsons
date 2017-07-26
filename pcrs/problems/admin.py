from django.contrib import admin

class ProblemAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'visibility', 'challenge', 'language', 'author' )
    list_filter = ( 'language', 'visibility', 'challenge', 'author' )
    search_fields = ( 'name', 'visibility', 'challenge', 'author' )
    select_related = ( 'challenge', )


class SubmissionAdmin(admin.ModelAdmin):
    ordering = ( '-timestamp', 'user' )
    list_display = ( 'user', 'problem', 'timestamp', 'has_best_score', 'score', 'section' )
    list_filter = ( 'section', 'has_best_score', 'problem', 'user' )
    select_related = ( 'user', 'section', 'problem' )
    search_fields = ( 'problem', 'user' )
