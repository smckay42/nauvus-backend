import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Wrapper client to talk to an email server
class EmailClient(object):
    @staticmethod
    def send_email(subject, html_content, body, to_emails):
        """Send Emails"""
        try:
            from_email = settings.SERVER_EMAIL
            msg = EmailMultiAlternatives(subject, body, from_email, to_emails)
            msg.attach_alternative(html_content, "text/html")
            email_sent = msg.send()
            return email_sent
        except Exception as e:
            logging.error("Failed to send email: {error}".format(error=str(e)))

        return None

    @staticmethod
    def send_html_email(subject, receiver, template_name, context, attachments=None):
        """
        Send HTML email and support multiple attachments and receivers.
        """

        body = render_to_string(template_name, context=context)

        message = EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL, receiver.split(';'))
        message.attach_alternative(body, "text/html")

        if attachments:
            if isinstance(attachments, list):
                for attachment in attachments:
                    message.attach_file(attachment)
            else:
                message.attach_file(attachments)
        message.send()
