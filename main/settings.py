# type: ignore[reportAttributeAccessIssue]
import typing
from pathlib import Path
from urllib.parse import ParseResult
from urllib.parse import urlparse as _urlparse

import environ

from main.logging import log_render_extra_context
from main.sentry import SentryConfig

BASE_DIR = Path(__file__).resolve().parent.parent


@typing.overload
def urlparse(value: None) -> None: ...


@typing.overload
def urlparse(value: str) -> ParseResult: ...


def urlparse(value) -> ParseResult:
    if not value:
        return None
    return _urlparse(value.strip("/"))


env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=str,
    ADDITIONAL_ALLOWED_HOSTS=(list, []),
    APP_ENVIRONMENT=str,
    APP_TYPE=str,
    APP_RELEASE=(str, None),
    APP_LOG_LEVEL=(str, "INFO"),
    # Domain configs
    APP_DOMAIN=str,
    FRONTEND_DOMAIN=str,
    SESSION_COOKIE_DOMAIN=str,  # .example.com
    CSRF_COOKIE_DOMAIN=str,  # .example.com
    ADDITIONAL_TRUSTED_ORIGINS=(list, []),
    TIME_ZONE=(str, "UTC"),
    # Database
    POSTGRES_DB=str,
    POSTGRES_USER=str,
    POSTGRES_PASSWORD=str,
    POSTGRES_HOST=str,
    POSTGRES_PORT=(int, 5432),
    # Storage
    MEDIA_URL=(str, "media/"),
    STATIC_URL=(str, "static/"),
    TEMP_DIR=(str, "/temp/"),
    # -- S3 storage
    AWS_S3_ENABLED=(bool, False),
    AWS_S3_ENDPOINT_URL=(str, None),
    AWS_S3_ACCESS_KEY_ID=str,
    AWS_S3_SECRET_ACCESS_KEY=str,
    AWS_S3_REGION_NAME=str,
    AWS_S3_MEDIA_BUCKET_NAME=str,
    AWS_S3_STATIC_BUCKET_NAME=str,
    # Sentry
    SENTRY_ENABLED=(bool, False),
    SENTRY_DEBUG=(bool, False),
    SENTRY_DSN=(str, None),
    SENTRY_TRACES_SAMPLE_RATE=(float, 0.2),
    SENTRY_PROFILE_SAMPLE_RATE=(float, 0.2),
    # -- Filesystem (default) XXX: Don't use in production
    MEDIA_ROOT=(str, BASE_DIR / "data/media"),
    STATIC_ROOT=(str, BASE_DIR / "data/static"),
)

APP_DOMAIN = urlparse(env("APP_DOMAIN"))
FRONTEND_DOMAIN = urlparse(env("FRONTEND_DOMAIN"))
APP_ENVIRONMENT = env("APP_ENVIRONMENT").upper()
APP_TYPE = env("APP_TYPE").upper()
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DEBUG")
APP_RELEASE = env("APP_RELEASE")

ALLOWED_HOSTS = [
    APP_DOMAIN.hostname,
    *env("ADDITIONAL_ALLOWED_HOSTS"),
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "corsheaders",
    "rest_framework",
    "strawberry_django",
    # - Health-check
    "health_check",  # required
    # Local apps
    "apps.common",
    "apps.geo",
    "apps.users",
    "apps.reports",
    "apps.content",
    "apps.dashboards",
    "apps.emergency",
    "apps.gallery",
    "apps.teams",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "main.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "main.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
    },
}

AUTH_USER_MODEL = "users.User"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TIME_ZONE")
USE_I18N = True
USE_TZ = True

TEMP_DIR = Path(env("TEMP_DIR"))
MEDIA_URL = env("MEDIA_URL")
STATIC_URL = env("STATIC_URL")


if env("AWS_S3_ENABLED"):
    AWS_S3_CONFIG_OPTIONS = {
        "endpoint_url": env("AWS_S3_ENDPOINT_URL"),
        "access_key": env("AWS_S3_ACCESS_KEY_ID"),
        "secret_key": env("AWS_S3_SECRET_ACCESS_KEY"),
        "region_name": env("AWS_S3_REGION_NAME"),
    }

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                **AWS_S3_CONFIG_OPTIONS,
                "bucket_name": env("AWS_S3_MEDIA_BUCKET_NAME"),
                "querystring_auth": False,
                "location": "media/",
                "file_overwrite": False,
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                **AWS_S3_CONFIG_OPTIONS,
                "bucket_name": env("AWS_S3_STATIC_BUCKET_NAME"),
                "querystring_auth": False,
                "location": "static/",
                "file_overwrite": True,
            },
        },
    }

else:
    # Filesystem
    MEDIA_ROOT = env("MEDIA_ROOT")
    STATIC_ROOT = env("STATIC_ROOT")

TRUSTED_ORIGINS = [
    APP_DOMAIN.geturl(),
    FRONTEND_DOMAIN.geturl(),
    *env("ADDITIONAL_TRUSTED_ORIGINS"),
]

SESSION_COOKIE_NAME = f"ERCS-{APP_ENVIRONMENT}-SESSIONID"
CSRF_COOKIE_NAME = f"ERCS-{APP_ENVIRONMENT}-CSRFTOKEN"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSP_DEFAULT_SRC = ["'self'"]
SECURE_REFERRER_POLICY = "same-origin"
if APP_DOMAIN.scheme == "https":
    SESSION_COOKIE_NAME = f"__Secure-{SESSION_COOKIE_NAME}"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SECURE_HSTS_SECONDS = 30  # TODO: Increase this slowly
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    CSRF_TRUSTED_ORIGINS = TRUSTED_ORIGINS

# -- https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-SESSION_COOKIE_DOMAIN
SESSION_COOKIE_DOMAIN = env("SESSION_COOKIE_DOMAIN")
# https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-cookie-domain
CSRF_COOKIE_DOMAIN = env("CSRF_COOKIE_DOMAIN")


# CORS
CORS_ALLOWED_ORIGINS = TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = TRUSTED_ORIGINS

CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r"(^/media/.*$)|(^/graphql/$)|(^/health-check/$)"
CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

CORS_ALLOW_HEADERS = (
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)
# Strawberry
STRAWBERRY_DJANGO = {
    "FIELD_DESCRIPTION_FROM_HELP_TEXT": True,
    "TYPE_DESCRIPTION_FROM_MODEL_DOCSTRING": True,
    "MUTATIONS_DEFAULT_HANDLE_ERRORS": True,
    "PAGINATION_DEFAULT_LIMIT": 20,
    "DEFAULT_PK_FIELD_NAME": "id",
}


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.SessionAuthentication",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

if DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
        *REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"],
        "rest_framework.renderers.BrowsableAPIRenderer",
    )

# Sentry Config
SENTRY_ENABLED = env("SENTRY_ENABLED")

if SENTRY_ENABLED:
    SENTRY_CONFIG = SentryConfig(
        dsn=env("SENTRY_DSN"),
        debug=env("SENTRY_DEBUG"),
        app_type=APP_TYPE,
        release=APP_RELEASE,
        environment=APP_ENVIRONMENT,
        send_default_pii=True,
        traces_sample_rate=env("SENTRY_TRACES_SAMPLE_RATE"),
        profiles_sample_rate=env("SENTRY_PROFILE_SAMPLE_RATE"),
        # Custom configs
        tags={"site": APP_DOMAIN.geturl()},
    )
    SENTRY_CONFIG.init_sentry()


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "render_extra_context": {
            "()": "django.utils.log.CallbackFilter",
            "callback": log_render_extra_context,
        },
    },
    "formatters": {
        "simple": {
            "format": ("%(asctime)s: - %(customThreadName)s/%(levelname)s - %(name)s - %(message)s %(context)s"),
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "filters": ["render_extra_context"],
        },
    },
    "loggers": {
        **{
            app: {
                "level": env("APP_LOG_LEVEL"),
                "handlers": ["console"],
                "propagate": False,
            }
            for app in ["apps", "main", "utils", "django"]
        },
    },
    "root": {
        "level": env("APP_LOG_LEVEL"),
        "handlers": ["console"],
    },
}

if DEBUG:
    LOGGING = {
        **LOGGING,
        "formatters": {
            **LOGGING["formatters"],
            "colored_verbose": {
                "()": "colorlog.ColoredFormatter",
                "format": (
                    "%(log_color)s%(asctime)s: %(customThreadName)s - %(levelname)-s%(red)s %(name)-s%(reset)s "
                    "%(blue)s%(message)s %(context)s"
                ),
            },
        },
        "handlers": {
            **LOGGING["handlers"],
            "colored_console": {
                "class": "logging.StreamHandler",
                "formatter": "colored_verbose",
                "filters": ["render_extra_context"],
            },
        },
        "loggers": {
            **{
                key: {
                    **logger,
                    "handlers": ["colored_console"],
                }
                for key, logger in LOGGING["loggers"].items()
            },
        },
        "root": {
            "level": env("APP_LOG_LEVEL"),
            "handlers": ["colored_console"],
        },
    }
