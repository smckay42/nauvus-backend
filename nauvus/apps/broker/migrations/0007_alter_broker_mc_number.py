# Generated by Django 3.2.13 on 2022-12-12 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0006_auto_20220810_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='broker',
            name='mc_number',
            field=models.CharField(blank=True, max_length=300, null=True, unique=True, verbose_name='MC Number'),
        ),
    ]