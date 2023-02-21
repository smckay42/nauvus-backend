from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CarrierBrokerCreateViewset,
    CarrierDispatcherInvitationViewset,
    CarrierFleetApplicationViewset,
    CarrierOnboardingStatusView,
    CarrierOrganizationViewset,
    CarrierW9InformationViewset,
    CurrentCarrierOrganiztionViewset,
)

app_name = "carrier"

router = DefaultRouter()

router.register(
    r"fleet-application",
    CarrierFleetApplicationViewset,
    basename="fleet_application",
)
router.register(r"w9-information", CarrierW9InformationViewset, basename="w9_information")
router.register(
    r"my-organizations",
    CarrierOrganizationViewset,
    basename="carrier-information",
)
router.register(r"broker", CarrierBrokerCreateViewset, basename="broker")

router.register(
    r"my-dispatchers",
    CarrierDispatcherInvitationViewset,
    basename="carrier_dispatcher_invitation",
)
router.register(
    r"carrier-organization",
    CurrentCarrierOrganiztionViewset,
    basename="carrier_organization_information",
)

urlpatterns = [
    path(
        r"onboarding-status",
        CarrierOnboardingStatusView.as_view(),
        name="onboarding_status",
    ),
    path(
        r"organization-information",
        CarrierOnboardingStatusView.as_view(),
        name="onboarding_status",
    ),
]
urlpatterns += router.urls
