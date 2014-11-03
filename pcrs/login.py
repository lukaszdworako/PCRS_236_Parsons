from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import logout_then_login
from django.core.context_processors import csrf

import content.models
import users.models

#
import logging
import datetime
from django.utils.timezone import localtime, utc
#

import os
import subprocess


def is_instructor(user):
    return user.is_instructor


def is_student(user):
    return user.is_student


def is_course_staff(user):
    return user.is_instructor or user.is_ta


def check_authorization(username, password):
    ''' Return True if user is authized on the university level, False othervise. '''
    if settings.AUTH_TYPE == 'none':
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


def login_django(request, username):
    logger = logging.getLogger('activity.logging')
    logger.info(str(localtime(datetime.datetime.utcnow().replace(tzinfo=utc))) + " | " +
                str(username) + " | Log in")
    # password-based authorization was provided at university level, 
    # just create a user object. 
    # user = authenticate(username=username, password=password)
    user = authenticate(username=username)

    if user is None and settings.AUTOENROLL:
        user = users.models.PCRSUser.objects.create_user(username, False, section_id='123')
        user = authenticate(username=username)

    if user is None:
        # Automatic accounts not set up or creation failed.
        NOTIFICATION = "djangoaccount"
    if not user.is_active:
        NOTIFICATION = "user inactive"
    else:
        request.session['section'] = user.section
        redirect_link = settings.SITE_PREFIX + '/content/quests'

        login(request, user)
        return HttpResponseRedirect(redirect_link)

    # Actions is user cannot be logged in.
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

    if settings.AUTH_TYPE == "shibboleth":
        # user authenticated through shibboleth
        username = os.environ["utorid"]
        response = login_django(request, username)
        if response:
            return response

    # for settings.AUTH_TYPE == 'none' and settings.AUTH_TYPE == 'pwauth'
    if request.POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if username != '':
            # university-level authentication
            existing_user = check_authorization(username, password)

            if not existing_user:
                NOTIFICATION = "username"
            else:
                response = login_django(request, username)                
                if response:
                    return response

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
