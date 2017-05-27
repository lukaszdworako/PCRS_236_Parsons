from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import logout_then_login
from django.core.context_processors import csrf

import content.models
import users.models

import logging
import datetime
from django.utils.timezone import localtime, utc

import os
import subprocess


def is_instructor(user):
    return user.is_instructor


def is_student(user):
    return user.is_student


def is_course_staff(user):
    return user.is_instructor or user.is_ta


def check_authorization(username, password):
    ''' Return True if user can be authorized and False otherwise.
    '''
    # AUTH_TYPE 'shibboleth' does not use this function
    if settings.AUTH_TYPE in ('none', 'pass'):
        # 'none' does no authentication, 'pass' will authenticate on user object creation
        return True
    # else settings.AUTH_TYPE == 'pwauth'
    pwauth = subprocess.Popen("/usr/sbin/pwauth", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              close_fds=True)
    try:
        data = (username + "\n" + password + "\n").encode(encoding='ascii')
    except UnicodeEncodeError:
        return False
    pw_out = pwauth.communicate(input=data)[0]
    retcode = pwauth.wait()
    return retcode == 0


def login_django(request, username):
    logger = logging.getLogger('activity.logging')
    logger.info(str(localtime(datetime.datetime.utcnow().replace(tzinfo=utc))) + " | " +
                str(username) + " | Log in")

    if settings.AUTH_TYPE == 'pass':
        passwd = request.POST.get('password', '')
        user = authenticate(username=username, password=passwd)
    else:  # AUTH_TYPEs 'none', 'pwauth', and 'shibboleth'
        user = authenticate(username=username)

    if user is None:
        # Automatic accounts not set up or creation failed.
        NOTIFICATION = "djangoaccount"
    elif not user.is_active:
        NOTIFICATION = "user inactive"
    else:
        request.session['section'] = user.section
        redirect_link = settings.SITE_PREFIX + '/content/quests'

        # Using meta data from request get next parameter
        previous_url = request.META.get('HTTP_REFERER')
        if previous_url:
            index = previous_url.find("next=")
            # Build new redirect_link
            if index >= 0:
                previous_url = previous_url[index + 5:]
                redirect_link = settings.SITE_PREFIX + previous_url

        login(request, user)
        return HttpResponseRedirect(redirect_link)

    # Actions if user cannot be logged in.
    if settings.AUTH_TYPE == 'shibboleth':
        # redirect user letting them know they do not belong to this server
        redirect_link = settings.SITE_PREFIX + '/usernotfound.html'
        return HttpResponseRedirect(redirect_link)

    return None

def login_view(request):
    """
        Check whether user is authorized to login and redirect, based on the group
        the user belongs to, to the corresponding start page.
    """

    NOTIFICATION = "False"
    NEXT = ""
    if 'next' in request.GET:
        NEXT = request.GET['next']
    if request.user and request.user.is_authenticated():
        return HttpResponseRedirect(NEXT or settings.SITE_PREFIX + '/content/quests')

    # AUTH_TYPE 'shibboleth' uses an environment variable instead of check_authorization
    if settings.AUTH_TYPE == "shibboleth":
        username = os.environ["utorid"]
        response = login_django(request, username)
        if response:
            return response

    # AUTH_TYPEs 'pwauth', 'pass', and 'none'
    elif request.POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if username != '':
            existing_user = check_authorization(username, password)

            if not existing_user:
                NOTIFICATION = "username"
            else:
                response = login_django(request, username)
                if response:
                    return response

    # Failed logins and GET requests
    context = {'NEXT': NEXT, 'NOTIFICATION': NOTIFICATION}
    context.update(csrf(request))
    return render_to_response('users/login.html', context)


def logout_view(request):
    """ Log out the user using django logout and redirect them to the login page. """
    user = getattr(request, 'user', None)
    logger = logging.getLogger('activity.logging')
    logger.info(str(localtime(datetime.datetime.utcnow().replace(tzinfo=utc))) + " | " +
            str(user) + " | Log out")
    from pcrs.settings import LOGIN_URL
    return logout_then_login(request, login_url=LOGIN_URL)
