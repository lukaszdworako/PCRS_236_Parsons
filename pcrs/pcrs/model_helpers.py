from django.db import models


def has_changed(instance, field):
    """
    Return True if the instance is a new instance of a model,
    or the field value has changed in the instance.
    """
    if not instance.pk:
        return True
    stored_value = get_stored_value(instance, field)
    current_value = getattr(instance, field)
    if isinstance(current_value, models.Model):
        current_value = instance.pk
    return current_value != stored_value


def get_stored_value(instance, field):
    """
    Get the value currently stored for the field in the instance.
    """
    if not instance.pk:
        return None
    stored_value = instance.__class__._default_manager.\
        filter(pk=instance.pk).values(field).get()[field]
    return stored_value