from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models


class AbstractSelfAwareModel(models.Model):
    """
    A model that is aware of its ContentType and app.
    """
    class Meta:
        abstract = True

    @classmethod
    def get_content_type(cls):
        """
        Returns the Content Type for this model.
        """
        return ContentType.objects.get_for_model(cls)

    @classmethod
    def get_content_type_id(cls):
        """
        Return the id of the Content Type for this model.
        """
        return cls.get_content_type().pk

    @classmethod
    def get_app_label(cls):
        """
        Return the app label of the Content Type for this model.
        """
        return cls.get_content_type().app_label

    @classmethod
    def get_problem_class(cls):
        app_label = cls.get_app_label()
        c_type = ContentType.objects.get(model='problem', app_label=app_label)
        return c_type.model_class()

    @classmethod
    def get_submission_class(cls):
        app_label = cls.get_app_label()
        c_type = ContentType.objects.get(model='submission', app_label=app_label)
        return c_type.model_class()

    @classmethod
    def get_pretty_name(cls):
        name = str(cls.get_content_type()).replace('_', ' ')
        if name == 'problem':
            name = '{kind} problem'\
                .format(kind=cls.get_app_label()
                .replace('_', ' ').replace('problems ', ''))
        return name


class AbstractNamedObject(models.Model):
    """
    An object that has a name, and an optional description.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class AbstractGenericObjectForeignKey(models.Model):
    objects = None

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, limit_choices_to=objects)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True


class AbstractOrderedGenericObjectSequence(AbstractGenericObjectForeignKey):
    order = models.SmallIntegerField(blank=True, default=0)

    class Meta:
        abstract = True
        ordering = ['order']


class AbstractOrderedGenericObjectSequence2(AbstractGenericObjectForeignKey):
    parents = None
    children = None

    parent_object_id = models.PositiveIntegerField()
    parent_content_type = models.ForeignKey(ContentType,
                                            limit_choices_to=parents)
    parent_content_object = generic.GenericForeignKey('parent_content_type',
                                                      'parent_object_id')

    child_object_id = models.PositiveIntegerField()
    child_content_type = models.ForeignKey(ContentType,
                                           limit_choices_to=children)
    child_content_object = generic.GenericForeignKey('child_content_type',
                                                     'child_object_id')

    class Meta:
        abstract = True
        ordering = ['order']
        order_with_respect_to = ['parent_content_object']
