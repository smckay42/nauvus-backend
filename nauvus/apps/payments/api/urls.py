from django.urls import path
from rest_framework.routers import DefaultRouter

from nauvus.apps.payments.api.views import TransferUserMoneyToExternalAccount, LoadPaymentViewSet

app_name = "payments"

router = DefaultRouter()
router.register("", LoadPaymentViewSet, basename="payments")

urlpatterns = [
    path('users-payouts/', TransferUserMoneyToExternalAccount.as_view(), name='users-payouts')
]

urlpatterns += router.urls
