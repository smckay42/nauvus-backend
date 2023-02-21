# Generated by Django 3.2.13 on 2023-01-17 16:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0007_userexternalbankaccount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userexternalbankaccount',
            name='user',
        ),
        migrations.RemoveField(
            model_name='userpaymentrecord',
            name='book_load',
        ),
        migrations.RemoveField(
            model_name='userpaymentrecord',
            name='user',
        ),
        migrations.DeleteModel(
            name='LoadPayment',
        ),
        migrations.DeleteModel(
            name='UserExternalBankAccount',
        ),
        migrations.DeleteModel(
            name='UserPaymentRecord',
        ),
    ]
