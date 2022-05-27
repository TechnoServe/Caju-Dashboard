# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import datetime
from datetime import date, time

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TimeInput
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import RemUser, RemOrganization
from . import models
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
    my_date_field = forms.DateField(
        label=_("From"),
        required=False,
        initial=dates0,
        widget=DateInput(
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
            }
        )
    )
    my_date_field1 = forms.DateField(
        label=_("To"),
        required=False,
        initial=dates,
        widget=DateInput(
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
            }
        )
    )


__open_ssh_tunnel__()
cur = __mysql_connect__().cursor()
country = "Benin"
query = "SELECT kor,location_region,location_sub_region,location_country FROM free_qar_result WHERE location_country=%s"
cur.execute(query, (country,))
__mysql_disconnect__()
__close_ssh_tunnel__()

infos = []
for kor in cur:
    for location_region in cur:
        infos.append(location_region)

infos_commune = []
for location_sub_region in cur:
    infos_commune.append(location_sub_region)

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
select0 = ('select department', _('Select Department'))
DEPARTMENT_CHOICES.insert(0, select0)

DEPARTMENT_CHOICES = models.Training.objects.values_list('department', flat=True)
DEPARTMENT_CHOICES = sorted(DEPARTMENT_CHOICES)
DEPARTMENT_CHOICES = set(DEPARTMENT_CHOICES)
DEPARTMENT_CHOICES = sorted(DEPARTMENT_CHOICES)

COMMUNE_CHOICE = models.Training.objects.values_list('commune', flat=True)
COMMUNE_CHOICE = sorted(COMMUNE_CHOICE)
COMMUNE_CHOICE = set(COMMUNE_CHOICE)
COMMUNE_CHOICE = sorted(COMMUNE_CHOICE)

COMMUNE_CHOICES = [tuple([x[0].lower() + x[1:], x.capitalize()]) for x in COMMUNE_CHOICE]
select1 = ('select commune', _('Select Commune'))
COMMUNE_CHOICES.insert(0, select1)


class DepartmentChoice(forms.Form):
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
            }
        )
    )


class CommuneChoice(forms.Form):
    commune = forms.ChoiceField(
        choices=COMMUNE_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
            }
        )
    )


nursery_column_search = (
    ('all', _('All')),
    ('nursery name', _('NURSERY NAME')),
    ('owner first name', _('OWNER FIRST NAME')),
    ('owner last name', _('OWNER LAST NAME')),
    ('nursery address', _('NURSERY ADDRESS')),
    ('country', _('COUNTRY')),
    ('commune', _('COMMUNE')),
    ('current area', _('CURRENT AREA')),
    ('latitude', _('LATITUDE')),
    ('longitude', _('LONGITUDE')),
    ('altitude', _('ALTITUDE')),
    ('partner', _('PARTNER')),
    ('number of plants', _('NUMBER OF PLANTS')),
)


class NurserySearch(forms.Form):
    column = forms.ChoiceField(
        choices=nursery_column_search,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
            }
        )
    )


beninyields_column_search = (
    ('all', _('All')),
    ('plantation name', _('PLANTATION NAME')),
    ('total yield kg', _('TOTAL YIELD KG')),
    ('total yield per ha kg', _('TOTAL YIELD PER HA KG')),
    ('total yield per tree kg', _('TOTAL YIELD PER TREE KG')),
    ('product id', _('PRODUCT ID')),
    ('total number trees', _('TOTAL NUMBER TREES')),
    ('total sick trees', _('TOTAL SICK TREES')),
    ('total dead trees', _('TOTAL DEAD TREES')),
    ('total trees out of prod', _('TOTAL TREES OUT OF PROD')),
    ('year', _('YEAR')),
)


class BeninYieldSearch(forms.Form):
    column = forms.ChoiceField(
        choices=beninyields_column_search,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
            }
        )
    )


plantations_column_search = (
    ('all', _('All')),
    ('plantation name', _('PLANTATION NAME')),
    ('plantation code', _('PLANTATION CODE')),
    ('owner first name', _('OWNER FIRST NAME')),
    ('owner last name', _('OWNER LAST NAME')),
    ('owner gender', _('OWNER GENDER')),
    ('total trees', _('TOTAL TREES')),
    ('country', _('COUNTRY')),
    ('department', _('DEPARTMENT')),
    ('commune', _('COMMUNE')),
    ('arrondissement', _('ARRONDISSEMENT')),
    ('village', _('village')),
    ('current area', _('CURRENT AREA')),
    ('latitude', _('LATITUDE')),
    ('longitude', _('LONGITUDE')),
    ('altitude', _('ALTITUDE')),

)


class PlantationsSearch(forms.Form):
    column = forms.ChoiceField(
        choices=plantations_column_search,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
            }
        )
    )


training_column_search = (
    ('all', _('All')),
    ('module name', _('MODULE NAME')),
    ('trainer first name', _('TRAINER FIRST NAME')),
    ('trainer last name', _('TRAINER LAST NAME')),
    ('number of participant', _('NUMBER OF PARTICIPANT')),
    ('department', _('DEPARTMENT')),
    ('commune', _('COMMUNE')),
)


class TrainingSearch(forms.Form):
    column = forms.ChoiceField(
        choices=training_column_search,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
            }
        )
    )


class TrainingDateForm(forms.Form):
    training_date = forms.DateField(
        initial=dates,
        widget=DateInput(
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
            }
        )
    )


times = str(time(hour=current_time.hour, minute=current_time.minute))


class TrainingTimeForm(forms.Form):
    training_time = forms.TimeField(
        initial=times,
        widget=TimeInput(
            format='%H:%M',
            attrs={
                'type': 'time',
                'class': 'form-control',
                'style': 'border-color: none;',
            }
        )
    )
