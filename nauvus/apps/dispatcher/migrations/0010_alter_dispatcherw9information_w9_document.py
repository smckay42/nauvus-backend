# Generated by Django 3.2.13 on 2022-05-11 05:18

from django.db import migrations, models
import nauvus.apps.dispatcher.models


class Migration(migrations.Migration):

    dependencies = [
        ('dispatcher', '0009_auto_20220511_0425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispatcherw9information',
            name='w9_document',
            field=models.FileField(blank=True, null=True, upload_to=nauvus.apps.dispatcher.models.wrapper_w9_info, verbose_name='W9 form and and Tax ID Number'),
        ),
    ]
