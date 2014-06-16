from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import logout_then_login
from django.core.context_processors import csrf

import subprocess


def is_instructor(user):
    return user.is_instructor


def is_student(user):
    return user.is_student

def is_course_staff(user):
    return user.is_instructor or user.is_ta


def check_authorization(username, password):
    ''' Return True if user is authized on the university level, False othervise. '''
    if not settings.PRODUCTION:
        return True

    pwauth = subprocess.Popen("/usr/sbin/pwauth", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              close_fds=True)
    try:
        data = (username + "\n" + password + "\n").encode(encoding='ascii')
    except UnicodeEncodeError:
        return False
    pw_out = pwauth.communicate(input=data)[0]
    retcode = pwauth.wait()
    return retcode == 0


def login_view(request):
    """
        Check whether user is authorized to login and redirect, based on the group
        the user belongs to, to the corresponding start page.
    """

    NOTIFICATION = "False"
    NEXT = ""
    if 'next' in request.GET:
        NEXT = request.GET['next']

    if request.POST:

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if username != '':
            # university-level authentication
            existing_user = check_authorization(username, password)

            if not existing_user:
                NOTIFICATION = "username"
            else:
                # password-based authorization was provided at university level, 
                # just create a user object. 
                # user = authenticate(username=username, password=password)
                user = authenticate(username=username)

                if user is None:
                    NOTIFICATION = "djangoaccount"
                else: 
                    request.session['section'] = user.section
                    post_link = request.POST['next']
                    redirect_link = post_link or settings.SITE_PREFIX + '/content/quests'

                    login(request, user)
                    return HttpResponseRedirect(redirect_link)
    context = {'NEXT': NEXT, 'NOTIFICATION': NOTIFICATION}
    context.update(csrf(request))
    return render_to_response('users/login.html', context)


def logout_view(request):
    """ Log out the user using django logout and redirect them to the login page. """

    from pcrs.settings import LOGIN_URL
    return logout_then_login(request, login_url=LOGIN_URL)
