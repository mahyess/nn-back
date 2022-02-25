import datetime
import os

from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool)

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    "django_admin_mazer",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_countries",
    "storages",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "django_rest_passwordreset",
    # 'knox',
    "namastenepal.accounts.apps.AccountsConfig",
    "namastenepal.community.apps.CommunityConfig",
    "namastenepal.usermodule.apps.UsermoduleConfig",
    "namastenepal.core.apps.CoreConfig",
    "namastenepal.posts.apps.PostsConfig",
    "namastenepal.points.apps.PointsConfig",
    "namastenepal.quiz.apps.QuizConfig",
    "namastenepal.chat_messages.apps.ChatMessagesConfig",
    "namastenepal.notifications.apps.NotificationsConfig",
    "firebase.apps.FirebaseConfig",
    "channels",
    "namastenepal.channels_app.apps.ChannelsAppConfig",
    # "graphene_django",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

AUTHENTICATION_BACKENDS = ("namastenepal.backends.CaseInsensitiveModelBackend",)

ROOT_URLCONF = "namastenepal.urls"

AUTH_USER_MODEL = "core.User"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            os.path.join(BASE_DIR, "namastenepal", "accounts", "templates"),
            os.path.join(BASE_DIR, "frontend-namaste-nepal"),
        ],
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

WSGI_APPLICATION = "namastenepal.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "ATOMIC_REQUESTS": True,
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": "",
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kathmandu"
# TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

# USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "static-cdn-local")
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
# media


MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

CORS_URLS_REGEX = r"^/api.*"
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = [
#     '*',
# ]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.UserRateThrottle",
        # 'rest_framework.throttling.AnonRateThrottle',
    ),
    "DEFAULT_THROTTLE_RATES": {
        "loginAttempts": "6/hr",
        "user": "1000/min",
    },
}

JWT_AUTH = {
    "JWT_RESPONSE_PAYLOAD_HANDLER": "namastenepal.accounts.utils.jwt_response_handler",
    "JWT_EXPIRATION_DELTA": datetime.timedelta(days=7),
    "JWT_SECRET_KEY": config("JWT_SECRET"),
    # 'JWT_ALLOW_REFRESH': True
}

FILE_UPLOAD_MAX_MEMORY_SIZE = 2000000000
DATA_UPLOAD_MAX_MEMORY_SIZE = 2000000000

# channels config
ASGI_APPLICATION = "namastenepal.channels_app.routing.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [('redis', 6379)], },
    },
}

# registration
SITE_ID = 1

# jet
JET_SIDE_MENU_COMPACT = True

# logger
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "namastenepal.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "propagate": True,
            "level": "DEBUG" if config("DEBUG", cast=bool) else "INFO",
        },
        "namastenepal": {
            "handlers": ["file"],
            "level": "DEBUG",
        },
    },
}

if os.name == "nt":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": os.path.join(BASE_DIR, "caches"),
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": "127.0.0.1:11211",
        }
    }

# Number of seconds of inactivity before a user is marked offline
USER_ONLINE_TIMEOUT = 300

# Number of seconds that we will keep track of inactive users before
# their last seen is removed from the cache
USER_LASTSEEN_TIMEOUT = 60 * 60 * 24 * 7

# TWILIO
TWILIO_ACCOUNT_SID = "ACcbd163457f1aabe811ff863acd39dfa0"
TWILIO_AUTH_TOKEN = "48b03add406a485abb63d8f45ffb097f"
VERIFICATION_SID = "VAb6431f85b6f58525ecd1fe48bb80306c"

GRAPHENE = {"SCHEMA": "namastenepal.schema.schema"}  # Where your Graphene schema lives

DEFAULT_EMAIL = config("EMAIL_USER")

# for jet admin panel
JET_PROJECT = 'namastenepal_2'
JET_TOKEN = '42cf7e56-de5e-4280-9462-99afa7c4033c'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
