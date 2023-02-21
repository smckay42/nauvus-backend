# Generated by Django 3.2.13 on 2022-08-10 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver', '0012_carrierdriver_carrier_user'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='carrierdriver',
            index=models.Index(fields=['id'], name='driver_carr_id_501c75_idx'),
        ),
        migrations.AddIndex(
            model_name='carrierdriver',
            index=models.Index(fields=['carrier'], name='driver_carr_carrier_69b3ed_idx'),
        ),
        migrations.AddIndex(
            model_name='driver',
            index=models.Index(fields=['id'], name='driver_driv_id_48f46d_idx'),
        ),
        migrations.AddIndex(
            model_name='driver',
            index=models.Index(fields=['user'], name='driver_driv_user_id_2bf564_idx'),
        ),
    ]