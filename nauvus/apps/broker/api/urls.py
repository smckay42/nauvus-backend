from rest_framework.routers import DefaultRouter

from .views import BrokerViewset

app_name = "broker"

router = DefaultRouter()

router.register(r"", BrokerViewset)
urlpatterns = []
urlpatterns += router.urls
