from django.template.defaultfilters import register


@register.filter
def get_number_completed(obj, user):
    return obj.get_number_completed(user)