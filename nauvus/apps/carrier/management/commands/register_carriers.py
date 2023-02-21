from django.core.management.base import BaseCommand

from nauvus.apps.carrier.models import CarrierUser
from nauvus.auth.utils import create_user_account_stripe
from nauvus.services.credit.oatfi.api import Oatfi


class Command(BaseCommand):
    oatfi = Oatfi()

    def handle(self, *args, **options):
        carrier_users = CarrierUser.objects.all()

        for cu in carrier_users:
            if cu.user.stripe_customer_id is None:
                cu.user.stripe_customer_id = create_user_account_stripe(cu.user.email)
                cu.user.save()
            # check to ensure
            try:
                self.oatfi.save_carrier(cu)
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR_OUTPUT(
                        f"Unable to save carrier user with id {cu.uid}. Due to error.  Full message: {e}"
                    )
                )
        self.stdout.write(self.style.SUCCESS("Carriers registered with Oatfi"))
