# Generated by Django 4.0.1 on 2022-01-22 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_remuser_email_remuser_first_name_remuser_last_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
