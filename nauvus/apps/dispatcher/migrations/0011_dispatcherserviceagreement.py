# Generated by Django 3.2.13 on 2022-05-13 11:06

from django.db import migrations, models
import django.db.models.deletion
import nauvus.apps.dispatcher.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dispatcher', '0010_alter_dispatcherw9information_w9_document'),
    ]

    operations = [
        migrations.CreateModel(
            name='DispatcherServiceAgreement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('envelope_id', models.CharField(max_length=255, verbose_name='Dispatcher Envelope ID')),
                ('is_signed', models.BooleanField()),
                ('document', models.FileField(blank=True, null=True, upload_to=nauvus.apps.dispatcher.models.wrapper_service_agreement_document, verbose_name='document')),
                ('dispatcher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dispatcher.dispatcher')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]