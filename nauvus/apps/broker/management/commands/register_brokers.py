from django.core.management.base import BaseCommand

from nauvus.apps.broker.models import Broker
from nauvus.services.credit.oatfi.api import Oatfi


class Command(BaseCommand):
    oatfi = Oatfi()

    def handle(self, *args, **options):
        brokers = Broker.objects.all()

        for broker in brokers:
            # check to ensure
            try:
                self.oatfi.save_broker(broker)
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR_OUTPUT(
                        f"Unable to save broker with id {broker.uid}. Due to error.  Full message: {e}"
                    )
                )
        self.stdout.write(self.style.SUCCESS("Brokers registered with Oatfi"))
