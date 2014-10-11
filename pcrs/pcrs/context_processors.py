from django.conf import settings

def site_settings(request):
    languages = [language[0] for language in settings.LANGUAGE_CHOICES]
    problem_types = [pt for pt in settings.INSTALLED_PROBLEM_APPS]
    return {'site_prefix': settings.SITE_PREFIX, 'languages': languages, 
            'problem_types': problem_types, 'mymedia_videos': settings.MYMEDIA_VIDEOS, 
            'auth_shibboleth': settings.AUTH_TYPE == 'shibboleth'}
