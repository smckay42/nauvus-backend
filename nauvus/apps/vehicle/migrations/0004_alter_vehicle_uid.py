# Generated by Django 3.2.13 on 2022-05-11 04:25

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0003_vehicle_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
