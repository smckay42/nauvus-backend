from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CarrierAccountDetailsView,
    CarrierBankingBalanceView,
    StripeCreateAccountLinkView,
    UserOnboardingRequirementStatusAPIView,
)

app_name = "banking"

router = DefaultRouter()

urlpatterns = [
    path("balance/", CarrierBankingBalanceView.as_view()),
    path("external-account-info/", CarrierAccountDetailsView.as_view()),
    path("create-account-links/", StripeCreateAccountLinkView.as_view(), name="create-account-links"),
    path(
        "user-onboarding-requirements-status/",
        UserOnboardingRequirementStatusAPIView.as_view(),
        name="user-onboarding-requirements-status",
    ),
]

urlpatterns += router.urls
