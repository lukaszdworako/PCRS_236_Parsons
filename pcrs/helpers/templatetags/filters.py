from django.template.defaultfilters import register


@register.filter
def classname(obj):
    return obj.__class__.__name__

@register.filter
def problem_type(obj):
    return obj.get_problem_type_name()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def problem_type_from_label(obj):
    return obj.replace('problems_', '').replace('_', ' ')

@register.filter
def module_name(obj):
    return obj.__class__.__module__.split('.')[0]

@register.filter
def get_div_class(obj):
    return obj.replace('problems_', '')

@register.filter
def issubset(s1, s2):
    return s1.issubset(s2)