from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from pyparsing import (CaselessKeyword, OneOrMore, Suppress, Word, ZeroOrMore,
                       alphanums, nums, originalTextFor,
                       Group, Literal, ParseException)

from pcrs.models import (AbstractNamedObject, AbstractGenericObjectForeignKey,
                         AbstractOrderedGenericObjectSequence,
                         AbstractSelfAwareModel)
from users.models import AbstractLimitedVisibilityObject, PCRSUser, Section


# TAGS
class Tag(models.Model):
    """
    An object tag.
    """
    name = models.CharField(max_length=100, unique=True)

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


# CONTENT OBJECTS

class Video(AbstractNamedObject):
    """
    A Video object has a name, a description, and a link to a video.
    """
    link = models.URLField()


class TextBlock(models.Model):
    """
    A text object has a single attribute - the text to be displayed.
    """
    text = models.TextField()


# PROBLEM CONTAINERS
class GradableObjectContainer(AbstractSelfAwareModel, AbstractNamedObject,
                              AbstractLimitedVisibilityObject):
    total_problems = models.SmallIntegerField(default=0)

    class Meta:
        abstract = True


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


# problem sets
class ContainerProblem(models.Model):
    container_content_type = models.ForeignKey(ContentType, related_name='container_content_type')
    container_id = models.PositiveIntegerField()
    container_object = generic.GenericForeignKey(
        'container_content_type', 'container_id')
    
    problem_content_type = models.ForeignKey(ContentType, related_name='problem_content_type')
    problem_id = models.PositiveIntegerField()
    problem_object = generic.GenericForeignKey(
        'problem_content_type', 'problem_id')

    class Meta:
        # a problem can be in a single problem container
        unique_together = ['problem_content_type', 'problem_id']


class ProblemSet(GradableObjectContainer):
    container = models.ForeignKey('Container', null=True)

    problems = generic.GenericRelation(ContainerProblem,
        content_type_field='container_content_type',
        object_id_field='container_object_id',
        related_name='problemset_problems')

    def get_absolute_url(self):
        return '/content/problem_set/{}'.format(self.pk)

    def get_main_page(self):
        return '{}/list'.format(self.get_absolute_url())

    def get_problems_for_type(self, app_label):
        content_type = ContentType.objects.get(app_label=app_label,
                                               model='problem')
        return ContainerProblem.objects.filter(problem_set=self,
                                                content_type=content_type)


# challenges
class Challenge(GradableObjectContainer):
    """
    A Challenge is a sequence of ContentPages, which are defined in markup.
    """
    markup = models.TextField(blank=True)
    container = models.ForeignKey('Container', null=True)

    problems = generic.GenericRelation(ContainerProblem,
        content_type_field='container_content_type',
        object_id_field='container_object_id',
        related_name='challenge_problems')

    pages = None

    def get_absolute_url(self):
        return '/content/challenge/{}'.format(self.pk)

    def get_first_page(self):
        return '{}/0'.format(self.get_absolute_url())

    def get_main_page(self):
        return '{}/go'.format(self.get_absolute_url())

    def get_problem_set(self):
        problems = ContentType.objects.filter(model='problem')
        x= {
            (item.app_label, item.object_id)
            for page in self.contentpage_set.all()
            for item in page.gradable_item_set.filter(content_type__in=problems)
        }
        print(x)
        return x


    # def parse(self):
    #     def parameter(parser):
    #         """
    #         Return a parser the parses parameters.
    #         """
    #         return Suppress('_{').leaveWhitespace() + parser + Suppress('}')
    #
    #     # def create_content_problem(start, location, tokens):
    #     #     app_label = 'problems_{}'.format(tokens.type)
    #     #     problem_content_type = ContentType.objects.get(app_label=app_label,
    #     #                                                    model='problem')
    #     #     problem_object = problem_content_type.\
    #     #         get_object_for_this_type(pk=tokens.pk)
    #     #     is_graded = (tokens[0] == '\summative')
    #     #     return ContentProblem.objects.create(content_object=problem_object,
    #     #                                          is_graded=is_graded)
    #
    #     def create_text_block(tokens):
    #         return TextBlock.objects.create(text=tokens[0])
    #
    #     pk = Word(nums)('pk')
    #
    #     problem_type = (Literal('code') | Literal('multiple_choice'))('type')
    #     p_kw = (CaselessKeyword('\\summative', identChars=alphanums) |
    #             CaselessKeyword('\\formative', identChars=alphanums))
    #     # problem = (p_kw +
    #     #            parameter(problem_type + pk)).setParseAction(create_content_problem)
    #
    #     video = (CaselessKeyword('\\video', identChars=alphanums) +
    #              parameter(pk)).setParseAction(lambda s, l, t: (t.pk))
    #
    #     text = originalTextFor(OneOrMore(Word(alphanums))).addParseAction(
    #         create_text_block)
    #
    #     content = Group(ZeroOrMore(text))('content')
    #
    #     page = Suppress(CaselessKeyword('\\page'))
    #     page_end = Suppress(CaselessKeyword('\\end'))
    #
    #     content = ZeroOrMore(Group(page + content + page_end))
    #
    #     return content.parseString(self.markup, parseAll=True)
    #
    # def clean_fields(self, exclude=None):
    #     super().clean_fields(exclude)
    #     try:
    #         self.pages = self.parse()
    #     except ParseException as e:
    #         print(e)
    #         error = 'Could not parse {line} at line {lineno} column {col}.'\
    #             .format(line=e.line, lineno=e.lineno, col=e.col)
    #         raise ValidationError({'markup': [error]})

    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields=None):
    #     # clear existing pages before creating content
    #     self.contentpage_set.all().delete()
    #     # need to save to reference this object in ContentPage
    #     super().save(force_insert, force_update, using, update_fields)
    #
    #     for page_num in range(len(self.pages)):
    #         page = ContentPage.objects.create(challenge=self,
    #                                           order=page_num)
    #         for object_order in range(len(self.pages[page_num].content)):
    #             content_obj = self.pages[page_num].content[object_order]
    #             ContentSequenceItem.objects.create(content_object=content_obj,
    #                                                content_page=page,
    #                                                order=object_order)


# CONTAINERS

class Container(AbstractNamedObject):
    pass


class SectionContainer(AbstractLimitedVisibilityObject):
    """

    """
    section = models.ForeignKey(Section)
    container = models.ForeignKey('Container')
    open_on = models.DateTimeField(blank=True, null=True)
    due_on = models.DateTimeField(blank=True, null=True)
    order = models.SmallIntegerField(default=0)
    is_graded = models.BooleanField(default=False)

    class Meta:
        unique_together = ['section', 'container']

    def __str__(self):
        return '{section} {container}'.format(section=self.section, container=self.container)