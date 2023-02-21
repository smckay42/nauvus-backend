import random
import uuid

# from nauvus.users.utils import returnUserName
from django.contrib.auth.models import AbstractUser
from django.db.models import CASCADE, BooleanField, CharField, EmailField, ForeignKey, Index, UUIDField
from django.utils.translation import gettext_lazy as _

from nauvus.base.models import BaseModel

us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}

# invert the dictionary
abbrev_to_us_state = dict(map(reversed, us_state_to_abbrev.items()))


class SignUpOtpVerification(BaseModel):
    """
    SignUpOtpVerification for the OTP verification of the User.
    """

    phone = CharField(_("Phone no"), max_length=20)
    otp = CharField(_("OTP"), max_length=10)
    signup_process_id = UUIDField(_("Uuid"), max_length=100, default=uuid.uuid4)
    verified = BooleanField(default=False)


# class PasswordResetOtpVerification(BaseModel):
#     """
#     PasswordResetOtpVerification for the OTP verification of the User.
#     """

#     email = CharField(_("Email "), max_length=20)
#     otp = CharField(_("OTP"), max_length=10)
#     verified = BooleanField(default=False)
#     reset_process_id = UUIDField(_("Uuid"), max_length=100, default=uuid.uuid4)


class EmailUpdateOtpVerification(BaseModel):
    """
    EmailUpdateOtpVerification for the email update verification.
    """

    email = CharField(_("Email "), max_length=50)
    otp = CharField(_("OTP"), max_length=10)


class LowercaseEmailField(EmailField):
    def get_prep_value(self, value):
        return str(value).lower()


class User(AbstractUser):
    """
    Default custom user model for Nauvus.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    DISPATCHER = "dispatcher"
    CARRIER_OWNER = "carrier_owner"
    DRIVER = "driver"
    CARRIER_OWNER_OPERATOR = "carrier_admin_operator"
    NAUVUS_BACKROOM_STAFF = "nauvus_backroom_staff"
    NAUVUS_ADMINISTRATOR = "nauvus_administrator"

    USER_TYPES = (
        (DISPATCHER, "Dispatcher"),
        (CARRIER_OWNER, "Carrier Admin"),
        (CARRIER_OWNER_OPERATOR, "Carrier Admin Operator"),
        (NAUVUS_BACKROOM_STAFF, "Nauvus Backroom Staff"),
        (NAUVUS_ADMINISTRATOR, "Nauvus Administrator"),
        (DRIVER, "Driver"),
    )

    email = LowercaseEmailField(_("Email"), unique=True, null=True, blank=True, default=None)
    phone = CharField(_("Phone no"), max_length=20)
    user_type = CharField(_("User Type"), blank=True, choices=USER_TYPES, max_length=30)
    password_reset_key = CharField(max_length=15, blank=True, null=True)
    email_reset_key = CharField(max_length=15, blank=True, null=True)
    stripe_customer_id = CharField(max_length=120, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.user_type != self.DRIVER:
            first_check = True
            username_exist = True
            while username_exist:
                if not self.email:
                    break
                elif first_check:
                    username = self.email.split("@")[0]
                    first_check = False
                else:
                    username = "{}{}".format(
                        self.email.split("@")[0],
                        "".join(random.choices("1234567890", k=4)),
                    )

                if not User.objects.filter(username=username).first():
                    self.username = username
                    username_exist = False
        return super().save(*args, **kwargs)

    REQUIRED_FIELDS = []

    class Meta:
        indexes = [
            Index(fields=["id"]),
            Index(fields=["email"]),
            Index(fields=["phone"]),
            Index(fields=["username"]),
            Index(fields=["user_type"]),
        ]


class Address(BaseModel):
    """
    User Address Model for Nauvus.
    Storing the User address According the User.
    """

    user = ForeignKey(User, null=True, blank=True, on_delete=CASCADE)
    street1 = CharField(_("Street1 Address"), null=True, blank=True, max_length=100)
    street2 = CharField(_("Street2 Address"), null=True, blank=True, max_length=100)
    city = CharField(_("City"), null=True, blank=True, max_length=50)
    state = CharField(_("State"), null=True, blank=True, max_length=50)
    zip_code = CharField(_("Zip"), null=True, blank=True, max_length=10)
    permenent_address = BooleanField(default=True)

    @staticmethod
    def get_state_abbreviation(state_name):
        if abbrev_to_us_state.get(state_name):
            return state_name

        abbrev = us_state_to_abbrev.get(state_name)
        return abbrev

    class Meta:
        indexes = [
            Index(fields=["id"]),
            Index(fields=["user"]),
        ]
