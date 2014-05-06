from django.db import models


class AbstractNamedObject(models.Model):
    """
    A named object.
    """
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name