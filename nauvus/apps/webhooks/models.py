from django.db import models

from nauvus.base.models import BaseModel


class ProcessedStripeEvent(BaseModel):
    """Log for tracking events from stripe that have been processed already."""

    stripe_event_id = models.CharField(max_length=50, primary_key=True)
