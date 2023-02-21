from rest_framework.routers import DefaultRouter

from .views import LoadViewSet

app_name = "loads"

router = DefaultRouter()
router.register("", LoadViewSet, basename="loads")

urlpatterns = []

urlpatterns += router.urls
