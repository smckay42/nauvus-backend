# Generated by Django 3.2.13 on 2022-06-10 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dispatcher', '0022_auto_20220610_0532'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dispatcheruser',
            name='active',
        ),
        migrations.RemoveField(
            model_name='dispatcheruser',
            name='commision',
        ),
        migrations.AddField(
            model_name='dispatcherinvitation',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='dispatcherinvitation',
            name='commision',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Commision of the invited dispatcher'),
        ),
    ]