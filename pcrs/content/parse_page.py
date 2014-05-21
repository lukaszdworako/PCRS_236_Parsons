from django.contrib.contenttypes.models import ContentType
from pyparsing import (CaselessKeyword, OneOrMore, Suppress, Word, ZeroOrMore,
                       alphanums, nums, originalTextFor,
                       Group, Literal)
from .models import ContentProblem, TextBlock, Video


def parameter(parser):
    """
    Return a parser the parses parameters.
    """
    return Suppress('_{').leaveWhitespace() + parser + Suppress('}')


def create_content_problem(start, location, tokens):
    app_label = 'problems_{}'.format(tokens.type)
    problem_content_type = ContentType.objects.get(app_label=app_label,
                                                   model='problem')
    problem = problem_content_type.get_object_for_this_type(pk=tokens.pk)
    return ContentProblem.objects.create(content_object=problem, is_graded=True)


def create_text_block(tokens):
    return TextBlock.objects.create(text=tokens[0])

pk = Word(nums)('pk')

problem_type = (Literal('code') | Literal('multiple_choice'))('type')
problem = (CaselessKeyword('\\problem', identChars=alphanums) +
           parameter(problem_type + pk)).setParseAction(create_content_problem)


video = (CaselessKeyword('\\video', identChars=alphanums) +
         parameter(pk)).setParseAction(lambda s, l, t: (t.pk))

text = originalTextFor(OneOrMore(Word(alphanums))).addParseAction(create_text_block)

content = Group(ZeroOrMore(problem | video | text))('content')

page = (Suppress(CaselessKeyword('\\page', identChars=alphanums)) +
        parameter(Word(alphanums)('name')))
page_end = Suppress(CaselessKeyword('\\end'))

content = ZeroOrMore(Group(page + content + page_end))


def parse(instring):
    return content.parseString(instring, parseAll=True)


if __name__ == '__main__':
    print(content.parseString(
        '\\page_{foo} aert \problem_{code 1} sdfg \end \\page_{foo} aert \problem_{code 1} sdfg \end',
        parseAll=True)[1].content.dump())
    # print(content.parseString('\problem_{coding 1} sdfg'))
    # print(content.parseString(' df  df \problem_{mc 1}'))
    # print(content.parseString('\problem_{mc 1}'))
    # print(content.parseString('dsf \\video_{100} d d'))