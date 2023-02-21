import uuid

from django.db import models

from nauvus.utils.conversion import convert_date_to_ms_since_epoch


class BaseModel(models.Model):
    uid = models.UUIDField(max_length=100, default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    class Meta:
        abstract = True

    def update_at_in_milliseconds(self):
        return convert_date_to_ms_since_epoch(self.updated_at)

    def created_at_in_milliseconds(self):
        return convert_date_to_ms_since_epoch(self.created_at)
