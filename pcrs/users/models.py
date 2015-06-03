from django.conf import settings
from django.db import models
from django.utils import timezone

# authentication
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import (BaseUserManager)
import content.models
from pcrs.models import AbstractSelfAwareModel

from django.db.models.signals import post_syncdb
from django.dispatch import receiver
import django.contrib.auth.models


VISIBILITY_LEVELS = (
    ('closed', 'closed'),
    ('draft', 'draft'),
    ('open', 'open')
)

MASTER_SECTION_ID = 'master'

@python_2_unicode_compatible
class CustomAbstractBaseUser(models.Model):
    """
    This is Django AbstractBaseUser class updated to function without the pasword.
    """
    # password = models.CharField(_('password'), max_length=128, blank=True, null=True)
    last_login = models.DateTimeField(_('last login'), default=timezone.now)

    is_active = True

    REQUIRED_FIELDS = []

    class Meta:
        abstract = True

    def get_username(self):
        """ Return the identifying username for this User """
        return getattr(self, self.USERNAME_FIELD)

    def __str__(self):
        return self.get_username()

    def natural_key(self):
        return (self.get_username(),)

    def is_anonymous(self):
        """
        Always returns False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    # def set_password(self, raw_password):
    #        self.password = make_password(raw_password)
    #
    #    def check_password(self, raw_password):
    #        """
    #        Returns a boolean of whether the raw_password was correct. Handles
    #        hashing formats behind the scenes.
    #        """
    #        def setter(raw_password):
    #            self.set_password(raw_password)
    #            self.save(update_fields=["password"])
    #        return check_password(raw_password, self.password, setter)
    #
    #    def set_unusable_password(self):
    #        # Sets a value that will never be a valid hash
    #        self.password = make_password(None)
    #
    #    def has_usable_password(self):
    #        return is_password_usable(self.password)

    def get_full_name(self):
        raise NotImplementedError()

    def get_short_name(self):
        raise NotImplementedError()


class PCRSUserManager(BaseUserManager):
    def create_user(self, username, is_instructor, section_id=None, is_admin=False, is_staff=False):
        """
        Creates and saves a superuser with the given username, instructor status,
        section id and password.
        """
        user = self.model(username=username, is_instructor=is_instructor, section_id=section_id, is_admin=is_admin)
        # user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, is_instructor, section_id=None):
        """
        Creates and saves a superuser with the given username, instructor status,
        section id and password.
        """
        # user = self.create_user(username=username, is_instructor=is_instructor, password=password, section_id=section_id, is_admin=True, is_staff=True)
        section_id = section_id or MASTER_SECTION_ID
        user = self.create_user(username=username, is_instructor=is_instructor, section_id=section_id, is_admin=True,
                                is_staff=True)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


        # create user:
        # if user is admin or is instructor:
        # use their password
        # else
        # use password 1

        # save
        # take password
        # if password has changed:
        # hash password
        # save user

    def get_students(self, active_only=False):
        """
        Returns all student users.
        """
        if active_only:
            return PCRSUser.objects.filter(is_student=True, is_active=True).all()
        else:
            return PCRSUser.objects.filter(is_student=True).all()

    def get_users(self, active_only=False):
        """
        Return all users, optionally excluding inactive users.
        """
        if active_only:
            return PCRSUser.objects.filter(is_active=True).all()
        else:
            return PCRSUser.objects.all()



class PCRSUser(CustomAbstractBaseUser):
    username = models.CharField('username', max_length=30, unique=True, db_index=True)
    section = models.ForeignKey("Section")

    code_style_choices = (
        ('monokai', 'Dark Background'),
        ('eclipse', 'Light Background'),
        ('shaped', 'Black and White')
    )
    code_style = models.CharField(max_length=7,
                                  choices=code_style_choices,
                                  default='monokai')
    use_simpleui = models.BooleanField(default=False)

    is_student = models.BooleanField(default=False)
    is_ta = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    objects = PCRSUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['is_instructor', ]

    def get_full_name(self):
        # The user is identified by their user id
        return self.username

    def get_short_name(self):
        # The user is identified by their user id
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        "Save hashed password or a hash of a dummy password. "
        # Django 1.4 and 1.5 treat both empty string and None as unusable password,
        # need to provide dummy password

        # pwd_not_required = not (self.is_admin or self.is_staff)
        # if pwd_not_required:
        #     try:
        #         self.password = PCRSUser.objects.get(pk=self.pk).password
        #         print("user does not require password")
        #
        #     except Exception as e:
        #         print("making password 1")
        #         self.password = make_password("1")
        #
        # elif self.password == "!":
        #     print("obtained !, keeping old password")
        #     print(PCRSUser.objects.get(pk=self.pk).password)
        #     self.password = PCRSUser.objects.get(pk=self.pk).password


        super(PCRSUser, self).save(*args, **kwargs)


class Section(AbstractSelfAwareModel):
    """
    Section has an id, location, lecture time, and optional description.
    A user is enrolled in one section.
    Instructors teach one or more sections.
    """
    section_id = models.SlugField("section id", primary_key=True, max_length=10)
    description = models.CharField("section description", max_length=100, blank=True, null=True)
    location = models.CharField("location", max_length=10)
    lecture_time = models.CharField("lecture time", max_length=20)

    def __unicode__(self):
        return '%s @ %s' % (self.lecture_time, self.location)

    def __str__(self):
        return '%s @ %s' % (self.lecture_time, self.location)

    @classmethod
    def get_base_url(cls):
        return '{site}/sections'.format(site=settings.SITE_PREFIX)

    @classmethod
    def get_lecture_sections(cls):
        return cls.objects.exclude(section_id=MASTER_SECTION_ID)

    def is_master(self):
        return self.section_id == MASTER_SECTION_ID

    def get_manage_section_quests_url(self):
        return '{site}/content/quests/section/{pk}'\
            .format(site=settings.SITE_PREFIX, pk=self.pk)

    def get_stats_url(self):
        return '{}/reports'.format(self.get_absolute_url())

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.__class__.objects.filter(pk=self.pk).exists():
            # new section: create SectionQuests for it
            super().save(force_insert, force_update, using, update_fields)
            for quest in content.models.Quest.objects.all():
                content.models.SectionQuest.objects.create(section=self,
                    quest=quest)
        else:
            super().save(force_insert, force_update, using, update_fields)


# This should ordinarily be in pcrs/management/__init__.py but it wasn't working that way
# The post_syncdb receiver is also deprecated in Django 1.9, in favor of post_migrate
@receiver(post_syncdb, sender=django.contrib.auth.models)
def insert_master_section(sender, **kwargs):
    # Required for the superuser creation and must happen first
    Section(pk='master', description='master', location='master', lecture_time='master').save()


class AbstractLimitedVisibilityObject(models.Model):
    visibility = models.CharField(choices=VISIBILITY_LEVELS, max_length=10,
                                  default='closed', blank=True, null=False)

    class Meta:
        abstract = True

    def serialize(self):
        return {
            'is_visible': self.is_visible_to_students(),
        }

    @classmethod
    def get_visible_for_user(cls, user):
        """
        Return the objects that the user is allowed to see.
        """
        if user.is_student:
            return cls.objects.filter(visibility='open')
        if user.is_ta:
            return cls.objects.exclude(visibility='closed')
        else:
            return cls.objects.all()

    def is_visible_to_students(self):
        return self.is_open()

    def is_open(self):
        return self.visibility == 'open'

    def is_closed(self):
        return self.visibility == 'closed'

    def is_draft(self):
        return self.visibility == 'draft'

    def open(self):
        self.visibility = "open"
        self.save()

    def closed(self):
        self.visibility = "closed"
        self.save()

    def draft(self):
        self.visibility = "draft"
        self.save()

