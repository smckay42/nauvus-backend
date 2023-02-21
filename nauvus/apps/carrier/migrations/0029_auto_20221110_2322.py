# Generated by Django 3.2.13 on 2022-11-10 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carrier', '0028_merge_0013_auto_20221110_0949_0027_carrier_fleet_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrier',
            name='no_of_trailers',
            field=models.PositiveIntegerField(blank=True, default=0, help_text='How many trailers do you have?', null=True),
        ),
        migrations.AlterField(
            model_name='carrier',
            name='no_of_trucks',
            field=models.PositiveIntegerField(blank=True, default=0, help_text='How many vehicles do you have', null=True),
        ),
    ]