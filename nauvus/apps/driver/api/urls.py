from rest_framework.routers import DefaultRouter

from .views import DriverViewSet

app_name = "driver"
router = DefaultRouter()

router.register(r"", DriverViewSet, basename="driver")


urlpatterns = [
    # path("driver-carrier/<int:pk>/", DriverListViewSet.as_view(), name="driver"),
]

urlpatterns += router.urls
