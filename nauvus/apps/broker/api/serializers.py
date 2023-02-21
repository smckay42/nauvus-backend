from rest_framework import serializers

from nauvus.api.serializers import BaseModelSerializer
from nauvus.apps.broker.models import Broker, BrokerPlatForm


class BrokerPlatFormSerializer(BaseModelSerializer):

    """Broker PlatForm Serializer"""

    class Meta:
        model = BrokerPlatForm
        fields = ("id", "name")
        read_only_fields = ("id",)


class BrokerSerializer(BaseModelSerializer):
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True, max_length=300)
    phone = serializers.CharField(required=True)
    mc_number = serializers.CharField(required=True)

    class Meta:
        model = Broker
        fields = "__all__"
