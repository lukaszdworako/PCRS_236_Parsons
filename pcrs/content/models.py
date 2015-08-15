import datetime

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F
from django.db.models.signals import pre_delete, post_delete
from django.utils.timezone import utc, now, localtime
#from graph_utilities.create_graph import output_graph

from content.tags import AbstractTaggedObject

from pcrs.settings import MYMEDIA_VIDEOS

from pcrs.models import (AbstractNamedObject, AbstractSelfAwareModel,
                         AbstractOrderedGenericObjectSequence,
                         get_problem_content_types)
from users.models import AbstractLimitedVisibilityObject, PCRSUser, Section


class Video(AbstractSelfAwareModel, AbstractNamedObject, AbstractTaggedObject):
    """
    A Video object has a name, a description, and a link to a video.
    """
    link = models.TextField()
    thumbnail = models.URLField(blank=True)
    download = models.URLField(blank=True)
    content_videos = generic.GenericRelation('ContentSequenceItem',
                                             content_type_field='content_type',
                                             object_id_field='object_id')

    @property
    def url(self):
        if "media/public" in self.link:      # Hack for MYMEDIA
            return 'rtmp://media.library.utoronto.ca/vod/&mp4:{}'.format(self.link)
        elif "youtube.com" in self.link:     # To embed YOUTUBE.COM
            tag = self.link.find("?v=")
            return 'https://www.youtube.com/embed/{0}'.format(self.link[tag+3:tag+14])
        else:
            return self.link

    @property
    def format(self):
        if "media/public" in self.link:      # Hack for MYMEDIA
            return 'rtmp/mp4'
        else:
            return 'video/mp4'

    class Meta:
        ordering = ['name']

    def get_number_watched(self, section=None):
        watched = WatchedVideo(video=self)
        if section:
            watched = watched.filter(user__section=section)
        return watched.count()

    def get_content_type_name(cls):
        return 'video'

    def serialize(self):
        serialized = {}
        for base in self.__class__.__bases__:
            serialized.update(base.serialize(self))
        serialized['url'] = self.url,
        serialized['thumbnail'] = self.thumbnail,
        serialized['download'] = self.download,
        serialized['record_watched'] = '{}/watched'\
            .format(self.get_absolute_url())
        return serialized


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


    @classmethod
    def watched(cls, user, video):
        try:
            cls.objects.get(user=user, video=video)
            return True
        except cls.DoesNotExist:
            return False


    @classmethod
    def get_watched_uri_ids(cls, user):
        return {
            watched.video.get_uri_id(): True
            for watched in cls.objects.select_related('video').filter(user=user)
        }


class TextBlock(AbstractSelfAwareModel):
    """
    A text object has a single attribute - the text to be displayed.
    """
    text = models.TextField()

    content_text = generic.GenericRelation('ContentSequenceItem',
                                            content_type_field='content_type',
                                            object_id_field='object_id')

    def __str__(self):
        return self.text[:150]

    def serialize(self):
        serialized = super().serialize()
        serialized.update({
            'text': self.text,
        })
        return serialized

    def get_content_type_name(cls):
        return 'textblock'


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


class ContentPage(AbstractSelfAwareModel):
    """
    A page displaying a sequence of ContentSequenceItems.
    """
    challenge = models.ForeignKey('Challenge')
    order = models.SmallIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return '{name}: page {order}'.format(name=self.challenge.name,
                                             order=self.order)
    @classmethod
    def get_content_type_name(cls):
        return 'content_page'

    @classmethod
    def get_visible_for_section(cls, section):
        """
        Return a queryset of ContentPages that are visible to the section.

        A Content Page is visible if the following conditions are met:
        1. the challenge this page is in is open
        2. the challenge's quest is live
        3. the quest is visible to the section
        4. the quest has been released to the section
        """
        return cls.objects.select_related('challenge').filter(
            challenge__visibility='open',
            challenge__quest__sectionquest__section=section,
            challenge__quest__mode='live',
            challenge__quest__sectionquest__visibility='open',
            challenge__quest__sectionquest__open_on__lt=localtime(now())
        )

    def serialize(self):
        serialized = super().serialize()
        serialized.update({
            'order': self.order,
            'url': self.get_absolute_url()
        })
        return serialized

    def get_absolute_url(self):
        return '{challenge}/{num}'.format(
            challenge=self.challenge.get_absolute_url(), num=self.order)

    def get_next_url(self):
        page = self.next()
        return page.get_absolute_url() if page else None

    def get_previous_url(self):
        page = self.previous()
        return page.get_absolute_url() if page else None

    def next(self):
        try:
            return ContentPage.objects.get(challenge=self.challenge,
                                           order=self.order+1)
        except ContentPage.DoesNotExist:
            return None

    def previous(self):
        if self.order == 1:
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

    @classmethod
    def get_content_type_name(cls):
        return 'challenge'
    
    def __str__(self):
        return '{name} | {quest}'.format(name=self.name, quest=self.quest)
    
    @staticmethod
    def _get_completed_challenges(completed, total):
        return {challenge.pk for challenge in Challenge.objects.all()
                if completed.get(challenge.pk, None) == total.get(challenge.pk, 0)}

    @classmethod
    def get_challenge_problem_data(cls, user, section):
        def sum_dict_values(*args):
            total = {}
            for arg in args:
                for key, value in arg.items():
                    existing = total.get(key, 0)
                    new = existing + value
                    total[key] = new
            return total

        data = {}
        challenge_to_total, challenge_to_completed = [], []
        best = {}
        problems_completed = {}

        for content_type in get_problem_content_types():  # 1 query
            problem_class = content_type.model_class()
            submission_class = problem_class.get_submission_class()
            challenge_to_total.append(problem_class.get_challenge_to_problem_number())
            challenge_to_completed.append(
                submission_class.get_completed_for_challenge_before_deadline(user, section))

            best[content_type.app_label], \
            problems_completed[content_type.app_label] = submission_class\
                .get_best_attempts_before_deadlines(user, section)


        data['best'] = best
        data['problems_completed'] = problems_completed
        # number of problems completed by a student in this challenge
        data['challenge_to_completed'] = sum_dict_values(*challenge_to_completed)
        # total number of problems in this challenge
        data['challenge_to_total'] = sum_dict_values(*challenge_to_total)

        data['challenges_completed'] = cls._get_completed_challenges(
            data['challenge_to_completed'], data['challenge_to_total'])

        return data

    @classmethod
    def get_challenge_graph_data(cls):
        """
        Return a dictionary mapping challenge id to a dictionary defining
        the challenge name, prerequisites, and quest id.
        """
        return {
            challenge.pk: {
                'name': challenge.name,
                'prerequisites': list(challenge.prerequisites.all()
                                               .values_list('id', flat=True)),
                'quest': challenge.quest_id,
                'url': challenge.get_first_page_url()
            }
            for challenge in cls.objects.prefetch_related('prerequisites').all()
        }

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        # output_graph(self.get_challenge_graph_data())

    def serialize(self):
        serialized = {}
        for base in self.__class__.__bases__:
            serialized.update(base.serialize(self))
        serialized.update({
            'order': self.order,
            'graded': self.is_graded,
            'url': self.get_absolute_url()
        })
        return serialized

    def get_first_page_url(self):
        try:
            page = self.contentpage_set.get(order=1)
            return page.get_absolute_url()
        except ContentPage.DoesNotExist:
            return None

    def get_stats_page_url(self):
        return '{}/stats'.format(self.get_absolute_url())


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
            for section in Section.get_lecture_sections():
                SectionQuest.objects.get_or_create(section=section, quest=self)
        else:
            super().save(force_insert, force_update, using, update_fields)

    @classmethod
    def get_content_type_name(cls):
        return 'quest'

    def serialize(self):
        serialized = {}
        for base in self.__class__.__bases__:
            serialized.update(base.serialize(self))
        serialized['order'] = self.order
        serialized['mode'] = self.mode
        return serialized


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

    def serialize(self):
        serialized = {}
        for base in self.__class__.__bases__:
            serialized.update(base.serialize(self))
        serialized.update({
            'deadline': localtime(self.due_on).strftime('%c')
                        if self.due_on else None,
            'deadline_passed': localtime(self.due_on) < localtime(now())
        })
        serialized.update(self.quest.serialize())
        return serialized


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


def contenttextitem_delete(sender, instance, **kwargs):
    """
    Delete the text block if its ContentSequenceItem was removed.
    """
    if instance.content_type.model == 'text block':
        instance.content_object.delete()

pre_delete.connect(page_delete, sender=ContentPage)
pre_delete.connect(contentsequenceitem_delete, sender=ContentSequenceItem)
post_delete.connect(contenttextitem_delete, sender=ContentSequenceItem)
