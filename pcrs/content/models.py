from collections import defaultdict
import datetime

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F
from django.db.models.signals import pre_delete
from django.utils.timezone import utc

from content.tags import AbstractTaggedObject

from pcrs.models import (AbstractNamedObject, AbstractSelfAwareModel,
                         AbstractOrderedGenericObjectSequence)
# import problems.models
from users.models import AbstractLimitedVisibilityObject, PCRSUser, Section


class Video(AbstractSelfAwareModel, AbstractNamedObject, AbstractTaggedObject):
    """
    A Video object has a name, a description, and a link to a video.
    """
    link = models.TextField()
    thumbnail = models.URLField()
    download = models.URLField()
    content_videos = generic.GenericRelation('ContentSequenceItem',
                                             content_type_field='content_type',
                                             object_id_field='object_id')

    class Meta:
        ordering = ['name']

    def get_number_watched(self, section=None):
        watched = WatchedVideo(video=self)
        if section:
            watched = watched.filter(user__section=section)
        return watched.count()


class WatchedVideo(models.Model):
    """
    A record of a user starting a Video.
    """
    video = models.ForeignKey(Video)
    user = models.ForeignKey(PCRSUser, to_field='username')

    class Meta:
        unique_together = ['video', 'user']

    @classmethod
    def get_watched_pk_list(cls, user):
        return set(cls.objects.filter(user=user)
                              .values_list('video_id', flat=True))


class TextBlock(models.Model):
    """
    A text object has a single attribute - the text to be displayed.
    """
    text = models.TextField()

    content_text = generic.GenericRelation('ContentSequenceItem',
                                            content_type_field='content_type',
                                            object_id_field='object_id')

    def __str__(self):
        return self.text[:150]


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
        return c_type.model_class().objects.filter(challenge__isnull=True)

    @classmethod
    def get_unassigned_video(cls):
        assigned_pks = cls.objects.filter(content_type=Video.get_content_type())\
                                  .values_list('object_id', flat=True)
        return Video.objects.exclude(pk__in=assigned_pks)

    def __str__(self):
        return 'challenge: {0}; content_type: {1}, id:{2}'\
            .format(self.content_page.challenge.pk,
                    self.content_type, self.object_id)


class ContentPage(models.Model):
    """
    A page displaying a sequence of ContentSequenceItems.
    """
    challenge = models.ForeignKey('Challenge')
    order = models.SmallIntegerField()

    def __str__(self):
        return '{name}: page {order}'.format(name=self.challenge.name,
                                             order=self.order)

    def get_absolute_url(self):
        return '{challenge}/{num}'.format(
            challenge=self.challenge.get_absolute_url(), num=self.order)

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


class Challenge(AbstractSelfAwareModel, AbstractNamedObject,
                AbstractLimitedVisibilityObject):
    """
    A Challenge is a sequence of ContentPages and can be graded or ungraded.
    """
    quest = models.ForeignKey('Quest', blank=True, null=True,
                              on_delete=models.SET_NULL)
    order = models.SmallIntegerField(default=0, blank=True)
    is_graded = models.BooleanField(default=False, blank=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False,
                                           blank=True, null=True)
    enforce_prerequisites = models.BooleanField(default=False, blank=True)

    class Meta:
        ordering = ['quest', 'order']

    def get_first_page_url(self):
        try:
            page = self.contentpage_set.get(order=1)
            return page.get_absolute_url()
        except ContentPage.DoesNotExist:
            return None

    def get_stats_page_url(self):
        return '{}/stats'.format(self.get_absolute_url())

    def get_prerequisite_pks_set(self):
        return set(c.pk for c in self.prerequisites.all())


class Quest(AbstractNamedObject, AbstractSelfAwareModel):
    """
    Am ordered sequence of Challenges.
    """
    MODES = (('maintenance', 'maintenance'), ('live', 'live'))

    order = models.SmallIntegerField(default=0)
    mode = models.CharField(choices=MODES, default='maintenance', max_length=16)

    class Meta:
        ordering = ['order']

    def is_live(self):
        return self.mode == 'live'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.__class__.objects.filter(pk=self.pk).exists():
            # new Quest, create SectionQuests for it
            super().save(force_insert, force_update, using, update_fields)
            for section in Section.objects.all():
                SectionQuest.objects.get_or_create(section=section, quest=self)
        else:
            super().save(force_insert, force_update, using, update_fields)


class SectionQuest(AbstractLimitedVisibilityObject):
    """
    Quest setup for a specific Section.
    """
    section = models.ForeignKey(Section)
    quest = models.ForeignKey('Quest')
    open_on = models.DateTimeField(blank=True, null=True)
    due_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['section', 'quest']
        ordering = ['quest__order']

    def is_past_due(self):
        return datetime.datetime.utcnow().replace(tzinfo=utc) > self.due_on

    def __str__(self):
        return '{section} {quest}'.format(section=self.section, quest=self.quest)


def page_delete(sender, instance, **kwargs):
    """
    Renumber the remaining page order, when a page is deleted.
    """
    ContentPage.objects\
        .filter(challenge=instance.challenge, order__gt=instance.order)\
        .update(order=F('order')-1)


def contentsequenceitem_delete(sender, instance, **kwargs):
    """
    Reset the problem's Challenge to None when deleting a
    ContentSequence Problem.
    """
    if (instance.content_type.model == 'problem' and
        instance.content_object is not None):
        instance.content_object.challenge = None
        instance.content_object.save()

pre_delete.connect(page_delete, sender=ContentPage)
pre_delete.connect(contentsequenceitem_delete, sender=ContentSequenceItem)