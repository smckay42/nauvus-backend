# Generated by Django 3.2.13 on 2022-05-11 04:25

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dispatcher', '0008_alter_dispatcherw9information_w9_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispatcher',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='dispatcherreference',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='dispatcherw9information',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]