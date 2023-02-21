# Generated by Django 3.2.13 on 2022-05-09 07:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('carrier', '0003_auto_20220505_1157'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('vehicle_ID', models.PositiveIntegerField(unique=True, verbose_name='Vehicle ID')),
                ('VIN', models.CharField(max_length=100, verbose_name='Vehicle VIN')),
                ('vehicle_year', models.CharField(max_length=10, verbose_name='Vehicle Year')),
                ('vehicle_make', models.CharField(max_length=100, verbose_name='Vehicle Make')),
                ('vehicle_model', models.CharField(max_length=100, verbose_name='Vehicle Model')),
                ('fuel_type', models.CharField(choices=[('Diesel', 'Diesel'), ('Petrol', 'Petrol'), ('Gas', 'Gas')], max_length=20, verbose_name='Fuel Type')),
                ('state', models.CharField(max_length=50, verbose_name='Vehicle State')),
                ('number', models.CharField(max_length=20, verbose_name='Vehicle Number')),
                ('odometer', models.CharField(choices=[('Miles', 'Miles'), ('Kilometers', 'Kilometers')], max_length=20, verbose_name='Odometer')),
                ('active', models.BooleanField(default=False)),
                ('carrier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carrier.carrier')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]