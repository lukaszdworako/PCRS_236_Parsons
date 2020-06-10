from sys import modules

from django.conf import settings
# ------------------
# Removed in >1.5, replaced with below
# from django.contrib.contenttypes import generic
from django.contrib.contenttypes.fields import GenericForeignKey
# ------------------
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q


def get_problem_labels():
    """
    Return the list app_labels of apps that contain a Problem class.
    """
    return [c.app_label for c in get_problem_content_types()]


def get_problem_content_types():
    apps = list(settings.INSTALLED_PROBLEM_APPS.keys())
    return ContentType.objects.filter(Q(model='problem', app_label__in=apps))


def get_submission_content_types():
    apps = list(settings.INSTALLED_PROBLEM_APPS.keys())
    return ContentType.objects.filter(Q(model='submission', app_label__in=apps))


class AbstractSelfAwareModel(models.Model):
    """
    A model that is aware of its ContentType and app.
    """
    class Meta:
        abstract = True

    def get_uri_id(self):
        return '{content_type}-{pk}'\
            .format(content_type=self.get_content_type_name(), pk=self.pk)

    def serialize(self):
        return {
            'id': self.get_uri_id(),
            'pk': self.pk,
            'content_type': self.get_content_type_name()
        }

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
    def get_class_by_name(cls, name):
        app = modules[cls.__module__]
        return getattr(app, name)

    @classmethod
    def get_problem_class(cls):
        return cls.get_class_by_name('Problem')

    @classmethod
    def get_submission_class(cls):
        return cls.get_class_by_name('Submission')

    @classmethod
    def get_testrun_class(cls):
        return cls.get_class_by_name('TestRun')

    @classmethod
    def get_pretty_name(cls):
        name = str(cls.get_content_type()).replace('_', ' ')
        if name == 'problem':
            name = '{kind} problem'\
                .format(kind=cls.get_app_label()
                .replace('_', ' ').replace('problems ', ''))
        return name

    @classmethod
    def get_base_url(cls):
        app_label = cls.get_app_label()
        model = cls.__name__.lower()
        url = '{app}/{model}s'.format(app=app_label, model=model)
        return '{prefix}/{url}'.format(prefix=settings.SITE_PREFIX, url=url)

    def get_absolute_url(self):
        return '{base}/{pk}'.format(base=self.get_base_url(), pk=self.pk)


class AbstractNamedObject(models.Model):
    """
    An object that has a name, and an optional description.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            'name': self.name,
            'description': self.description
        }

    def replace_latex(self):
        tag_count = self.description.count("$$")
        current_count = 0
        sections = self.description.split("$$")
        total_string = ""

        for i in range(len(sections)):
            if i % 2 == 0:
                if i != 0 or sections[0] != "":
                    total_string += sections[i]
            elif current_count + 2 <= tag_count and i % 2 == 1:
                total_string += '<img src="http://latex.codecogs.com/svg.latex?'
                total_string += sections[i]
                total_string += '" border="0"/>'
                current_count += 2

        return total_string


class AbstractGenericObjectForeignKey(models.Model):
    objects = None

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, limit_choices_to=objects, on_delete=models.CASCADE)
    content_object = GenericForeignKey('content_type', 'object_id')

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
    parent_content_object = GenericForeignKey('parent_content_type',
                                                      'parent_object_id')

    child_object_id = models.PositiveIntegerField()
    child_content_type = models.ForeignKey(ContentType,
                                           limit_choices_to=children)
    child_content_object = GenericForeignKey('child_content_type',
                                                     'child_object_id')

    class Meta:
        abstract = True
        ordering = ['order']
        order_with_respect_to = ['parent_content_object']
