import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from celery import shared_task
from django.template.loader import get_template

from nauvus.services.docusign.docusign import docusign_worker
from nauvus.services.email_client import EmailClient
from nauvus.users.models import User

from ..apps.carrier.models import CarrierFleetApplication, CarrierW9Information


def send_mail_from_template(template_name, recipient_email, subject, template_values=None):
    try:
        subject = subject
        html_template = get_template(f"{template_name}.html")
        text_template = get_template(f"{template_name}.txt")

        context = template_values
        body = text_template.render(context)
        html_content = html_template.render(context)

        email_sent = EmailClient().send_email(subject, html_content, body, [recipient_email])
        if not email_sent:
            logging.error("Failed to send email.")

    except Exception as e:
        logging.error("Failed to send email: {error}".format(error=str(e)))


# helper function for password reset emails
def send_password_reset_mail(email, code):

    subject = "Password Reset Key"
    template = "auth/password_reset_email"

    send_mail_from_template(template, email, subject, {"code": code, "url": settings.FRONTEND_URL})


# helper function for sending mail invitations
def send_invitation_mail(
    email,
    organization_name=None,
    access_type=None,
    link="http://www.nauvus.com",
    owner_first_name=None,
    owner_last_name=None,
):

    subject = "You’ve been invited to Nauvus!"
    template = "invitation/invitation_email"

    context = {
        "organization_name": organization_name,
        "access_type": access_type,
        "link": link,
        "inviter_first_name": owner_first_name,
        "inviter_last_name": owner_last_name,
    }

    send_mail_from_template(template, email, subject, context)


@shared_task
def send_nauvus_service_agreement(user_id):

    user = User.objects.get(id=user_id)
    docusign_worker(user)


@shared_task
def send_welcome_mail(email=None, first_name=None, last_name=None):
    try:
        subject = "Welcome Mail"
        html_template = get_template("auth/welcome_email.html")
        text_template = get_template("auth/welcome_email.txt")

        context = {"first_name": first_name, "last_name": last_name}
        body = text_template.render(context)
        html_content = html_template.render(context)

        email_sent = EmailClient().send_email(subject, html_content, body, [email])
        if not email_sent:
            logging.error("Failed to send email from Sendgrid ")

    except Exception as e:
        logging.error("Failed to send email from Sendgrid : {error}".format(error=str(e)))


def send_documents(carrier_id=None, email=None, documents=None):
    try:
        kwargs = dict(
            to=[
                email,
            ],
            # from_email="testxyz@yopmail.com",
            from_email=settings.SERVER_EMAIL,
            subject="document",
            body="documents",
            # alternatives=((html_content, 'text/html'),)
        )
        files = []
        for document in documents:
            if document == "operating_authority_letter":
                operating_authority_letter = CarrierFleetApplication.objects.filter(carrier__id=carrier_id).first()
                if operating_authority_letter:
                    files.append(operating_authority_letter.operating_authority_letter.path)
            if document == "insurance_certificate":
                insurance_certificate = CarrierFleetApplication.objects.filter(carrier__id=carrier_id).first()
                if insurance_certificate:
                    files.append(insurance_certificate.insurance_certificate.path)
            if document == "business_documentation":
                business_documentation = CarrierFleetApplication.objects.filter(carrier__id=carrier_id).first()
                if business_documentation:
                    files.append(business_documentation.business_documentation.path)
            if document == "w9_document":
                w9_document = CarrierW9Information.objects.filter(carrier__id=carrier_id).first()
                if w9_document:
                    files.append(w9_document.w9_document.path)
        message = EmailMultiAlternatives(**kwargs)

        # file = CarrierFleetApplication.objects.last().insurance_certificate.path
        for file in files:
            message.attach_file(file)

        message.send()
    except Exception as e:
        logging.error("Failed to send email from Sendgrid : {error}".format(error=str(e)))
