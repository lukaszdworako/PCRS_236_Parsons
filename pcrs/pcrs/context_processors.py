from django.conf import settings

def site_settings(request):
    problem_types = [pt for pt in settings.INSTALLED_PROBLEM_APPS.keys()]
    languages = [pt[1] for pt in settings.INSTALLED_PROBLEM_APPS.items() if pt[1]]

    return {'site_prefix': settings.SITE_PREFIX, 'languages': languages, 
            'problem_types': problem_types, 'mymedia_videos': settings.MYMEDIA_VIDEOS, 
            'auth_shibboleth': settings.AUTH_TYPE == 'shibboleth'}
