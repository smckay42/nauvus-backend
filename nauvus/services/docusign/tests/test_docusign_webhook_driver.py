import base64

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from config import settings
from nauvus.apps.carrier.models import CarrierServiceAgreement
from nauvus.apps.dispatcher.models import DispatcherUser, Dispatcher, DispatcherServiceAgreement
from nauvus.apps.driver.models import Driver, DriverServiceAgreement


class TestDocusignWebhookDispatcher(APITestCase):
    def setUp(self):
        settings.ACCOUNT_EMAIL_VERIFICATION = (
            "optional"  # set email verification optinal only for testcases
        )

        self.user_driver = get_user_model().objects.create_user(
            username="driver_test",
            first_name="Driver Testing",

            # Please, enter a valid email to receive the documentation from Docusign
            email="driver_demo@demo.com",

            password='somestrongpass2023',
        )

        self.driver = Driver.objects.create(user=self.user_driver)
        # self.dispatcher_user = DispatcherUser.objects.create(user=self.user_dispatcher, dispatcher=self.dispatcher)
        DriverServiceAgreement.objects.create(driver=self.driver, envelope_id='123456', is_signed=False)

        self.docusign_payload = {
            "event": "recipient-sent",
            "uri": "/restapi/{apiVersion}/accounts/{accountId}/envelopes/{envelopeId}",
            "retryCount": "0",
            "configurationId": "xxxxxxx",
            "apiVersion": "v2.1",
            "generatedDateTime": "",
            "data": {
                "accountId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "recipientId": "1",
                "envelopeId": "123456",
                "envelopeSummary": {
                    "status": "sent",
                    "emailSubject": "API Demo subject",
                    "emailBlurb": "Please sign this Demo Envelope",
                    "signingLocation": "online",
                    "enableWetSign": "true",
                    "allowMarkup": "false",
                    "allowReassign": "true",
                    "createdDateTime": "2019-12-12T18:23:36.6800000Z",
                    "lastModifiedDateTime": "2019-12-12T18:23:36.6970000Z",
                    "statusChangedDateTime": "2019-12-12T18:23:36.6800000Z",
                    "useDisclosure": "false",
                    "sender": {
                        "userName": "John Smith",
                        "userId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                        "accountId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                        "email": "johnsmith@docusign.com"
                    },

                    "envelopeDocuments": [
                        {
                            "documentId": "1",
                            "documentIdGuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                            "name": "BlankDoc.txt",
                            "type": "content",
                            "order": "1",
                            "display": "inline",
                            "includeInDownload": "true",
                            "signerMustAcknowledge": "no_interaction",
                            "templateRequired": "false",
                            "authoritative": "false",
                            "PDFBytes": base64.b64encode('testing 123'.encode('ascii'))
                        }
                    ]
                }
            }
        }

    def test_webhook_for_driver_return_200(self):
        response = self.client.post('/api/v1/docusign/webhook/callback/', self.docusign_payload, format='json')
        self.assertEqual(response.status_code, 200)

    def test_webhook_for_driver_return_document_is_signed(self):
        self.client.post('/api/v1/docusign/webhook/callback/', self.docusign_payload, format='json')
        envelope_id = self.docusign_payload.get('data').get('envelopeId')
        dispatcher_service_agreement = DriverServiceAgreement.objects.get(envelope_id=envelope_id)
        self.assertTrue(dispatcher_service_agreement.is_signed)
