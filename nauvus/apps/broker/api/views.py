from rest_framework import viewsets

from nauvus.api.permissions import IsCarrierOrDispatcher
from nauvus.apps.broker.api.serializers import BrokerSerializer
from nauvus.apps.broker.models import Broker


class BrokerViewset(viewsets.ModelViewSet):
    """A simple viewset for working with brokers"""

    serializer_class = BrokerSerializer
    permission_classes = [IsCarrierOrDispatcher]
    queryset = Broker.objects.all()
