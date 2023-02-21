import datetime
from datetime import date

from django.core.management.base import BaseCommand

from nauvus.apps.loads.models import Load


class Command(BaseCommand):
    def handle(self, *args, **options):
        day_before_yesterday = (date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")

        loads_to_delete = Load.objects.filter(
            pickup_date__lte=day_before_yesterday, current_status=Load.Status.AVAILABLE
        )

        answer = input(
            f"{loads_to_delete.count()} loads are from {day_before_yesterday} or earlier."
            + " Are you sure you want to delete them? (Y/n)"
        )

        if answer == "Y":
            loads_to_delete.delete()
            self.stdout.write(f"Deleted all loads with pickup dates on or before {day_before_yesterday}")
        else:
            self.stdout.write("Loads were not deleted.")
