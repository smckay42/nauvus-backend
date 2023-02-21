from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# router.register("users", UserViewSet)


app_name = "api"
urlpatterns = [
    path("auth/", include("nauvus.auth.api.urls"), name="user_authentication"),
    path("broker/", include("nauvus.apps.broker.api.urls"), name="broker"),
    path("carrier/", include("nauvus.apps.carrier.api.urls"), name="carrier"),
    path("driver/", include("nauvus.apps.driver.api.urls"), name="driver"),
    path("vehicle/", include("nauvus.apps.vehicle.api.urls"), name="vehicle"),
    path("loads/", include("nauvus.apps.loads.api.urls"), name="loads"),
    # path(
    #     "bookings/", include("nauvus.apps.bookings.api.urls"), name="booking"
    # ),
    path("cities/", include("nauvus.apps.cities.api.urls"), name="cities"),
    path("users/", include("nauvus.apps.banking.api.urls"), name="banking"),
    path(
        "dispatcher/",
        include("nauvus.apps.dispatcher.api.urls"),
        name="dispatcher",
    ),
    path(
        "docusign/",
        include("nauvus.services.docusign.urls"),
        name="docusign",
    ),
    path(
        "nauvus/admin/",
        include("nauvus.apps.nauvus_admin.api.urls"),
        name="nauvus_admin",
    ),
    path("", include(router.urls)),
    path(
        "invitations/",
        include("nauvus.apps.invitations.api.urls"),
        name="invitations",
    ),
    path("payments/", include("nauvus.apps.payments.api.urls"), name="payments"),
    path("webhooks/", include("nauvus.apps.webhooks.api.urls"), name="webhooks"),
    path("banking/", include("nauvus.apps.banking.api.urls"), name="banking"),
]
