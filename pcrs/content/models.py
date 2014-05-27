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
from users.models import AbstractLimitedVisibilityObject, PCRSUser


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
    GRADE_MODES = (('attempt', 'Attempt ALL'), ('complete', 'Complete ALL'))
    grade_mode = models.CharField(max_length=10, choices=GRADE_MODES,
                                  blank=True)

    @property
    def gradable_item_set(self):
        raise NotImplementedError('Must be implemented by subclasses.')

    class Meta:
        abstract = True
        ordering = ['ordered__order']

    def was_completed(self, user):
        """
        Return True iff the user completed all complete-able objects based on
        the definition of completion.
        """
        if self.grade_mode == 'complete':
            return self._was_completed(self, user)
        elif self.grade_mode == 'attempt':
            return self._was_attmepted(self, user)
        else:
            return True

    def _was_completed(self, user):
        sequence_items = self.gradable_item_set.all()
        return all(item.content_object.was_completed(user)
                   for item in sequence_items)

    def _was_attempted(self, user):
        sequence_items = self.gradable_item_set.all()
        return all(item.content_object.was_attempted(user)
                   for item in sequence_items)

    # def get_number_completed(self, user):
    #     """
    #     Return the number of complete-able objects that the user has completed
    #     based on the definition of completion.
    #     """
    #     sequence_items = self.gradable_item_set.all()
    #     if self.grade_mode == 'complete':
    #         return sum([int(item.content_object.was_completed(user))
    #                     for item in sequence_items])
    #     elif self.grade_mode == 'attempt':
    #         return sum([int(item.content_object.was_attempted(user))
    #                     for item in sequence_items])
    #     else:
    #         return None
    def get_number_completed(self, user):
        """
        Return the number of complete-able objects that the user has completed
        based on the definition of completion.
        """
        problems = self.get_problem_set()
        if self.grade_mode == 'complete':
            return sum(ct.model_class().get_number_attempted(user)
                       for ct in ContentType.objects.filter(model='problem'))
        elif self.grade_mode == 'attempt':
            return sum(ct.model_class().get_number_attempted(user)
                       for ct in ContentType.objects.filter(model='problem'))
        else:
            return None


class ContentSequenceItem(AbstractOrderedGenericObjectSequence):
    """
    A content objects to be displayed on some page.
    """
    objects = (models.Q(model='problem') |
               models.Q(model='video') | models.Q(model='textblock'))

    content_page = models.ForeignKey('ContentPage')

    def __str__(self):
        return 'challenge: {0}; content_type: {1}, id:{2}'\
            .format(self.content_page.pk, self.content_type, self.object_id)


class ContentPage(models.Model):
    """
    A page displaying a sequence of ContentSequenceItems.
    """
    challenge = models.ForeignKey('Challenge')
    order = models.SmallIntegerField()

    @property
    def gradable_item_set(self):
        # only include Problems as gradable objects
        return self.contentsequenceitem_set

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
class ProblemSetProblem(AbstractGenericObjectForeignKey):
    problem_set = models.ForeignKey('ProblemSet')
    objects = models.Q(model='problem')


class ProblemSet(GradableObjectContainer):
    ordered = generic.GenericRelation('OrderedContainerItem',
                               content_type_field='child_content_type',
                               object_id_field='child_object_id',
                               related_name='problemset')

    @property
    def gradable_item_set(self):
        return self.problemsetproblem_set

    def get_absolute_url(self):
        return '/content/problem_set/{}'.format(self.pk)

    def get_main_page(self):
        return '{}/list'.format(self.get_absolute_url())

    def get_problems_for_type(self, app_label):
        content_type = ContentType.objects.get(app_label=app_label,
                                               model='problem')
        return ProblemSetProblem.objects.filter(problem_set=self,
                                                content_type=content_type)

    def get_problem_set(self):
        return {
            (item.app_label, item.object_id)
            for item in self.gradable_item_set.all()
        }


# challenges
class Challenge(GradableObjectContainer):
    """
    A Challenge is a sequence of ContentPages, which are defined in markup.
    """
    markup = models.TextField()

    ordered = generic.GenericRelation('OrderedContainerItem',
                               content_type_field='child_content_type',
                               object_id_field='child_object_id',
                               related_name='challenges')

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


    def parse(self):
        def parameter(parser):
            """
            Return a parser the parses parameters.
            """
            return Suppress('_{').leaveWhitespace() + parser + Suppress('}')

        # def create_content_problem(start, location, tokens):
        #     app_label = 'problems_{}'.format(tokens.type)
        #     problem_content_type = ContentType.objects.get(app_label=app_label,
        #                                                    model='problem')
        #     problem_object = problem_content_type.\
        #         get_object_for_this_type(pk=tokens.pk)
        #     is_graded = (tokens[0] == '\summative')
        #     return ContentProblem.objects.create(content_object=problem_object,
        #                                          is_graded=is_graded)

        def create_text_block(tokens):
            return TextBlock.objects.create(text=tokens[0])

        pk = Word(nums)('pk')

        problem_type = (Literal('code') | Literal('multiple_choice'))('type')
        p_kw = (CaselessKeyword('\\summative', identChars=alphanums) |
                CaselessKeyword('\\formative', identChars=alphanums))
        # problem = (p_kw +
        #            parameter(problem_type + pk)).setParseAction(create_content_problem)

        video = (CaselessKeyword('\\video', identChars=alphanums) +
                 parameter(pk)).setParseAction(lambda s, l, t: (t.pk))

        text = originalTextFor(OneOrMore(Word(alphanums))).addParseAction(
            create_text_block)

        content = Group(ZeroOrMore(text))('content')

        page = Suppress(CaselessKeyword('\\page'))
        page_end = Suppress(CaselessKeyword('\\end'))

        content = ZeroOrMore(Group(page + content + page_end))

        return content.parseString(self.markup, parseAll=True)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)
        try:
            self.pages = self.parse()
        except ParseException as e:
            print(e)
            error = 'Could not parse {line} at line {lineno} column {col}.'\
                .format(line=e.line, lineno=e.lineno, col=e.col)
            raise ValidationError({'markup': [error]})

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # clear existing pages before creating content
        self.contentpage_set.all().delete()
        # need to save to reference this object in ContentPage
        super().save(force_insert, force_update, using, update_fields)

        for page_num in range(len(self.pages)):
            page = ContentPage.objects.create(challenge=self,
                                              order=page_num)
            for object_order in range(len(self.pages[page_num].content)):
                content_obj = self.pages[page_num].content[object_order]
                ContentSequenceItem.objects.create(content_object=content_obj,
                                                   content_page=page,
                                                   order=object_order)


    def get_grade_report(self):
        # get problems
        objects = self.contentsequence_set.filter(
            content_type__model='contentproblem')
        for o in objects:
            problem = o.content_object.content_object
            if problem.is_graded:
                print(problem.best_per_user_before_time())
                pass


# CONTAINERS

class Container(AbstractLimitedVisibilityObject, AbstractNamedObject,
                AbstractSelfAwareModel):
    """
    An ordered collection of Containers or ProblemContainers.
    """
    open_on = models.DateTimeField(blank=True, null=True)
    due_on = models.DateTimeField(blank=True, null=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False,
                                           blank=True, null=True)

    ordered = generic.GenericRelation('OrderedContainerItem',
                               content_type_field='child_content_type',
                               object_id_field='child_object_id',
                               related_name='containers')

    children = generic.GenericRelation('OrderedContainerItem',
                               content_type_field='parent_content_type',
                               object_id_field='parent_object_id',
                               related_name='children')

    @classmethod
    def get_root_containers(cls, queryset):
        """
        Return the Containers that have no parents.
        """
        # get ids of the Containers that are children
        # children_containers_pks = queryset\
        #     .filter(child_content_type=cls.get_content_type())\
        #     .values_list('child_object_id', flat=True)
        # include only top-level containers, i.e. those that have no parent
        return OrderedContainerItem.objects.filter(parent_object_id__isnull=True)

    def get_non_leaf_children_containers(self, queryset):
        """
        Return the Containers that are children of this Container.
        """
        return [
            leaf.child_content_object
            for leaf in queryset\
                .filter(parent_content_type=self.get_content_type(),
                        parent_object_id=self.pk)\
                .filter(child_content_type=self.get_content_type())
        ]

    def get_leaf_containers(self, queryset):
        """
        Return the content object of ContainerItem objects that are children
        of this Container and have themselves no children.
        """
        # only objects that are not Containers are leaves
        return [
            leaf.child_content_object
            for leaf in queryset\
                .filter(parent_content_type=self.get_content_type(),
                        parent_object_id=self.pk)\
                .filter(~Q(child_content_type=self.get_content_type()))
        ]


class OrderedContainerItem(models.Model):
    parents = models.Q(model='container')
    children = (models.Q(model='container') |
                models.Q(model='challenge') |
                models.Q(model='problemset'))

    parent_object_id = models.PositiveIntegerField(null=True)
    parent_content_type = models.ForeignKey(ContentType, null=True,
                                            limit_choices_to=parents,
                                            related_name='parent')
    parent_content_object = generic.GenericForeignKey('parent_content_type',
                                                      'parent_object_id')

    child_object_id = models.PositiveIntegerField()
    child_content_type = models.ForeignKey(ContentType,
                                           limit_choices_to=children, related_name='child')
    child_content_object = generic.GenericForeignKey('child_content_type',
                                                     'child_object_id')
    order = models.SmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        # index_together =
        # order_with_respect_to = 'parent_object_id'

    def __str__(self):
        # return '{0}->{1}'.format(
        #     self.parent_content_object, self.child_content_object
        # )
        return 'foo'


