from django.urls import path
from rest_framework.routers import DefaultRouter

from nauvus.apps.cities.api.views import CityViewset, DistanceView

app_name = "cities"

router = DefaultRouter()

router.register(
    r"",
    CityViewset,
    basename="cities",
)

# router.register(
#     r"",
#     DistanceViewset,
#     basename="distance",
# )

urlpatterns = [path("distance/", DistanceView.as_view(), name="distance")]
urlpatterns += router.urls
