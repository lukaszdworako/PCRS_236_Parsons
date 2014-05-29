from django.conf import settings

def site_settings(request):
    languages = [language[0] for language in settings.LANGUAGE_CHOICES]
    return {'site_prefix': settings.SITE_PREFIX, 'languages': languages}
