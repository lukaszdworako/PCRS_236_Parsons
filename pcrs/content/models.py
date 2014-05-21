from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models

from pyparsing import (CaselessKeyword, OneOrMore, Suppress, Word, ZeroOrMore,
                       alphanums, nums, originalTextFor,
                       Group, Literal, ParseException)

from pcrs.models import (AbstractNamedObject, AbstractGenericObjectForeignKey,
                         AbstractOrderedGenericObjectSequence,
                         AbstractSelfAwareModel)
from users.models import AbstractLimitedVisibilityObject


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


class ContentProblem(AbstractGenericObjectForeignKey):
    objects = models.Q(model='problem')
    is_graded = models.BooleanField()

    def is_completed(self, user):
        pass


class Challenge(AbstractSelfAwareModel, AbstractLimitedVisibilityObject,
                AbstractNamedObject):
    """
    A Challenge is a sequence of ContentPages, which are defined in markup.
    """
    markup = models.TextField()

    ordered = generic.GenericRelation('OrderedContainerItem',
                               content_type_field='child_content_type',
                               object_id_field='child_object_id', related_name='challenges')

    pages = None

    class Meta:
        ordering = ['ordered__order']

    def get_absolute_url(self):
        return '/content/challenge/{}'.format(self.pk)

    def get_first_page(self):
        return '{}/0'.format(self.get_absolute_url())

    def get_main_page(self):
        return '{}/go'.format(self.get_absolute_url())

    def get_all_problems(self):
        pages = self.contentpage_set.all()
        problem_type = ContentType.objects.filter(model='contentproblem')
        problems = [problem.content_object.content_object
                    for page in pages
                    for problem in page.contentsequenceitem_set.all()
                                       .filter(content_type__in=problem_type)]
        return problems

    def get_required(self):
        pass

    def get_optional(self):
        pass

    def parse(self):
        def parameter(parser):
            """
            Return a parser the parses parameters.
            """
            return Suppress('_{').leaveWhitespace() + parser + Suppress('}')

        def create_content_problem(start, location, tokens):
            app_label = 'problems_{}'.format(tokens.type)
            problem_content_type = ContentType.objects.get(app_label=app_label,
                                                           model='problem')
            problem_object = problem_content_type.\
                get_object_for_this_type(pk=tokens.pk)
            is_graded = (tokens[0] == '\summative')
            return ContentProblem.objects.create(content_object=problem_object,
                                                 is_graded=is_graded)

        def create_text_block(tokens):
            return TextBlock.objects.create(text=tokens[0])

        pk = Word(nums)('pk')

        problem_type = (Literal('code') | Literal('multiple_choice'))('type')
        p_kw = (CaselessKeyword('\\summative', identChars=alphanums) |
                CaselessKeyword('\\formative', identChars=alphanums))
        problem = (p_kw +
                   parameter(problem_type + pk)).setParseAction(create_content_problem)

        video = (CaselessKeyword('\\video', identChars=alphanums) +
                 parameter(pk)).setParseAction(lambda s, l, t: (t.pk))

        text = originalTextFor(OneOrMore(Word(alphanums))).addParseAction(
            create_text_block)

        content = Group(ZeroOrMore(problem | video | text))('content')

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


    # def get_grade_report(self):
    #     # get problems
    #     objects = self.contentsequence_set.filter(
    #         content_type__model='contentproblem')
    #     for o in objects:
    #         problem = o.content_object.content_object
    #         if problem.is_graded:
    #             print(problem.best_per_student_before_time())
    #             pass


class ContentPage(models.Model):
    challenge = models.ForeignKey(Challenge)
    order = models.SmallIntegerField()

    def __str__(self):
        return '{name}:{order}'.format(name=self.challenge.name,
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


class ContentSequenceItem(AbstractOrderedGenericObjectSequence):
    """
    A content objects to be displayed on some page.
    """
    objects = (models.Q(model='contentproblem') |
               models.Q(model='video') | models.Q(model='textblock'))

    content_page = models.ForeignKey(ContentPage)

    def __str__(self):
        return 'challenge: {0}; content_type: {1}, id:{2}'\
            .format(self.content_page.pk, self.content_type, self.object_id)


class Container(AbstractLimitedVisibilityObject, AbstractNamedObject):
    """
    A container of Containers or Challenges.
    """
    open_on = models.DateTimeField(blank=True, null=True)
    due_on = models.DateTimeField(blank=True, null=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False,
                                           blank=True, null=True)
    parents = generic.GenericRelation('OrderedContainerItem',
                               content_type_field='child_content_type',
                               object_id_field='child_object_id', related_name='parents')

    children = generic.GenericRelation('OrderedContainerItem',
                               content_type_field='parent_content_type',
                               object_id_field='parent_object_id', related_name='children')

    # def get_challenges(self):
    #     challenge_pks = OrderedContainerItem.objects\
    #         .filter(parent_object_id=self.pk)\
    #         .filter(child_content_type=models.Q(model='challenge'))\
    #         .values_list('child_object_id', flat=True)
    #     return Container.objects.filter(pk__in=set(challenge_pks))

    def _get_children_container_pks(self):
        container_type = ContentType.objects.get_for_model(self)

        pks = OrderedContainerItem.objects\
            .filter(parent_object_id=self.pk,
                    child_content_type=container_type.id)\
            .values_list('child_object_id', flat=True)
        return set(pks)

    def get_children_containers(self):
        pks = self._get_children_container_pks()
        return Container.objects.filter(pk__in=pks)

    def _get_children_challenge_pks(self):
        container_type = ContentType.objects.get(model='challenge')
        # print ('type:',container_type)
        pks = OrderedContainerItem.objects\
            .filter(parent_object_id=self.pk,
                    child_content_type=container_type.id)\
            .values_list('child_object_id', flat=True)
        return set(pks)

    def get_children_challenges(self):
        pks = self._get_children_challenge_pks()
        return Challenge.objects.filter(pk__in=pks)


class OrderedContainerItem(models.Model):
    parents = models.Q(model='container')
    children = models.Q(model='container') | models.Q(model='challenge')

    parent_object_id = models.PositiveIntegerField()
    parent_content_type = models.ForeignKey(ContentType,
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
        # order_with_respect_to = 'parent_object_id'

    def __str__(self):
        return '{0}->{1}'.format(
            self.parent_content_object, self.child_content_object
        )


class ProblemSetProblem(AbstractGenericObjectForeignKey):
    problem_set = models.ForeignKey('ProblemSet')
    objects = models.Q(model='problem')


class ProblemSet(AbstractNamedObject, AbstractSelfAwareModel):
    def get_absolute_url(self):
        return '/content/problem_set/{}'.format(self.pk)

    def get_main_page(self):
        return '{}/list'.format(self.get_absolute_url())

    def get_problems_for_type(self, app_label):
        content_type = ContentType.objects.get(app_label=app_label,
                                               model='problem')
        return ProblemSetProblem.objects.filter(problem_set=self,
                                                content_type= content_type)
