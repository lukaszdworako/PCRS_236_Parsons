from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django import forms
from pcrs.form_mixins import CrispyFormMixin, BaseRelatedObjectForm

from problems_rdb.models import Dataset, Schema
from problems_sql.models import TestCase


class SchemaForm(CrispyFormMixin, forms.ModelForm):
    """
    Form for entering the details of a Schema.
    """
    save_and_add_ds = Submit('submit', 'Save and add datasets',
                             css_class='btn-success pull-right',
                             formaction='create_and_add_dataset')

    class Meta:
        model = Schema
        fields = ('name', 'definition')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Fieldset('', *self.Meta.fields),
            ButtonHolder(self.save_and_add_ds, css_class='pull-right')
        )


class DatasetForm(BaseRelatedObjectForm):
    """
    Form for entering the details of a Dataset.
    """

    class Meta:
        model = Dataset
        fields = ('schema', 'name', 'definition')
        widgets = {'schema': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        BaseRelatedObjectForm.__init__(self, *args, formaction='datasets',
                                       **kwargs)


class RDBTestCaseForm(BaseRelatedObjectForm):
    """
    Form for creating an RDB testcase.
    """
    class Meta:
        model = TestCase
        widgets = {'problem': forms.HiddenInput()}
        fields = ('dataset', 'problem')

    def __init__(self, *args, **kwargs):
        schema = kwargs.pop('schema', None)
        BaseRelatedObjectForm.__init__(self, *args, formaction='testcases',
                                       **kwargs)
        # limit the options to the datasets within the schema for the problem
        # for which the testcase is created
        self.fields['dataset'].queryset = Dataset.objects.filter(schema=schema)