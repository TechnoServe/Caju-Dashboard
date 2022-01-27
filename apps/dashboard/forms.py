# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from apps.authentication.models import RemUser, RemOrganization

ACTIVE = 1
INACTIVE = 0
Status = [
    (ACTIVE, 'Active'),
    (INACTIVE, 'Inactive'),
]


class UserBaseProfileForm(ModelForm):
    def clean(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError({"email": "Email exists"})

        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError({"username": "Username exists"})

        return self.cleaned_data

    class Meta:
        model = User
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "placeholder": "Username",
                    "class": "form-control",
                    "type": "text",
                    "id": "input-username",
                    "name": "username",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "placeholder": "E-mail",
                    "class": "form-control",
                    "type": "email",
                    "id": "input-email",
                    "name": "email_address",
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "First Name",
                    "class": "form-control",
                    "type": "text",
                    "id": "input-first-name",
                    "name": "first_name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Last Name",
                    "class": "form-control",
                    "type": "text",
                    "id": "input-last-name",
                    "name": "last_name",
                }
            ),
        }
        fields = [
            # 'username',
            # 'email',
            'first_name',
            'last_name'
        ]


class UserCustomProfileForm(ModelForm):
    organization = forms.ModelChoiceField(
        queryset=RemOrganization.objects.all().filter(status=ACTIVE),
        empty_label='Not Listed',
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
                'id': 'id_organization',
            }
        )
    )

    class Meta:
        model = RemUser
        widgets = {

            "email": forms.EmailInput(
                attrs={
                    "placeholder": "E-mail",
                    "class": "form-control",
                    "type": "email",
                    "id": "input-email",
                    "name": "email_address",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Phone Number",
                    "class": "form-control",
                    "type": "text",
                    "id": "input-phone",
                    "name": "phone",
                }
            ),
        }
        fields = ['email', 'phone', 'organization']
