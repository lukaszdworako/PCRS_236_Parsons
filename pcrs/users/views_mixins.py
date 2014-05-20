from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator

from login import is_instructor, is_course_staff


class ProtectedViewMixin:
    """
    A mixin for decorating a class based view to require a user to be logged in.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProtectedViewMixin, self).dispatch(*args, **kwargs)

    def get_visible_problems(self, request):
        problem_class = self.model.get_problem_class()
        if request.user.is_student:
            return problem_class.objects.filter(visibility='open')
        if request.user.is_ta:
            return problem_class.objects.exclude(visibility='closed')
        else:
            return problem_class.objects.all()


class InstructorViewMixin(ProtectedViewMixin):
    """
    A mixin for decorating a class based view to require a user to be logged in
    and to be an instructor.
    """
    @method_decorator(login_required)
    @method_decorator(user_passes_test(is_instructor))
    def dispatch(self, *args, **kwargs):
        return super(InstructorViewMixin, self).dispatch(*args, **kwargs)


class CourseStaffViewMixin(ProtectedViewMixin):
    """
    A mixin for decorating a class based view to require a user to be logged in.
    """
    @method_decorator(login_required)
    @method_decorator(user_passes_test(is_course_staff))
    def dispatch(self, *args, **kwargs):
        return super(CourseStaffViewMixin, self).dispatch(*args, **kwargs)