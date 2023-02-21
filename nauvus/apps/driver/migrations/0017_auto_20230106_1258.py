# Generated by Django 3.2.13 on 2023-01-06 12:58

from django.db import migrations, models
import django.db.models.deletion
import nauvus.apps.driver.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('driver', '0016_merge_20220930_0438'),
    ]

    operations = [
        migrations.CreateModel(
            name='DriverServiceAgreement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('envelope_id', models.CharField(max_length=255, verbose_name='Driver Envelope ID')),
                ('is_signed', models.BooleanField(default=False)),
                ('document', models.FileField(blank=True, null=True, upload_to=nauvus.apps.driver.models.wrapper_service_agreement_document, verbose_name='document')),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='driver.driver')),
            ],
        ),
        migrations.AddIndex(
            model_name='driverserviceagreement',
            index=models.Index(fields=['id'], name='driver_driv_id_62c105_idx'),
        ),
        migrations.AddIndex(
            model_name='driverserviceagreement',
            index=models.Index(fields=['driver'], name='driver_driv_driver__644d9e_idx'),
        ),
    ]
