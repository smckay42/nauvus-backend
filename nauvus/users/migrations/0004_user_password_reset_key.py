# Generated by Django 3.2.13 on 2022-05-11 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_passwordresetotpverification'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='password_reset_key',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
