# -*- coding: utf-8 -*-

from dj_rest_auth.jwt_auth import get_refresh_view
from dj_rest_auth.views import (  # PasswordChangeView,; PasswordResetConfirmView,; PasswordResetView,
    LoginView,
    LogoutView,
    UserDetailsView,
)
from django.urls import include, path
from rest_framework.decorators import authentication_classes
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .views import (
    DriverLoginView,
    InitiateSignUpViewset,
    NauvusBackRoomStaffLoginView,
    PasswordResetViewset,
    RegistrationViewset,
    UserInformationViewset,
    VerifySignUpOTPViewset,
)

# -----------------------------------------------------------------------------

app_name = "auth"
router = DefaultRouter()

router.register(
    r"initiate-signup", InitiateSignUpViewset, basename="initiate_signup"
)
router.register(
    r"verify-signup-otp", VerifySignUpOTPViewset, basename="verify_signup_otp"
)
router.register(r"signup", RegistrationViewset, basename="signup")
router.register(r"password", PasswordResetViewset, basename="password_reset")
router.register(
    r"user-information", UserInformationViewset, basename="user_information"
)


urlpatterns = [
    # Auth
    path(
        "login/",
        authentication_classes([])(LoginView).as_view(),
        name="user_login",
    ),
    path(
        "driver-login/",
        DriverLoginView.as_view(),
        name="driver_login",
    ),
    path(
        "nauvus-backroom-staff-login/",
        NauvusBackRoomStaffLoginView.as_view(),
        name="nauvus_backroom_staff_login",
    ),
    path("", include(router.urls)),
    path("token/refresh/", get_refresh_view().as_view(), name="token_refresh"),
    # path(
    #     "password/reset/confirm/",
    #     PasswordResetConfirmView.as_view(),
    #     name="user_password_reset_confirm",
    # ),
    # path(
    #     "password/change/",
    #     authentication_classes([JSONWebTokenAuthentication])(PasswordChangeView).as_view(),
    #     name="rest_password_change",
    # ),
    path(
        "logout/",
        authentication_classes([])(LogoutView).as_view(),
        name="user_logout",
    ),
    path(
        "user/",
        authentication_classes([JSONWebTokenAuthentication])(
            UserDetailsView
        ).as_view(),
        name="rest_user_details",
    ),
]
