# dublicate and rename to local.py when pulling for the first time
import os
import datetime
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "2bblpw#g8^52*jyyvt5dv8@n5!pv**zkw6*d5@09crr%!6547+"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "jet",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "django_rest_passwordreset",
    # 'knox',
    "namastenepal.accounts",
    "namastenepal.community",
    "namastenepal.usermodule",
    "namastenepal.core",
    "namastenepal.posts",
    "namastenepal.points",
    "namastenepal.quiz",
    "namastenepal.channels_app.apps.ChannelsAppConfig",
    "graphene_django",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "namastenepal.urls"

AUTH_USER_MODEL = "core.User"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles"),
]

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static-cdn-local")


MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


CORS_URLS_REGEX = r"^/api.*"
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = ("*",)

# REST_FRAMEWORK = {
#     'DEFAULT_PERMISSION_CLASSES': (
#         'rest_framework.permissions.IsAuthenticated',
#     ),
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
#         'rest_framework.authentication.SessionAuthentication',
#         'rest_framework.authentication.BasicAuthentication',
#     ),
# }

JWT_AUTH = {
    "JWT_RESPONSE_PAYLOAD_HANDLER": "namastenepal.accounts.utils.jwt_response_handler",
    "JWT_EXPIRATION_DELTA": datetime.timedelta(seconds=300000),
}

FILE_UPLOAD_MAX_MEMORY_SIZE = 2000000000
DATA_UPLOAD_MAX_MEMORY_SIZE = 2000000000

## channels config

ASGI_APPLICATION = "namastenepal.channels_app.routing.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": ["redis://localhost:6379"]},
    },
}


PREPEND_WWW = False
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None

# TWILIO
TWILIO_ACCOUNT_SID = "ACcbd163457f1aabe811ff863acd39dfa0"
TWILIO_AUTH_TOKEN = "48b03add406a485abb63d8f45ffb097f"
VERIFICATION_SID = "VAb6431f85b6f58525ecd1fe48bb80306c"


GRAPHENE = {"SCHEMA": "namastenepal.schema.schema"}  # Where your Graphene schema lives
