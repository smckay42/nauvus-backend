from django.urls import path
from rest_framework.routers import DefaultRouter

from nauvus.apps.invitations.api.views import InvitationViewset

app_name = "invitations"

router = DefaultRouter()

router.register(
    r"",
    InvitationViewset,
    basename="invitations",
)

# router.register(
#     r"",
#     DistanceViewset,
#     basename="distance",
# )

urlpatterns = []
urlpatterns += router.urls
