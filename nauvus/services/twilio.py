import logging
import os

import phonenumbers
from twilio.rest import Client


class TwilioClient(object):

    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_from_number = os.environ.get("TWILIO_FROM_NUMBER")
    messaging_service_sid = os.environ.get("MESSAGING_SERVICE_SID")

    def __init__(self) -> None:
        self.client = Client(self.account_sid, self.auth_token)

    def send_sms(self, recipient, content):
        """Send SMS to the given phone number"""
        # Find your Account SID and Auth Token at twilio.com/console
        # and set the environment variables. See http://twil.io/secure
        recipient = phonenumbers.parse(recipient, "US")
        recipient = phonenumbers.format_number(
            recipient, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )

        try:
            message = self.client.messages.create(
                body=content,
                messaging_service_sid=self.messaging_service_sid,  # TODO: Change this to number
                to=recipient,
            )
            return message
        except Exception as e:
            logging.error(
                "Failed to send message from Twillio : {error}".format(error=str(e))
            )

        return None
