# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import RemRole, RemUser, RemOrganization
from .utils import DateInput

# from phonenumber_field.formfields import PhoneNumberField

ACTIVE = 1
INACTIVE = 0
Status = [
    (ACTIVE, 'Active'),
    (INACTIVE, 'Inactive'),
]

MALE = 'male'
FEMALE = 'female'
OTHERS = 'others'

GenderChoices = [
    (MALE, 'Male'),
    (FEMALE, 'Female'),
    (FEMALE, 'Others'),
]


class NewPassword(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        )
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
                "class": "form-control"
            }
        )
    )

    def clean(self):
        password_ = self.cleaned_data.get('password')
        password__ = self.cleaned_data.get('password1')
        if password_ != password__:
            raise ValidationError(
                {
                    "password": "Password and confirm password do not match",
                    "password1": "Password and confirm password do not match"
                }
            )
        return self.cleaned_data

    class Meta:
        model = User
        fields = ('password', 'password1',)


class ForgotPassword(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        )
    )

    def clean(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError({"email": "Email does not exists"})

        return self.cleaned_data

    class Meta:
        model = User
        fields = ('email',)


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'remember_me')


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control",
                "autocomplete": "off",
            }
        ))
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First Name",
                "autocomplete": "off",
                "class": "form-control"
            }
        ))
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last Name",
                "autocomplete": "off",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "autocomplete": "off",
                "class": "form-control"
            }
        ))
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Phone Number",
                "autocomplete": "off",
                "class": "form-control"
            }
        )
    )
    organization = forms.ModelChoiceField(
        queryset=RemOrganization.objects.all().filter(status=ACTIVE),
        empty_label='Not Listed',
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
                "autocomplete": "off",
                'id': 'id_organization',
            }
        )
    )
    role = forms.ModelChoiceField(
        queryset=RemRole.objects.all().filter(status=ACTIVE),
        empty_label='Not Listed',
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
                "autocomplete": "off",
                'id': 'id_role'
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "autocomplete": "off",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
                "autocomplete": "off",
                "class": "form-control"
            }
        ))

    def clean(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError({"email": "Email exists"})

        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError({"username": "Username exists"})

        password = self.cleaned_data.get('password1')
        password1 = self.cleaned_data.get('password2')
        if password != password1:
            raise ValidationError(
                {
                    "password1": "Password and confirm password do not match",
                    "password2": "Password and confirm password do not match"
                }
            )
        return self.cleaned_data

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'phone', 'organization', 'role', 'password1', 'password2')


class FullSignUpForm(forms.ModelForm):
    user_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        )
    )

    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First Name",
                "class": "form-control"
            }
        )
    )

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last Name",
                "class": "form-control"
            }
        )
    )

    gender = forms.CharField(
        max_length=6,
        widget=forms.Select(
            choices=GenderChoices,
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
            }
        ),
    )

    date_of_birth = forms.DateField(widget=DateInput())

    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format:
    # '+999999999'. Up to 15 digits allowed.")
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Phone Number",
                "class": "form-control"
            }
        )
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        )
    )

    organization_name = forms.ModelChoiceField(
        queryset=RemOrganization.objects.all().filter(status=ACTIVE),
        empty_label='Not Listed',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
                'id': 'id_organization',
            }
        )
    )

    # selected_org = ''
    # if organization_name != "---------":
    #     selected_org = organization_name

    role = forms.ModelChoiceField(
        queryset=RemRole.objects.none(),
        # empty_label='(Not Listed)',.filter(organization = selected_org)
        empty_label='Not Listed',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'border-color: none;',
                'id': 'id_role'
            }
        )
    )

    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Address",
                "class": "form-control"
            }
        )
    )

    country = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Country",
                "class": "form-control"
            }
        )
    )

    city = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "City",
                "class": "form-control"
            }
        )
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        )
    )

    class Meta:
        model = RemUser
        fields = (
            'user_name',
            'first_name',
            'last_name',
            'gender',
            'date_of_birth',
            'phone',
            'email',
            'organization_name',
            'role',
            'address',
            'country',
            'city',
            'password1',
            'password2'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Init empty did queryset
        self.fields['role'].queryset = RemRole.objects.none()

        # Get did queryset for the selected fid
        if 'organization_name' in self.data:
            try:
                org_id = int(self.data.get('organization_name'))
                self.fields['role'].queryset = RemRole.objects.filter(
                    organization=org_id)
            except (ValueError, TypeError):
                # invalid input from the client; ignore and use empty queryset
                pass


class RegisterOrganization(forms.ModelForm):
    organization_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Organization Name",
                "class": "form-control"
            }
        )
    )

    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Description",
                "class": "form-control"
            }
        )
    )

    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Phone Number",
                "class": "form-control"
            }
        )
    )

    e_mail = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        )
    )

    website = forms.URLField(
        widget=forms.URLInput(
            attrs={
                "placeholder": "Website",
                "class": "form-control"
            }
        )
    )

    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Address",
                "class": "form-control"
            }
        )
    )

    country = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Country",
                "class": "form-control"
            }
        )
    )

    city = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "City",
                "class": "form-control"
            }
        )
    )

    class Meta:
        model = RemOrganization
        fields = (
            'organization_name',
            'description',
            'phone',
            'e_mail',
            'website',
            'address',
            'country',
            'city',
        )


'''
role_name = models.CharField(max_length=200)
organization = models.ForeignKey(RemOrganization, on_delete=models.CASCADE, null=True)
status = models.IntegerField(choices=Status, default=ACTIVE,)
created_by = models.BigIntegerField()
created_date = models.DateTimeField(blank=False, null=False)
updated_by = models.BigIntegerField()
updated_date = models.DateTimeField(blank=False, null=False)
'''


class RegisterRole(forms.ModelForm):
    role_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Role",
                "class": "form-control"
            }
        )
    )

    # organization_ = forms.ModelChoiceField(
    #     queryset=RemOrganization.objects.all(),
    #     empty_label='Not Listed',
    #     widget=forms.Select(
    #         attrs={
    #             'class': 'form-control',
    #             'style': 'border-color: none;',
    #         }
    #     )
    # )

    class Meta:
        model = RemRole
        fields = (
            'role_name',
            # 'organization_',
        )
