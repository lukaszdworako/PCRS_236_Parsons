from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F
from django.db.models.signals import pre_delete
from content.tags import AbstractTaggedObject

from pcrs.models import (AbstractNamedObject, AbstractGenericObjectForeignKey,
                         AbstractOrderedGenericObjectSequence,
                         AbstractSelfAwareModel)
from users.models import AbstractLimitedVisibilityObject, PCRSUser, Section


# CONTENT OBJECTS

class Video(AbstractSelfAwareModel, AbstractNamedObject, AbstractTaggedObject):
    """
    A Video object has a name, a description, and a link to a video.
    """
    link = models.TextField()

    class Meta:
        ordering = ['name']


class TextBlock(models.Model):
    """
    A text object has a single attribute - the text to be displayed.
    """
    text = models.TextField()


class ContainerAttempt(AbstractGenericObjectForeignKey, models.Model):
    """

    """
    objects = (models.Q(model='challenge') | models.Q(model='problemset'))

    user = models.ForeignKey(PCRSUser)

    attempted_ontime = models.SmallIntegerField(default=0)
    completed_ontime = models.SmallIntegerField(default=0)
    attempted = models.SmallIntegerField(default=0)
    completed = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = ['content_type', 'object_id', 'user']

    def __str__(self):
        return '{0} {1} a:{2} c:{3}'\
            .format(self.content_type, self.object_id, self.attempted,
            self.completed)

    @classmethod
    def get_cont_to_num_completed(cls, user, content_type):
        """
        Return a dictionary mapping the pks of containers of type content_type
        to the number of problems the user completed on time in that container.
        """
        return {
            problem_container.object_id:
                problem_container.completed_ontime
            for problem_container in cls.objects.filter(
                user=user, content_type=content_type).select_related()
        }


class ContentSequenceItem(AbstractOrderedGenericObjectSequence):
    """
    A content objects to be displayed on some page.
    """
    objects = (models.Q(model='problem') |
               models.Q(model='video') | models.Q(model='textblock'))

    content_page = models.ForeignKey('ContentPage')

    class Meta:
        # a problem can be in a single content page
        unique_together = ['content_type', 'object_id', 'content_page']

    @classmethod
    def get_unassigned_problems(cls, app_label):
        c_type = ContentType.objects.get(app_label=app_label, model='problem')
        assigned_pks = cls.objects.filter(content_type=c_type)\
                                  .values_list('object_id', flat=True)
        return c_type.model_class().objects.exclude(pk__in=assigned_pks)

    @classmethod
    def get_unassigned_video(cls):
        assigned_pks = cls.objects.filter(content_type=Video.get_content_type())\
                                  .values_list('object_id', flat=True)
        return Video.objects.exclude(pk__in=assigned_pks)

    def __str__(self):
        return 'challenge: {0}; content_type: {1}, id:{2}'\
            .format(self.content_page.challenge.pk, self.content_type, self.object_id)


class ContentPage(models.Model):
    """
    A page displaying a sequence of ContentSequenceItems.
    """
    challenge = models.ForeignKey('Challenge')
    order = models.SmallIntegerField()

    def __str__(self):
        return '{name}: page {order}'.format(name=self.challenge.name,
                                             order=self.order)

    def next(self):
        try:
            return ContentPage.objects.get(challenge=self.challenge,
                                           order=self.order+1)
        except ContentPage.DoesNotExist:
            return None

    def previous(self):
        if self.order == 0:
            return None
        else:
            return ContentPage.objects.get(challenge=self.challenge,
                                           order=self.order-1)


class ChallengeProblem(models.Model):
    challenge_content_type = models.ForeignKey(
        ContentType, related_name='challenge_content_type')
    challenge_id = models.PositiveIntegerField()
    challenge_object = generic.GenericForeignKey(
        'challenge_content_type', 'challenge_id')
    
    problem_content_type = models.ForeignKey(
        ContentType, related_name='problem_content_type')
    problem_id = models.PositiveIntegerField()
    problem_object = generic.GenericForeignKey(
        'problem_content_type', 'problem_id')

    class Meta:
        # a problem can be in a single problem container
        unique_together = ['problem_content_type', 'problem_id']


class Challenge(AbstractSelfAwareModel, AbstractNamedObject,
                AbstractLimitedVisibilityObject):
    """
    A Challenge is a sequence of ContentPages, which are defined in markup.
    """
    quest = models.ForeignKey('Quest', blank=True, null=True)
    is_graded = models.BooleanField(default=False, blank=True)

    problems = generic.GenericRelation(ChallengeProblem,
        content_type_field='container_content_type',
        object_id_field='container_object_id')

    pages = None


    def get_first_page(self):
        return '{}/0'.format(self.get_absolute_url())

    def get_main_page(self):
        return '{}/go'.format(self.get_absolute_url())


class Quest(AbstractNamedObject):
    pass


class SectionQuest(AbstractLimitedVisibilityObject):
    """

    """
    section = models.ForeignKey(Section)
    container = models.ForeignKey('Quest')
    open_on = models.DateTimeField(blank=True, null=True)
    due_on = models.DateTimeField(blank=True, null=True)
    order = models.SmallIntegerField(default=0)
    is_graded = models.BooleanField(default=False)

    class Meta:
        unique_together = ['section', 'container']

    def __str__(self):
        return '{section} {container}'.format(section=self.section,
            container=self.container)


def page_delete(sender, instance, **kwargs):
    """
    Renumber the remaining page order, when a page is deleted.
    """
    ContentPage.objects\
        .filter(challenge=instance.challenge, order__gt=instance.order)\
        .update(order=F('order')-1)
pre_delete.connect(page_delete, sender=ContentPage)