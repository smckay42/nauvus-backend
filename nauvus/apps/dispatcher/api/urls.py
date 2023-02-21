from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CurrentDispatcherOrganiztionViewset,
    DispatcherAdminInvitationViewset,
    DispatcherCarrierviewset,
    DispatcherInvitationViewset,
    DispatcherOganizationInformationViewSet,
    DispatcherOnboardingStatusView,
    DispatcherReferenceViewset,
    DispatcherW9ViewSet,
)

app_name = "dispatcher"
router = DefaultRouter()

router.register(
    r"w9-information", DispatcherW9ViewSet, basename="dispatcher_w9_form"
),
router.register(
    r"reference", DispatcherReferenceViewset, basename="dispatcher_reference"
)
router.register(
    r"my-organizations",
    DispatcherOganizationInformationViewSet,
    basename="organization_information",
)
router.register(
    r"dispatcher-invitation",
    DispatcherInvitationViewset,
    basename="dispatcher_invitation",
)
router.register(
    r"dispatcher-admin-invitation",
    DispatcherAdminInvitationViewset,
    basename="dispatcher_admin_invitation",
)
router.register(
    r"dispatcher-organization",
    CurrentDispatcherOrganiztionViewset,
    basename="current_dispatcher_organization",
)
router.register(
    r"my-carriers",
    DispatcherCarrierviewset,
    basename="dispatcher_carrier_organization",
)

urlpatterns = [
    path(
        r"onboarding-status",
        DispatcherOnboardingStatusView.as_view(),
        name="onboarding_status",
    )
]

urlpatterns += router.urls
