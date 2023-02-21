from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from nauvus.users.models import (  # PasswordResetOtpVerification,
    Address,
    EmailUpdateOtpVerification,
    SignUpOtpVerification,
)
from django.utils.translation import gettext, gettext_lazy as _

User = get_user_model()


@admin.register(SignUpOtpVerification)
class SignUpOtpVerificationAdmin(admin.ModelAdmin):
    list_display = ["phone", "otp", "signup_process_id"]


# @admin.register(PasswordResetOtpVerification)
# class PasswordResetOtpVerificationAdmin(admin.ModelAdmin):
#     list_display = ["email", "otp", "reset_process_id"]


@admin.register(EmailUpdateOtpVerification)
class EmailUpdateOtpVerificationAdmin(admin.ModelAdmin):
    list_display = ["email", "otp"]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    list_display = [
        "id",
        "username",
        "first_name",
        "email",
        "is_superuser",
        "user_type",
    ]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "user_type",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "user",
        "street1",
        "street2",
        "state",
        "city",
        "zip_code",
    ]
