from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers


class TransferUserMoneyToExternalAccountSerializer(serializers.Serializer):
    amount = serializers.DecimalField(required=True, decimal_places=2, max_digits=20)


class PaymentTermsSerializer(serializers.Serializer):
    instant = serializers.BooleanField(default=False)
    terms_accepted = serializers.BooleanField()
    terms_accepted_timestamp = serializers.DateTimeField()

    def validate_terms_accepted(self, value):
        if value is not True:
            raise serializers.ValidationError("Terms must be accepted in order to receive payment")
        return value

    def validate_instant(self, value):
        if value is True:
            # if instant_payment is true, ensure that there is a loan
            load = self.context["load"]
            try:
                load.loadsettlement.invoice.loan
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Instant pay is only available if loan terms have been offered.")
        return value
