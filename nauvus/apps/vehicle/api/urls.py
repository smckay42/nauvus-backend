from rest_framework.routers import DefaultRouter

from .views import VehicleViewset

app_name = "vehicle"

router = DefaultRouter()

router.register(
    r"",
    VehicleViewset,
    basename="vehicle",
)

urlpatterns = []
urlpatterns += router.urls
