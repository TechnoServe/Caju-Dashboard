# -*- encoding: utf-8 -*-
"""
Copyright (c) 2021 - present Technoserve x Damilola
"""

import datetime
import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from .forms import *
# Create your views here.
from django.shortcuts import render, redirect
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext
from .forms import SignUpForm, LoginForm
from django.db.models.signals import post_save

from . import forms as custom_forms
from .models import RemUser
from .utils import account_activation_token
import os

logger = logging.getLogger(__name__)


def signin(request):
    msg = None
    if request.user.is_authenticated:
        return redirect("/dashboard/")

    elif request.method == "POST":
        form = LoginForm(data=request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            remember_me = form.cleaned_data.get("remember_me")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if remember_me:
                    request.session.set_expiry(604800)
                return redirect("/dashboard/")
            else:
                msg = gettext('Invalid credentials')

        else:
            msg = str(form.errors)  # 'Error validating the form'
    else:
        form = LoginForm()

    return render(request, "authentication/login.html", {"form": form, "msg": msg, 'segment': 'login'})


def signup(request):
    msg = None
    success = False
    fullpage = not (request.user.is_staff or request.user.is_superuser)

    try:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False

                email = form.cleaned_data.get("email")
                phone = form.cleaned_data.get("phone")
                organization = form.cleaned_data.get("organization")
                role = form.cleaned_data.get("role")

                current_site = get_current_site(request)
                mail_subject = gettext(
                    'Activate your Cashew Remote Sensing account.')
                message = loader.get_template('authentication/acc_active_email.html').render(
                    {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                    }
                )
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(
                    mail_subject,
                    message,
                    from_email='"Caju-Lab Support" <' +
                    os.getenv("EMAIL_HOST_USER") + '>',
                    to=[to_email]
                )
                email.content_subtype = "html"

                email.send()

                msg = gettext(
                    'Please confirm your email address to complete the registration')
                success = True

                user.save()

                rem_user = RemUser.objects.get(user=user)
                rem_user.email = email
                rem_user.phone = phone
                rem_user.organization = organization
                rem_user.role = role
                rem_user.save()

            else:
                msg = gettext('Form is not valid')
        else:
            form = SignUpForm()
        return render(request, 'authentication/register.html', {"form": form, "msg": msg, "success": success, "fullpage": fullpage})

    except Exception as e:
        print(e)
        print(os.getenv("EMAIL_HOST_USER"))
        msg = gettext('An Error has Occurred')
        return render(request, 'authentication/register.html', {"form": form, "msg": msg, "success": False, "fullpage": fullpage})


@login_required(login_url="/")
def register_org(request):
    msg = None
    success = False

    if request.method == "POST":
        form = RegisterOrganization(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            try:
                current_user = request.user
                if current_user.is_authenticated:
                    # Do something for authenticated users.
                    obj.created_by = current_user.id
                    obj.created_date = datetime.datetime.now()
                    obj.updated_by = current_user.id
                    obj.updated_date = datetime.datetime.now()

                    # return redirect("/login/")
            except:
                print("")

            obj.save()
            msg = gettext(
                'Organization created - please <a href="/register">register user</a>.')
            success = True

        else:
            msg = gettext('Form is not valid')
    else:
        form = RegisterOrganization()

    return render(request, "authentication/register_org.html", {"form": form, "msg": msg, "success": success})


def register_user_full(request):
    msg = None
    success = False

    if request.method == "POST":
        form = FullSignUpForm(request.POST)
        if form.is_valid():

            raw_password1 = form.cleaned_data.get("password1")
            raw_password2 = form.cleaned_data.get("password2")

            if raw_password1 == raw_password2:
                current_user = request.user
                # id = uuid.uuid4().int
                obj = form.save(commit=False)
                obj.created_by = current_user.id
                obj.created_date = datetime.datetime.now()
                obj.updated_by = current_user.id
                obj.updated_date = datetime.datetime.now()

                org_name = form.cleaned_data.get("organization_name")
                obj.organization = org_name

                email = form.cleaned_data.get("email")
                obj.e_mail = email

                # obj.id = id

                obj.password = raw_password1

                obj.save()
                # username = form.cleaned_data.get("username")
                # raw_password = form.cleaned_data.get("password1")
                # user = authenticate(username=username, password=raw_password)

                user_name = form.cleaned_data.get("user_name")
                email = form.cleaned_data.get("email")

                sec_user = User(username=user_name, email=email)
                sec_user.set_password(raw_password1)

                sec_user.save()

                msg = 'User created - please <a href="/login">login</a>.'
                success = True

                # return redirect("/login/")

            else:
                msg = gettext('Form is not valid - Passwords do not match')

        else:
            msg = gettext('Form is not valid')
    else:
        form = FullSignUpForm()

    return render(request, "authentication/full_login.html", {"form": form, "msg": msg, "success": success})


def signout(request):
    logout(request)
    msg = None

    if request.method == "POST":
        form = LoginForm(data=request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            remember_me = form.cleaned_data.get("remember_me")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if remember_me:
                    request.session.set_expiry(604800)
                return redirect("/")
            else:
                msg = gettext('Invalid credentials')

        else:
            msg = str(form.errors)  # 'Error validating the form'
    else:

        form = LoginForm()

    return render(request, "authentication/login.html", {"form": form, "msg": msg, 'segment': 'login'})


def forgot_password(request):
    msg = None
    success = False

    if request.method == 'POST':
        form = custom_forms.ForgotPassword(request.POST)
        if form.is_valid():

            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            current_site = get_current_site(request)
            mail_subject = gettext('Reset your Password')
            message = loader.get_template('authentication/password_reset_email.html').render(
                {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }
            )
            # message = render_to_string('authentication/acc_active_email.html', {
            #     'user': user,
            #     'domain': current_site.domain,
            #     'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            #     'token':account_activation_token.make_token(user),
            # })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject,
                message,
                from_email='"Caju-Lab Support" <cajusupport@tnslabs.org>',
                to=[to_email]
            )
            email.content_subtype = "html"

            email.send()

            msg = gettext("We have emailed you instructions for setting your password. \
                        If an account exists with the email you have entered, you should receive them shortly.\
                        If you do not receive an email, please make sure you've entered the address you registered with correctly, \
                        and check your spam folder.")
            success = True
            # return HttpResponse('Please confirm your email address to complete the registration')
        else:
            msg = gettext('Form is not valid')
    else:
        form = custom_forms.ForgotPassword()
    return render(request, 'authentication/password_reset_form.html', {"form": form, "msg": msg, "success": success})


def password_reset_confirm(request, uidb64, token):
    context = {}
    try:
        # uid = force_str(urlsafe_base64_decode(uidb64))
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):

        msg = None
        success = False

        if request.method == 'POST':

            form = custom_forms.NewPassword(request.POST)

            if form.is_valid():

                password = form.cleaned_data.get("password")
                user.set_password(password)

                user.save()

                msg = gettext('Password change successful. Now you can')
                success = True
                # return HttpResponse('Please confirm your email address to complete the registration')
            else:
                msg = gettext('Form is not valid')
        else:
            form = custom_forms.NewPassword()
        return render(request, 'authentication/new_password.html', {"form": form, "msg": msg, "success": success})
    else:
        html_template = loader.get_template(
            'authentication/password_change_failed.html')
        return HttpResponse(html_template.render(context, request))


def activate(request, uidb64, token):
    context = {}
    try:
        # uid = force_str(urlsafe_base64_decode(uidb64))
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # login(request, user)
        html_template = loader.get_template(
            'authentication/email_confirmed.html')
        return HttpResponse(html_template.render(context, request))
    else:
        html_template = loader.get_template(
            'authentication/email_confirm_invalid.html')
        return HttpResponse(html_template.render(context, request))
