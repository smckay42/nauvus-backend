import environ
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Seeds initial data for the application."
    ENV = environ.Env()

    def __init__(self):
        self.user_class = get_user_model()
        super().__init__()

    def handle(self, *args, **options):
        for app in apps.get_app_configs():
            call_command("makemigrations", app.label)
        call_command("migrate")
        call_command("migrate", "--database=search")
        self.create_super_user()

    def create_super_user(self):
        if self.user_class.objects.filter(
            email=settings.ADMIN_EMAIL,
        ).exists():
            self.stdout.write("Admin account : Already exist")
            return False

        self.user_class.objects.create_superuser(
            username=settings.ADMIN_EMAIL,
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
            pk=0,
        )

        self.stdout.write(
            "Created {} admin account.".format(settings.ADMIN_EMAIL)
        )
    