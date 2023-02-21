import environ
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command
from django.template.defaultfilters import slugify

from nauvus.apps.carrier.models import Carrier


class Command(BaseCommand):
    help = "Update Carrier information"
    ENV = environ.Env()

    def __init__(self):
        self.user_class = get_user_model()
        super().__init__()

    def handle(self, *args, **options):
        self.create_carrier_fleet_id()

    def create_carrier_fleet_id(self):
        carriers = Carrier.objects.all()
        for carrier in carriers:
            carrier.fleet_id = (
                slugify(carrier.organization_name)
                + slugify(carrier.created_at.time())
                + slugify(carrier.created_at.date().day)
                + slugify(carrier.created_at.date().month)
                + slugify(carrier.id)
                + slugify(carrier.created_at.date().year)
            )
            carrier.save()
