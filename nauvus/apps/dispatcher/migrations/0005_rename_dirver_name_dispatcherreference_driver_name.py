# Generated by Django 3.2.13 on 2022-05-05 11:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dispatcher', '0004_dispatcherreference'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dispatcherreference',
            old_name='dirver_name',
            new_name='driver_name',
        ),
    ]