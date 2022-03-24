# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import datetime
from datetime import date

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import RemUser, RemOrganization
from .db_conn_string import __mysql_disconnect__, __close_ssh_tunnel__, __open_ssh_tunnel__, __mysql_connect__

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


class DateInput(forms.DateInput):
    input_type = 'date'


current_time = datetime.datetime.now()
dates0 = str(date(year=current_time.year - 1, month=current_time.month, day=current_time.day))
dates = str(date.today())


class KorDateForm(forms.Form):
    my_date_field = forms.DateField(label=_("From"), initial=dates0, widget=DateInput)
    my_date_field1 = forms.DateField(label=_("To"), initial=dates, widget=DateInput)


__open_ssh_tunnel__()
cur = __mysql_connect__().cursor()
country = "Benin"
query = "SELECT kor,location_region,location_country FROM free_qar_result WHERE location_country=%s"
cur.execute(query, (country,))
__mysql_disconnect__()
__close_ssh_tunnel__()

infos = []
for kor in cur:
    for location_region in cur:
        infos.append(location_region)

infos1 = sorted(infos, key=lambda name: name[1])

names_with_duplicate = []
for x in infos1:
    names_with_duplicate.append(x[1])

y = 0
while len(names_with_duplicate) > y:
    if "Department" in names_with_duplicate[y]:
        names_with_duplicate[y] = names_with_duplicate[y].replace(" Department", "")
    else:
        pass
    y += 1

names_sorted = list(set(names_with_duplicate))
names_sorted = sorted(names_sorted)

DEPARTMENT_CHOICES = [tuple([x[0].lower() + x[1:], x.capitalize()]) for x in names_sorted]
lower_depselct = _('select department')
upper_depselct = _('Select Department')
select0 = (str(lower_depselct), str(upper_depselct))
DEPARTMENT_CHOICES.insert(0, select0)


class DepartmentChoice(forms.Form):
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES)
