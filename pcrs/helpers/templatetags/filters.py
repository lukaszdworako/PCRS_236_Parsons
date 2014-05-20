from django.template.defaultfilters import register


@register.filter
def classname(obj):
    return obj.__class__.__name__

@register.filter
def problem_type(obj):
    return obj.content_object.content_object._meta.app_label

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def problem_type_from_label(obj):
    return obj.replace('problems_', '').replace('_', ' ')