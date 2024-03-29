# Generated by Django 3.2.13 on 2022-06-09 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_rename_load_loaditem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loaditem',
            name='pickup_date_time',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='loaditem',
            name='pickup_date_time_utc',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='loaditem',
            name='posted_date',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='loaditem',
            name='received_at',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
