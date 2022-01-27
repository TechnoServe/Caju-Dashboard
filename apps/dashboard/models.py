# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Qar(models.Model):
    document_id = models.CharField(max_length=255)

    country = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    commune = models.CharField(max_length=200)

    site = models.CharField(max_length=200)

    latitude = models.FloatField(null=True, blank=False)
    longitude = models.FloatField(null=True, blank=False)
    altitude = models.FloatField(null=True)

    kor = models.FloatField(null=True)

    def __str__(self):
        return self.document_id


class Nursery(models.Model):
    class Status:
        ACTIVE = 1
        INACTIVE = 0

    class GenderChoices:
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHERS = 'others', _('Others')

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

    nursery_name = models.CharField(max_length=200, unique=True)
    owner_first_name = models.CharField(max_length=200)
    owner_last_name = models.CharField(max_length=200)
    nursery_address = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    commune = models.CharField(max_length=200)
    current_area = models.FloatField(null=True)
    latitude = models.FloatField(null=True, blank=False)
    longitude = models.FloatField(null=True)
    altitude = models.FloatField(null=True)
    partner = models.CharField(max_length=200)
    status = models.IntegerField(choices=Status, default=ACTIVE, )
    number_of_plants = models.IntegerField(null=True)

    def __str__(self):
        return self.nursery_name


class NurseryPlantsHistory(models.Model):
    nursery_id = models.ForeignKey(Nursery, on_delete=models.CASCADE, null=True)
    year = models.IntegerField()
    season = models.IntegerField()
    total_plants = models.BigIntegerField()
    total_grafted = models.BigIntegerField()
    total_graft_holders = models.BigIntegerField()
    polyclonal = models.CharField(max_length=300)
    comment = models.CharField(max_length=300)

    def __str__(self):
        return self.total_plants


class MotherTree(models.Model):
    class Status:
        ACTIVE = 1
        INACTIVE = 0

    class GenderChoices:
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHERS = 'others', _('Others')

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

    # id = models.BigAutoField(primary_key=True)
    mother_tree_name = models.CharField(max_length=200, unique=True)
    owner_first_name = models.CharField(max_length=200)
    owner_last_name = models.CharField(max_length=200)
    owner_gender = models.CharField(
        max_length=6,
        choices=GenderChoices,
        default=OTHERS,
    )
    owner_date_of_birth = models.DateField(blank=True, null=True)
    # owner_phone = PhoneNumberField(null=False, blank=False, unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)  # validators should be a list
    mother_tree_address = models.CharField(max_length=200)
    owner_address = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    commune = models.CharField(max_length=200)
    arrondissement = models.CharField(max_length=200)
    village = models.CharField(max_length=200)
    plantation_id = models.CharField(max_length=200)
    latitude = models.FloatField(null=False, blank=False)
    longitude = models.FloatField(null=True)
    altitude = models.FloatField(null=True)
    certified = models.BooleanField(default=False)
    certified_by = models.BigIntegerField(blank=True)
    certified_date = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(choices=Status, default=INACTIVE, )
    created_by = models.BigIntegerField(blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    updated_by = models.BigIntegerField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.mother_tree_name


class Plantation(models.Model):
    class Status:
        ACTIVE = 1
        INACTIVE = 0

    class GenderChoices:
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHERS = 'others', _('Others')

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

    plantation_name = models.CharField(max_length=200, unique=True)
    plantation_code = models.CharField(max_length=200, unique=True)
    owner_first_name = models.CharField(max_length=200)
    owner_last_name = models.CharField(max_length=200)
    owner_gender = models.CharField(
        max_length=6,
        choices=GenderChoices,
        default=OTHERS,
    )
    total_trees = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    commune = models.CharField(max_length=200)
    arrondissement = models.CharField(max_length=200)
    village = models.CharField(max_length=200)
    current_area = models.FloatField(null=True)
    latitude = models.FloatField(null=False, blank=False)
    longitude = models.FloatField(null=True)
    altitude = models.FloatField(null=True)
    status = models.IntegerField(choices=Status, default=ACTIVE, )

    # id = models.BigAutoField(primary_key=True)
    # plantation_id = models.CharField(max_length=200, unique=True)
    # plantation_age = models.IntegerField(blank=True, null=True)
    # owner_date_of_birth = models.DateField(blank=True, null=True)
    # owner_phone = PhoneNumberField(null=False, blank=False, unique=True)
    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    # phone = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list
    # plantation_address = models.CharField(max_length=200)
    # owner_address = models.CharField(max_length=200)
    # certified = models.BooleanField(default=False)
    # certified_by = models.BigIntegerField(blank=True)
    # certified_date = models.DateTimeField(blank=True, null=True)
    # partner = models.CharField(max_length=200)
    # website = models.URLField(max_length=254, null=True)
    # created_by = models.BigIntegerField(blank=True, null=True)
    # created_date = models.DateTimeField(blank=True, null=True)
    # updated_by = models.BigIntegerField(blank=True, null=True)
    # updated_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.plantation_name


class BeninYield(models.Model):
    class Status:
        ACTIVE = 1
        INACTIVE = 0

    ACTIVE = 1
    INACTIVE = 0
    Status = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]

    plantation_name = models.CharField(max_length=200)
    plantation_code = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    commune = models.CharField(max_length=200)
    arrondissement = models.CharField(max_length=200)
    village = models.CharField(max_length=200)
    owner_first_name = models.CharField(max_length=200)
    owner_last_name = models.CharField(max_length=200)
    plantation_code = models.CharField(max_length=200)
    surface_area = models.FloatField(null=True)
    total_yield_kg = models.FloatField()
    total_yield_per_ha_kg = models.FloatField()
    total_yield_per_tree_kg = models.FloatField()
    sex = models.CharField(max_length=200)
    plantation_id = models.ForeignKey(Plantation, on_delete=models.CASCADE, null=True)
    product_id = models.CharField(max_length=60)
    total_number_trees = models.FloatField()
    total_sick_trees = models.FloatField()
    total_dead_trees = models.FloatField()
    total_trees_out_of_prod = models.FloatField()
    plantation_age = models.FloatField()
    latitude = models.FloatField(null=False, blank=False)
    longitude = models.FloatField(null=True)
    altitude = models.FloatField(null=True)
    status = models.IntegerField(choices=Status, default=ACTIVE, )
    year = models.IntegerField()

    def __str__(self):
        return str(self.product_id) + str(self.year)


class AlteiaData(models.Model):
    plantation_code = models.CharField(max_length=200, unique=True)
    cashew_tree_cover = models.FloatField(null=True)

    def __str__(self):
        return str(self.plantation_code)


class DeptSatellite(models.Model):
    country = models.CharField(max_length=200)
    department = models.CharField(max_length=200, unique=True)
    cashew_tree_cover = models.FloatField(null=True)

    def __str__(self):
        return str(self.department)


class CommuneSatellite(models.Model):
    country = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    commune = models.CharField(max_length=200, unique=True)
    cashew_tree_cover = models.FloatField(null=True)

    def __str__(self):
        return str(self.commune)


class SpecialTuple(models.Model):
    plantation_id = models.CharField(max_length=200, unique=True)
    alteia_id = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return str(self.alteia_id)

# Create your models here.
