# Generated by Django 3.2.13 on 2022-07-26 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0015_bookload_rate_confirmation_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookload',
            name='final_price',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
