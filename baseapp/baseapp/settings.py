"""
Django settings for baseapp project.

Generated by 'django-admin startproject' using Django 3.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import logging
from pathlib import Path
import json
import time
import requests as req
import os

from django.conf import settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", default="asdasfas23i27rqwgerxsYA^S&DR^%ADC")

AUTH_USER_MODEL = "bot.ScheduleUser"

# 'DJANGO_ALLOWED_HOSTS' должен быть в виде одной строки с хостами разделенными символом пробела
# Для примера: 'DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]'

# SECURITY WARNING: don't run with debug turned on in production!

PRODUCTION_MODE = False

DOCKERIZED = bool(os.environ.get("DOCKERISED", default=False))

if DOCKERIZED:
    DEBUG = bool(os.environ.get("DEBUG", default=True))
    PRODUCTION_MODE = bool(os.environ.get("PROD_MODE", default=False))

    if PRODUCTION_MODE:
        LOG_FILE = "bottrace.log"
    else:
        LOG_FILE = None
    time.sleep(5)
    responce = req.get("http://ngrok:4040/api/tunnels")
    if responce.status_code == 200:
        ngrok_responce = responce.json()
        tunnel = ngrok_responce["tunnels"][0]
        if tunnel["proto"] == "http":
            DOMAIN = tunnel["public_url"][7:]
        elif tunnel["proto"] == "https":
            DOMAIN = tunnel["public_url"][8:]

        logging.info(f"\n\n\tDomain: {DOMAIN}\n\n")

    else:
        logging.exception(
            "GET request failed with status code {code}\nRequest:{req_str}".format(
                code=responce.status_code,
                req_str="http://localhost:4040/api/tunnels",
            )
        )
        raise ConnectionError("Cannot connect to api")

    DATA_UPLOAD = bool(int(os.environ.get("DATA_UPLOAD", default=False)))
    TOKEN = os.environ.get("API_TOKEN", default=None)
    CURRENT_WEEK = None

    logging.info(f"Config state:\n\tDATA_UPLOAD {DATA_UPLOAD}")

else:
    with open(f"{BASE_DIR}/appsettings.json", "r") as reader:
        json_doc = json.load(reader)
        DEBUG = json_doc["debug"]
        TOKEN = json_doc["api-token"]
        DOMAIN = json_doc["domain"]
        DATA_UPLOAD = json_doc["data-fetching"]
        LOG_FILE = None

LOG_LEVEL = int(os.environ.get("LOG_LEVEL", default=logging.DEBUG))
logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILE)

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", default="localhost 127.0.0.1 [::1]"
).split(" ")
ALLOWED_HOSTS.append(DOMAIN)
# Application definition


INSTALLED_APPS = [
    "bot.apps.BotConfig",
    "django.contrib.contenttypes",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "baseapp.urls"

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

WSGI_APPLICATION = "baseapp.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.mysql"),
        "NAME": os.environ.get("SQL_DATABASE", "TempDB"),
        "USER": os.environ.get("SQL_USER", "root"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "e3Vz2Ukgp99"),
        "HOST": os.environ.get("SQL_HOST", "127.0.0.1"),
        "PORT": os.environ.get("SQL_PORT", "3306"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/staticfiles/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
