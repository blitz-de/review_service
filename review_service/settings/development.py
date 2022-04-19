from .base import *

DOMAIN = env("DOMAIN")

DATABASES = {
    'default': {
        'ENGINE': env("POSTGRES_ENGINE"),
        'NAME': env("POSTGRES_DB"),
        'USER': env("POSTGRES_USER"),
        'PASSWORD': env("POSTGRES_PASSWORD"),
        'HOST': env("PG_HOST"),   # Or an IP Address that your DB is hosted on
        'PORT': env("PG_PORT"),
    }
}