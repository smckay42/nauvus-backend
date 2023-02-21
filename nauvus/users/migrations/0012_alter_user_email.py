# Generated by Django 3.2.13 on 2022-11-27 17:26

from django.db import migrations
import nauvus.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_merge_20220827_0552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=nauvus.users.models.LowercaseEmailField(blank=True, default=None, max_length=254, null=True, unique=True, verbose_name='Email'),
        ),
    ]