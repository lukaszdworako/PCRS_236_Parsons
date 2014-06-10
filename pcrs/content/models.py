from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F, Q
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
    content_videos = generic.GenericRelation('ContentSequenceItem',
                                             content_type_field='content_type',
                                             object_id_field='object_id')


class TextBlock(models.Model):
    """
    A text object has a single attribute - the text to be displayed.
    """
    text = models.TextField()

    content_text = generic.GenericRelation('ContentSequenceItem',
                                        content_type_field='content_type',
                                             object_id_field='object_id')


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
    order = models.SmallIntegerField(default=0, blank=True)
    is_graded = models.BooleanField(default=False, blank=True)

    problems = generic.GenericRelation(ChallengeProblem,
        content_type_field='container_content_type',
        object_id_field='container_object_id')

    class Meta:
        ordering = ['quest', 'order']
        # order_with_respect_to = 'quest'

    def get_first_page(self):
        return '{}/0'.format(self.get_absolute_url())

    def get_main_page(self):
        return '{}/go'.format(self.get_absolute_url())


class Quest(AbstractNamedObject, AbstractSelfAwareModel):
    order = models.SmallIntegerField(default=0)

    class Meta:
        ordering = ['order']


class SectionQuest(AbstractLimitedVisibilityObject):
    """

    """
    section = models.ForeignKey(Section)
    quest = models.ForeignKey('Quest')
    open_on = models.DateTimeField(blank=True, null=True)
    due_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['section', 'quest']

    def __str__(self):
        return '{section} {quest}'.format(section=self.section, quest=self.quest)


def page_delete(sender, instance, **kwargs):
    """
    Renumber the remaining page order, when a page is deleted.
    """
    ContentPage.objects\
        .filter(challenge=instance.challenge, order__gt=instance.order)\
        .update(order=F('order')-1)
pre_delete.connect(page_delete, sender=ContentPage)