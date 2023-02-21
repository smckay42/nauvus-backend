# Generated by Django 3.2.13 on 2022-05-05 10:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dispatcher', '0002_rename_name_dispatcher_organization_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='DispatcherW9Information',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('w9_document', models.FileField(blank=True, null=True, upload_to='', verbose_name='W9 form and and Tax ID Number')),
                ('taxpayer_id_number', models.CharField(max_length=255, verbose_name='Tax ID number')),
                ('dispatcher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dispatcher.dispatcher')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]