# Generated by Django 3.2.13 on 2022-05-05 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carrier', '0002_alter_carrierw9information_taxpayer_id_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrierfleetapplication',
            name='business_documentation',
            field=models.FileField(upload_to='carrier/fleet application', verbose_name='Business Documentation'),
        ),
        migrations.AlterField(
            model_name='carrierfleetapplication',
            name='insurance_certificate',
            field=models.FileField(upload_to='carrier/fleet application', verbose_name='Insurance Certificate'),
        ),
        migrations.AlterField(
            model_name='carrierfleetapplication',
            name='operating_authority_letter',
            field=models.FileField(upload_to='carrier/fleet application', verbose_name='Authority Letter'),
        ),
    ]
