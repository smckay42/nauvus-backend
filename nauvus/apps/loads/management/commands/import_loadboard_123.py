from django.core.management.base import BaseCommand, CommandParser

from nauvus.services.loadboards.loadboard123.api import Loadboard123


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--states", type=str, help="a comma separated list of states to import from loadboard123 ")

    def handle(self, *args, **options):

        states = []
        arg_states = options.get("states")
        if arg_states:
            states = arg_states.split(",")
        Loadboard123().process_loads(states=states)
        self.stdout.write("Loads imported.")
