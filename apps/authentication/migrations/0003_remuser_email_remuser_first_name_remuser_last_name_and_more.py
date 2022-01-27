# Generated by Django 4.0.1 on 2022-01-22 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_remove_remuser_email_remove_remuser_first_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='remuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, unique=True),
        ),
        migrations.AddField(
            model_name='remuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='remuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='remuser',
            name='username',
            field=models.CharField(blank=True, max_length=200, unique=True),
        ),
    ]
