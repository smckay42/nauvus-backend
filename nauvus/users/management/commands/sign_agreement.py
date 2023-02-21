import random

from django.core.management.base import BaseCommand, CommandParser

from nauvus.apps.carrier.models import CarrierServiceAgreement, CarrierUser
from nauvus.apps.dispatcher.models import DispatcherServiceAgreement, DispatcherUser
from nauvus.apps.driver.models import Driver, DriverServiceAgreement
from nauvus.users.models import User


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--email", type=str, required=True, help="The email of the user to mark the agreement as signed for."
        )

    def handle(self, *args, **options):

        user_email = options.get("email")

        try:
            user = User.objects.get(email=user_email)

            type = user.user_type

            if type == User.CARRIER_OWNER:
                carrier_user = CarrierUser.objects.get(user=user)
                agreement, created = CarrierServiceAgreement.objects.get_or_create(carrier=carrier_user.carrier)

            if type == User.DISPATCHER:
                dispatcher_user = DispatcherUser.objects.get(user=user)
                agreement, created = DispatcherServiceAgreement.objects.get_or_create(
                    dispatcher=dispatcher_user.dispatcher
                )

            if type == User.DRIVER:
                driver_user = Driver.objects.get(user=user)
                agreement, created = DriverServiceAgreement.objects.get_or_create(driver=driver_user)

            if created:
                # for some reason, there is not an agreement, so go ahead and add an envelope id with a random #
                id = random.randint(100000, 999999)
                agreement.envelope_id = f"GENERATED-{id}"
            agreement.is_signed = True  # mark as signed
            agreement.save()

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No user found with email '{user_email}'."))
            return

        self.stdout.write(self.style.SUCCESS("Marked agreement as signed."))
