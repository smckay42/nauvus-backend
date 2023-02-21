# Generated by Django 3.2.13 on 2022-06-09 10:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dispatcher', '0020_dispatcheradmininvitation_pending_invitation'),
        ('carrier', '0021_carrieradmininvitation_pending_invitation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carrieradmininvitation',
            name='pending_invitation',
        ),
        migrations.RemoveField(
            model_name='carrieradmininvitation',
            name='permission',
        ),
        migrations.AddField(
            model_name='carrieruser',
            name='pending_invitation',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='carrieruser',
            name='permission',
            field=models.CharField(blank=True, choices=[('full_admin', 'Full Admin'), ('redy_only_admin', 'Read Only Admin')], default='redy_only_admin', max_length=20, null=True),
        ),
        migrations.CreateModel(
            name='CarrierDispatcher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, verbose_name='Status of the Carrier dispatcher')),
                ('carrier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='carrier.carrier')),
                ('dispatcher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dispatcher.dispatcher')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
