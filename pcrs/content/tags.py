import re

from django.core.exceptions import ValidationError
from django.db import models
from pcrs.models import AbstractSelfAwareModel


class Tag(AbstractSelfAwareModel):
    """
    An object tag.
    """
    name = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)

        ''' Note: This is normally implemented in crispy forms, but we
                  need to validate it manually for normal tag object creation
        '''
        if not re.compile("^[0-9a-z\-_]+$", re.IGNORECASE).match(self.name):
            raise ValidationError({'name':
              "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.",
            })


class AbstractTaggedObject(models.Model):
    """
    An object that may have any number of tags.
    """
    tags = models.ManyToManyField(Tag, null=True, blank=True,
                                  related_name='%(app_label)s_%(class)s_related')

    class Meta:
        abstract = True

    def serialize(self):
        return {
            'tags': [tag.name for tag in self.tags.all()]
        }
