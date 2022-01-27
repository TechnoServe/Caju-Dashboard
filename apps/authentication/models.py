# -*- encoding: utf-8 -*-
"""
Copyright (c) 2020 - Technoserve
"""

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save


# Create your models here.

class RemOrganization(models.Model):
    class Status:
        ACTIVE = 1
        INACTIVE = 0

    ACTIVE = 1
    INACTIVE = 0
    Status = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]

    # id = models.BigAutoField(primary_key=True)
    organization_name = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)  # validators should be a list
    # phone = PhoneNumberField(null=False, blank=False, unique=True)
    e_mail = models.EmailField(max_length=254)
    website = models.URLField(max_length=254, null=False)
    address = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    status = models.IntegerField(choices=Status, default=ACTIVE, )
    created_by = models.BigIntegerField(null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    updated_by = models.BigIntegerField(null=True)
    updated_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.organization_name


class RemRole(models.Model):
    class Status():
        ACTIVE = 1
        INACTIVE = 0

    ACTIVE = 1
    INACTIVE = 0
    Status = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]
    # id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=200)
    # organization = models.ForeignKey(RemOrganization, on_delete=models.CASCADE, null=True)
    status = models.IntegerField(choices=Status, default=ACTIVE, )
    created_by = models.BigIntegerField(null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    updated_by = models.BigIntegerField(null=True)
    updated_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.role_name


class RemUserManager(models.Manager):
    pass


class RemUser(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    email = models.CharField(max_length=64, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits "
                                         "allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    organization = models.ForeignKey(RemOrganization, on_delete=models.CASCADE, null=True, blank=True)
    role = models.ForeignKey(RemRole, on_delete=models.CASCADE, null=True)
    objects = RemUserManager()

    def __str__(self):
        return self.user.username


def create_remuser(sender, **kwargs):
    if kwargs['created']:
        rem_user = RemUser.objects.create(user=kwargs['instance'])


post_save.connect(create_remuser, sender=User)