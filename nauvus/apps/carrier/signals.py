# import inbuilt user model
from django.db.models.signals import post_save
from django.dispatch import receiver
from nauvus.apps.carrier.models import Carrier
from django.template.defaultfilters import slugify


@receiver(post_save, sender=Carrier)
def fleet_id_post_save(sender, instance, created, **kwargs):
    
    # Create unique fleet id for carrier
    if created:
        instance.fleet_id = (
            slugify(instance.organization_name)
            + slugify(instance.created_at.time())
            + slugify(instance.created_at.date().day)
            + slugify(instance.created_at.date().month)
            + slugify(instance.id)
            + slugify(instance.created_at.date().year)
        )
        instance.save()
