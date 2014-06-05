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


class AbstractTaggedObject(models.Model):
    """
    An object that may have any number of tags.
    """
    tags = models.ManyToManyField(Tag, null=True, blank=True,
                                  related_name='%(app_label)s_%(class)s_related')

    class Meta:
        abstract = True