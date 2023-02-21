from django.urls import path
from rest_framework.routers import DefaultRouter

from nauvus.apps.webhooks.api.views import StripeWebhook

app_name = "webhooks"

router = DefaultRouter()

urlpatterns = [
    path('stripe-webhooks/', StripeWebhook.as_view(), name='stripe-webhooks')
]

urlpatterns += router.urls
