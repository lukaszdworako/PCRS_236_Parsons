from django.http import HttpResponseRedirect


class OneToManyMixin(object):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        self.object = self.model.objects.get(pk=pk) if pk else None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = self.formset_class()
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset))

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        self.object = self.model.objects.get(pk=pk) if pk else None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = self.formset_class()

        # Form and formset objects are saved iff form and formset BOTH valid.
        if form.is_valid():
            self.object = form.save(commit=False)
            formset = self.formset_class(request.POST, instance=self.object)
            if formset.is_valid():
                return self.form_valid(form, formset)
        else:
            formset = self.formset_class(request.POST)
        return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        self.object = form.save()
        formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form,
                                                             formset=formset))
