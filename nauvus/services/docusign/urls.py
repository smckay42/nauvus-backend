from django.urls import path

from nauvus.services.docusign.views import DocusignWebhookCallback

urlpatterns = [
    path(
        "webhook/callback/", DocusignWebhookCallback.as_view(), name="redirect"
    ),
]
