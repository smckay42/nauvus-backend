# Generated by Django 3.2.13 on 2022-12-12 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0007_alter_broker_mc_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='broker',
            name='metadata',
            field=models.JSONField(blank=True, null=True, verbose_name='Metadata'),
        ),
    ]
