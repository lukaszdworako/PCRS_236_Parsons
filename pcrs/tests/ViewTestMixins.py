from users.models import Section, PCRSUser


class UsersMixin:
    def setUp(self):
        self.section = Section.objects.create(pk=1, lecture_time='10-11',
                                              location='SS')
        self.instructor = PCRSUser.objects.create(username='instructor',
                                                  is_instructor=True)
        self.ta = PCRSUser.objects.create(username='ta',
                                          is_ta=True)
        self.student = PCRSUser.objects.create(username='student',
                                               is_instructor=False,
                                               is_student=True, section=self.section)


class InstructorViewTestMixin(UsersMixin):
    def setUp(self):
        UsersMixin.setUp(self)
        self.client.login(username='instructor')

    def test_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)
        self.assertTemplateUsed('login')

    def test_instructor_access(self):
        self.client.login(username='instructor')
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_ta_access(self):
        self.client.login(username='ta')

        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)
        self.assertTemplateUsed('login')

        response = self.client.post(self.url, {})
        self.assertEqual(302, response.status_code)
        self.assertTemplateUsed('login')

    def test_student_access(self):
        self.client.login(username='student')

        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)
        self.assertTemplateUsed('login')

        response = self.client.post(self.url, {})
        self.assertEqual(302, response.status_code)
        self.assertTemplateUsed('login')


class CourseStaffViewTestMixin(UsersMixin):
    def setUp(self):
        UsersMixin.setUp(self)
        self.client.login(username='ta')

    def test_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)
        self.assertTemplateUsed('login')

    def test_instructor_access(self):
        self.client.login(username='instructor')
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_ta_get(self):
        self.client.login(username='ta')

        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_student_access(self):
        self.client.login(username='student')

        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)
        self.assertTemplateUsed('login')

        response = self.client.post(self.url, {})
        self.assertEqual(302, response.status_code)
        self.assertTemplateUsed('login')


class ProtectedViewTestMixin(UsersMixin):
    def setUp(self):
        UsersMixin.setUp(self)
        self.client.login(username='instructor')

    def test_not_logged_in(self):
        self.client.logout()

        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)
        self.assertTemplateUsed('login')

        response = self.client.post(self.url, {})
        self.assertEqual(302, response.status_code)
        self.assertTemplateUsed('login')

    def test_instructor_access(self):
        self.client.login(username='instructor')
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_ta_get(self):
        self.client.login(username='ta')
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_student_get(self):
        self.client.login(username='student')
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)