from .base import *

DOMAIN = env("DOMAIN")

DATABASES = {
    'default': {
        'ENGINE': env("POSTGRES_ENGINE"),
        'NAME': env("POSTGRESQL_DB"),
        'USER': env("POSTGRES_USER"),
        'PASSWORD': env("POSTGRES_PASSWORD"),
        'HOST': env("PG_HOST"),   # Or an IP Address that your DB is hosted on
        'PORT': env("PG_PORT"),
    }
}

# MYSQL_ENGINE=django.db.backends.mysql
# MYSQL_DB=user_management
# MYSQL_USER=root
# MYSQL_PASSWORD=root
# MYSQL_HOST=mysql-db
# MYSQL_PORT=3306
