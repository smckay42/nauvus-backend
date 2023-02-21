import base64

from django.core.files.base import ContentFile
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from nauvus.apps.carrier.models import CarrierServiceAgreement
from nauvus.apps.dispatcher.models import DispatcherServiceAgreement
from nauvus.apps.driver.models import DriverServiceAgreement


class DocusignWebhookCallback(APIView):

    """
    Docusign Webhook
    """

    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data["data"]["envelopeSummary"]["envelopeDocuments"][0]["PDFBytes"]
        envelope_id = request.data["data"]["envelopeId"]

        data = ContentFile(base64.b64decode(data), name="temp." + "pdf")
        try:
            carrier_service_agreement = CarrierServiceAgreement.objects.get(
                envelope_id=envelope_id
            )
            carrier_service_agreement.is_signed = True
            carrier_service_agreement.document = data
            carrier_service_agreement.save()

        except CarrierServiceAgreement.DoesNotExist:
            try:
                dispatcher_service_agreement = (
                    DispatcherServiceAgreement.objects.get(envelope_id=envelope_id)
                )
                dispatcher_service_agreement.is_signed = True
                dispatcher_service_agreement.document = data
                dispatcher_service_agreement.save()

            except DispatcherServiceAgreement.DoesNotExist:
                driver_service_agreement = (
                    DriverServiceAgreement.objects.get(envelope_id=envelope_id)
                )
                driver_service_agreement.is_signed = True
                driver_service_agreement.document = data
                driver_service_agreement.save()

        return Response({})
