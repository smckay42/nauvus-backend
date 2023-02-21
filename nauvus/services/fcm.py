L = logger.getChild(__name__)
from fcm_django.models import FCMDevice
class FCMClient(object):
    @staticmethod
    def send_fcm_message(
        title=None,
        body=None,
        data=None,
        sound=None,
        user_devices=None,
    ):
        """Send FCM Messages"""
        try:
            data["title"] = title
            data["body"] = body
            kwargs = {
                "content_available": True,
            }
            extra_kwargs = {
                "apns-priority": "5",
            }
            push_notification_response = {}
            if user_devices:
                push_notification_response = user_devices.send_message(
                    # title=title,
                    # body=body,
                    data=data,
                    # sound=sound,
                    extra_kwargs=extra_kwargs,
                    **kwargs
                )
            return push_notification_response
        except Exception as e:
            print("Error :: ", e)
            L.error("Failed to send email")
            L.error(e)
