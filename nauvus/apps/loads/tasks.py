from celery import shared_task

from nauvus.services.loadboards.loadboard123.api import Loadboard123


@shared_task(soft_time_limit=18000)
def get_loads_123loadboard():
    Loadboard123().process_loads()
