from django.contrib import admin

from nauvus.apps.notifications.models import Notification

# Register your models here.

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = ["id", "notification_type", "book_load"]