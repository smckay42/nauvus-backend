# Generated by Django 3.2.13 on 2022-12-28 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loads', '0013_load_final_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='load',
            name='delivery_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]