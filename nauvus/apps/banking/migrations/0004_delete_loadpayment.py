# Generated by Django 3.2.13 on 2022-07-20 04:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0003_loadpayment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LoadPayment',
        ),
    ]