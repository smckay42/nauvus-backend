# Generated by Django 3.2.13 on 2022-11-10 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carrier', '0012_alter_carrierserviceagreement_is_signed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrier',
            name='no_of_trailers',
            field=models.PositiveIntegerField(blank=True, default=0, help_text='How many trailers Do you plan for Nauvus?', null=True),
        ),
        migrations.AlterField(
            model_name='carrier',
            name='no_of_trucks',
            field=models.PositiveIntegerField(blank=True, default=0, help_text='How many vehicles Do you plan for Nauvus?', null=True),
        ),
    ]
