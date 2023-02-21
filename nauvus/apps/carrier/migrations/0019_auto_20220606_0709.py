# Generated by Django 3.2.13 on 2022-06-06 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carrier', '0018_carrieruser_is_current_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrier',
            name='source',
            field=models.CharField(blank=True, choices=[('social_media', 'Social Media'), ('email', 'Email'), ('blog', 'Blog'), ('other', 'Other')], max_length=50, null=True, verbose_name='Source'),
        ),
        migrations.AlterField(
            model_name='carriertrailersize',
            name='trailer_size',
            field=models.CharField(blank=True, choices=[('48_eet', 'Feet 48'), ('40_feet', 'Feet 40'), ('45_feet', 'Feet 45'), ('53_feet', 'Feet 53'), ('other', 'Other')], max_length=50, null=True, verbose_name='Trailer Size'),
        ),
        migrations.AlterField(
            model_name='carriertrailertype',
            name='trailer_type',
            field=models.CharField(blank=True, choices=[('dry_van', 'Dry Van'), ('reefer', 'Reefer'), ('flatbed', 'Flatbed'), ('step_deck', 'Step Deck'), ('box_truck', 'Box Truck'), ('hotshot', 'Hotshot'), ('power_only', 'Power Only'), ('other', 'Other')], max_length=50, null=True, verbose_name='Trailer Type'),
        ),
    ]
