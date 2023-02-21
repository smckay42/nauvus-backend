# Generated by Django 3.2.13 on 2022-06-16 09:36

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('carrier', '0023_delete_carrieradmininvitation'),
        ('driver', '0012_carrierdriver_carrier_user'),
        ('dispatcher', '0026_merge_20220614_0919'),
        ('bookings', '0008_bookload_dispatcher'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalLoad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rc_document', models.FileField(blank=True, null=True, upload_to='', verbose_name='Rc Document of the Load')),
                ('customer_reference_number', models.CharField(blank=True, max_length=200, null=True)),
                ('pickup', models.CharField(blank=True, max_length=200, null=True, verbose_name='Pickup point company name')),
                ('dropoff', models.CharField(blank=True, max_length=200, null=True, verbose_name='Pickup point company name')),
                ('pickup_address', models.CharField(blank=True, max_length=200, null=True, verbose_name='Pickup point address')),
                ('dropoff_address', models.CharField(blank=True, max_length=200, null=True, verbose_name='Pickup point address')),
                ('pickup_location', models.CharField(blank=True, max_length=200, null=True, verbose_name='Pickup point Location')),
                ('dropoff_location', models.CharField(blank=True, max_length=200, null=True, verbose_name='Pickup point Location')),
                ('pickup_date', models.CharField(blank=True, max_length=200, null=True, verbose_name='Load pickup date')),
                ('dropoff_date', models.CharField(blank=True, max_length=200, null=True, verbose_name='Load Dropoff date')),
                ('weight', models.CharField(blank=True, max_length=200, null=True, verbose_name='weight of the load')),
                ('load_price', models.CharField(blank=True, max_length=200, null=True, verbose_name='Price of the Load')),
                ('packging_type', models.CharField(blank=True, max_length=200, null=True, verbose_name='packging Type of the load')),
                ('equipment_type', models.CharField(blank=True, max_length=200, null=True, verbose_name='equipment_type')),
                ('broker', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='carrier.carrierbroker')),
                ('carrier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='carrier.carrier')),
                ('dispatcher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dispatcher.dispatcher')),
                ('driver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='driver.driver')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]