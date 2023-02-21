"""
Base settings to build other settings files upon.
"""
import datetime
from pathlib import Path

import environ

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
# nauvus/
APPS_DIR = ROOT_DIR / "nauvus"
env = environ.Env()

# READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
# if READ_DOT_ENV_FILE:
#     # OS environment variables take precedence over variables from .env
env.read_env(str(ROOT_DIR / ".env"))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "UTC"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [str(ROOT_DIR / "locale")]

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "psqlextra.backend",
        "NAME": env("APP_DB_NAME"),
        "USER": env("APP_DB_USER"),
        "PASSWORD": env("APP_DB_PASSWORD"),
        "HOST": env("APP_DB_HOST"),
        "PORT": env("APP_DB_PORT"),
    },
    # "search": {
    #     "ENGINE": "djongo",
    #     "NAME": env("MONGODB_NAME", default="1234"),
    #     "HOST": env("MONGODB_HOST", default="127.0.0.1"),
    #     "PORT": env("MONGODB_PORT", default="27017"),
    #     "DB_NAME": env("MONGODB_DATABASE", default="nauvus"),
    #     "USER": env("MONGODB_USER", default="root"),
    #     "PASSWORD": env("MONGODB_PASSWORD", default="password"),
    # },
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASE_ROUTERS = ["config.default_db_router.DefaultDatabaseRouter"]
# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    "django.contrib.admin",
    "django.forms",
    "django.contrib.postgres",
    "psqlextra",
    "django.contrib.humanize",
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "django_celery_beat",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt.token_blacklist",
    "dj_rest_auth",
    "corsheaders",
    "drf_yasg",
    "fcm_django",
    "django_filters",
    # "cities",
]

LOCAL_APPS = [
    # "nauvus.users",
    "config",
    "nauvus.users.apps.CoreConfig",
    "nauvus.apps.carrier.apps.CarrierConfig",
    "nauvus.apps.dispatcher.apps.DispatcherConfig",
    "nauvus.apps.broker.apps.BrokerConfig",
    "nauvus.apps.driver.apps.DriverConfig",
    "nauvus.apps.vehicle.apps.VehicleConfig",
    "nauvus.apps.loads.apps.LoadsConfig",
    "nauvus.apps.cities.apps.CitiesAppConfig",
    "nauvus.apps.nauvus_admin.apps.NauvusAdminConfig",
    # "nauvus.apps.citiesapp.apps.CitiesappConfig",
    "nauvus.apps.bookings.apps.BookingsConfig",
    "nauvus.apps.notifications.apps.NotificationsConfig",
    "nauvus.apps.payments.apps.PaymentsConfig",
    "nauvus.apps.banking.apps.BankingConfig",
    "nauvus.apps.invitations.apps.InvitationsConfig",
    "nauvus.apps.webhooks.apps.WebhookConfig",
    # Your stuff: custom apps go here
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "nauvus.contrib.sites.migrations"}

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "users:redirect"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "account_login"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ORIGIN_ALLOW_ALL = True

OTP_CODE_OVERRIDE = env("OTP_CODE_OVERRIDE", default=None)

FRONTEND_URL = env("FRONTEND_URL", default="https://staging.nauvus.com/")

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR / "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR / "static")]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR / "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#dirs
        "DIRS": [str(APPS_DIR / "templates")],
        # https://docs.djangoproject.com/en/dev/ref/settings/#app-dirs
        "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "nauvus.users.context_processors.allauth_settings",
            ],
        },
    }
]

# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5
SERVER_EMAIL = "noreply@nauvus.com"

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""Nauvus""", "justin@nauvus.com")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": " {levelname} {asctime} {name} {funcName} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "django-handler": {
            "class": "logging.FileHandler",
            "filename": f"{ROOT_DIR}/logs/django.log",
            "formatter": "verbose",
        },
        "stripe-handler": {
            "class": "logging.FileHandler",
            "filename": f"{ROOT_DIR}/logs/stripe.log",
            "formatter": "verbose",
        },
        "file-handler": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": f"{ROOT_DIR}/logs/output.log",
            "formatter": "verbose",
            "when": "midnight",
        },
    },
    "root": {"level": env("LOG_LEVEL", default="INFO"), "handlers": ["console", "file-handler"]},
    "loggers": {
        "django": {
            "handlers": ["django-handler"],
            "level": "WARNING",
            "propagate": False,
        },
        "stripe": {
            "handlers": ["stripe-handler"],
            "level": env("LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
    },
}

# Celery
# ------------------------------------------------------------------------------
if USE_TZ:
    # https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-timezone
    CELERY_TIMEZONE = TIME_ZONE
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ["json"]
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = "json"
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = "json"
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERY_TASK_TIME_LIMIT = 5 * 60
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-soft-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERY_TASK_SOFT_TIME_LIMIT = 60
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#beat-scheduler
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = "email"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_REQUIRED = True
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_ADAPTER = "nauvus.users.adapters.AccountAdapter"
# https://django-allauth.readthedocs.io/en/latest/forms.html
ACCOUNT_FORMS = {"signup": "nauvus.users.forms.UserSignupForm"}
# https://django-allauth.readthedocs.io/en/latest/configuration.html
SOCIALACCOUNT_ADAPTER = "nauvus.users.adapters.SocialAccountAdapter"
# https://django-allauth.readthedocs.io/en/latest/forms.html
SOCIALACCOUNT_FORMS = {"signup": "nauvus.users.forms.UserSocialSignupForm"}
# django-rest-auth
# ------------------------------------------------------------------------------
REST_AUTH_SERIALIZERS = {
    "JWT_SERIALIZER": "nauvus.auth.api.serializers.JWTSerializer",
}

# django-compressor
# ------------------------------------------------------------------------------
# https://django-compressor.readthedocs.io/en/latest/quickstart/#installation
INSTALLED_APPS += ["compressor"]
STATICFILES_FINDERS += ["compressor.finders.CompressorFinder"]

# django-compressor
# ------------------------------------------------------------------------------
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_ENABLED
COMPRESS_ENABLED = env.bool("COMPRESS_ENABLED", default=True)
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_URL
COMPRESS_URL = STATIC_URL  # noqa F405
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_OFFLINE
COMPRESS_OFFLINE = True  # Offline compression is required when using Whitenoise
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_FILTERS
COMPRESS_FILTERS = {
    "css": [
        "compressor.filters.css_default.CssAbsoluteFilter",
        "compressor.filters.cssmin.rCSSMinFilter",
    ],
    "js": ["compressor.filters.jsmin.JSMinFilter"],
}


# django-rest-framework
# -------------------------------------------------------------------------------
# django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",  # 'iso-8601'
    "DATE_FORMAT": "%Y-%m-%d",
    "TIME_FORMAT": "%H:%M:%S",
    "DATETIME_INPUT_FORMATS": ["%Y-%m-%d %H:%M:%S"],
    "DEFAULT_RENDERER_CLASSES": ["nauvus.api.renderers.BaseJSONRenderer"],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
        # "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
        # "rest_framework.authentication.BasicAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "STRICT_JSON": False,
    "ORDERING_PARAM": "order_by",
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework_filters.backends.RestFrameworkFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
}


REST_USE_JWT = True

JWT_AUTH = {
    "JWT_ENCODE_HANDLER": "rest_framework_jwt.utils.jwt_encode_handler",
    "JWT_DECODE_HANDLER": "rest_framework_jwt.utils.jwt_decode_handler",
    "JWT_PAYLOAD_HANDLER": "rest_framework_jwt.utils.jwt_payload_handler",
    "JWT_PAYLOAD_GET_USER_ID_HANDLER": "rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler",
    "JWT_RESPONSE_PAYLOAD_HANDLER": "rest_framework_jwt.utils.jwt_response_payload_handler",
    "JWT_GET_USER_SECRET_KEY": None,
    "JWT_PUBLIC_KEY": None,
    "JWT_PRIVATE_KEY": None,
    "JWT_ALGORITHM": "HS256",
    "JWT_VERIFY": True,
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_LEEWAY": 0,
    "JWT_EXPIRATION_DELTA": datetime.timedelta(hours=24),
    "JWT_AUDIENCE": None,
    "JWT_ISSUER": None,
    "JWT_ALLOW_REFRESH": False,
    "JWT_REFRESH_EXPIRATION_DELTA": datetime.timedelta(days=7),
    "JWT_AUTH_HEADER_PREFIX": "JWT",
    "JWT_AUTH_COOKIE": None,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(days=1),
}

# #  cities
# CITIES_COUNTRY_MODEL = 'nauvus.apps.citiesapp.models.CustomCountryModel'

# django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
CORS_URLS_REGEX = r"^/api/.*$"

# Your stuff...
# ------------------------------------------------------------------------------

ADMIN_EMAIL = env("ADMIN_EMAIL", default="admin@nauvus.com")
ADMIN_PASSWORD = env("ADMIN_PASSWORD", default="admin@123")


# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
#     ROOT_DIR, ""
# )  # noqa


# Docusign

DOCUSIGN_CLIENT_AUTH_ID = env("DOCUSIGN_CLIENT_AUTH_ID", default="")
DOCUSIGN_CLIENT_USER_ID = env("DOCUSIGN_CLIENT_USER_ID", default="")
DOCUSIGN_ACCOUNT_ID = env("DOCUSIGN_ACCOUNT_ID", default="")
DOCUSIGN_BASE_PATH = env("DOCUSIGN_BASE_PATH", default="")
DOCUSIGN_TEMPLATE_ID = env("DOCUSIGN_TEMPLATE_ID", default="")

# 123LoadBoard

LOADBOARD_CLIENT_ID = env("LOADBOARD_CLIENT_ID", default="")
LOADBOARD_CLIENT_SECRET = env("LOADBOARD_CLIENT_SECRET", default="")
LOADBOARD_USERNAME = env("LOADBOARD_USERNAME", default="")
LOADBOARD_PASSWORD = env("LOADBOARD_PASSWORD", default="")
LOADBOARD_URL = env("LOADBOARD_URL", default="")

# MonGoDB
MONOGO_DB_NAME = env("MONOGO_DB_NAME", default="test")
MONGODB_HOST = env("MONGODB_HOST", default="127.0.0.1")

# Stirpe Payment Gateway
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", default="1234")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="1234")
STRIPE_PRODUCT_ID = env("STRIPE_PRODUCT_ID")
STRIPE_ENDPOINT_SECRET = env("STRIPE_ENDPOINT_SECRET")

# App Url
APP_URL = env("APP_URL", default="")

# OATFI URL & Credentials
OATFI_API_KEY = env("OATFI_API_KEY", default="")
OATFI_URL = env("OATFI_URL", default="")
OATFI_PARTNER_ID = env("OATFI_PARTNER_ID", default="")
OATFI_STRIPE_ACCOUNT = env("OATFI_STRIPE_ACCOUNT", default="")
OATFI_FACTORING_PRODUCT_ID = env("OATFI_FACTORING_PRODUCT_ID", default="")

# FEES
NAUVUS_HANDLING_FEE_PERCENT = env("NAUVUS_HANDLING_FEE_PERCENT", default=1.0)
NAUVUS_FEE_ACCOUNT = env("NAUVUS_FEE_ACCOUNT", default="")


# Firebase Config
# FCM_DJANGO_SETTINGS = {"FCM_SERVER_KEY": env("FCM_SERVER_KEY")}

# FIREBASE_CREDS = env("FIREBASE_CREDS")
# cred = credentials.Certificate(FIREBASE_CREDS)
# firebase_admin.initialize_app(cred)
