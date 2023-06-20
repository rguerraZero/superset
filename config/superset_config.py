# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# This file is included in the final Docker image and SHOULD be overridden when
# deploying the image to prod. Settings configured here are intended for use in local
# development environments. Also note that superset_config_docker.py is imported
# as a final step as a means to override "defaults" configured here
#
import logging
import os
from typing import Optional
from datetime import timedelta
from flask_appbuilder.security.manager import AUTH_OAUTH
from custom_sso_security_manager import CustomSsoSecurityManager

from celery.schedules import crontab
from cachelib.redis import RedisCache
from superset.superset_typing import CacheConfig

logger = logging.getLogger()

# pylint: disable=too-many-lines


def get_env_variable(var_name: str, default: Optional[str] = None) -> str:
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        else:
            error_msg = "The environment variable {} was missing, abort...".format(
                var_name
            )
            raise EnvironmentError(error_msg)

FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
    "ESTIMATE_QUERY_COST": True,
    "ALERT_REPORTS": True,
    "ALLOW_FULL_CSV_EXPORT": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "ENABLE_TEMPLATE_REMOVE_FILTERS": True,
}

PREVIOUS_SECRET_KEY = 'CHANGE_ME_TO_A_COMPLEX_RANDOM_SECRET'
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY")
CURRENT_ENV = os.environ.get("ENV")
# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = get_env_variable("DATABASE_URL")
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 30
SQLALCHEMY_POOL_TIMEOUT = 180
REDIS_HOST = get_env_variable("CELERY_URL")
REDIS_PORT = get_env_variable("CELERY_PORT")
REDIS_CELERY_DB = get_env_variable("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = get_env_variable("REDIS_RESULTS_DB", "1")

CACHE_CONFIG: CacheConfig = {
    "CACHE_TYPE": "redis",
    "CACHE_DEFAULT_TIMEOUT": int(timedelta(days=1).total_seconds()), 
    "CACHE_KEY_PREFIX": "superset_cache",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
}

FILTER_STATE_CACHE_CONFIG: CacheConfig = {
    "CACHE_TYPE": "redis",
    "CACHE_DEFAULT_TIMEOUT": int(timedelta(days=1).total_seconds()), 
    "CACHE_KEY_PREFIX": "superset_filter_cache",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
}
EXPLORE_FORM_DATA_CACHE_CONFIG: CacheConfig = {
    "CACHE_TYPE": "redis",
    "CACHE_DEFAULT_TIMEOUT": int(timedelta(days=1).total_seconds()), 
    "CACHE_KEY_PREFIX": "superset_explore_cache",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
}
DATA_CACHE_CONFIG: CacheConfig = {
    "CACHE_TYPE": "redis",
    "CACHE_DEFAULT_TIMEOUT": int(timedelta(days=1).total_seconds()), 
    "CACHE_KEY_PREFIX": "superset_data_cache",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
}

RESULTS_BACKEND = RedisCache(
    host=REDIS_HOST, port=REDIS_PORT, key_prefix="superset_results"
)

SUPERSET_WEBSERVER_TIMEOUT = 300
SUPERSET_WEBSERVER_PROTOCOL = "https"

FILTER_SELECT_ROW_LIMIT = 100000
ROW_LIMIT = 500000
SQL_MAX_ROW = 5000000
DISPLAY_MAX_ROW = 10000
SAMPLES_ROW_LIMIT = 1000
ENABLE_TEMPLATE_PROCESSING = True

# # smtp server configuration
ALERT_REPORTS_NOTIFICATION_DRY_RUN = False
SMTP_HOST = get_env_variable("SENDGRID_HOST")
SMTP_STARTTLS = True
SMTP_SSL = False
SMTP_USER = get_env_variable("SENDGRID_USERNAME")
SMTP_PORT = get_env_variable("SENDGRID_PORT")
SMTP_PASSWORD = get_env_variable("SENDGRID_PASSWORD")
SMTP_MAIL_FROM = "superset@zerofox.com"
CLIENT_ID = get_env_variable("SSO_CLIENT_ID")
CLIENT_SECRET = get_env_variable("SSO_CLIENT_SECRET")
API_BASE_URL = get_env_variable("SSO_API_BASE_URL")

THUMBNAIL_SELENIUM_USER = "amason@zerofox.com"
WEBDRIVER_BASEURL = f"https://superset-{CURRENT_ENV}.zerofox.com"
WEBDRIVER_BASEURL_USER_FRIENDLY = WEBDRIVER_BASEURL
WEBDRIVER_TYPE = "chrome"
WEBDRIVER_OPTION_ARGS = [
    "--force-device-scale-factor=2.0",
    "--high-dpi-support=2.0",
    "--headless",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-extensions",
]
SCREENSHOT_LOCATE_WAIT = 100
SCREENSHOT_LOAD_WAIT = 600

# Set the authentication type to OAuth
AUTH_TYPE = AUTH_OAUTH

OAUTH_PROVIDERS = [
    {
        "name": "zfapi",
        "token_key": "access_token",  # Name of the token in the response of access_token_url
        "icon": "fa-address-card",  # Icon for the provider
        "remote_app": {
            "client_id": CLIENT_ID,  # Client Id (Identify Superset application)
            "client_secret": CLIENT_SECRET,
            "access_token_method": "POST",
            "api_base_url": API_BASE_URL,
            "access_token_url": f"{API_BASE_URL}/o/token",
            "authorize_url": f"{API_BASE_URL}/o/authorize",
        },
    }
]

# Will allow user self registration, allowing to create Flask users from Authorized User
# AUTH_USER_REGISTRATION = True

# # The default user self registration role
# AUTH_USER_REGISTRATION_ROLE = "Public"

# CUSTOM_SECURITY_MANAGER = CustomSsoSecurityManager

class CeleryConfig:  # pylint: disable=too-few-public-methods
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = ("superset.sql_lab",)
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    worker_prefetch_multiplier = 1
    task_acks_late = False
    task_annotations = {
        "sql_lab.get_sql_results": {"rate_limit": "100/s"},
        "email_reports.send": {
            "rate_limit": "1/s",
            "time_limit": int(timedelta(seconds=120).total_seconds()),
            "soft_time_limit": int(timedelta(seconds=150).total_seconds()),
            "ignore_result": True,
        },
    }
    beat_schedule = {
        "email_reports.schedule_hourly": {
            "task": "email_reports.schedule_hourly",
            "schedule": crontab(minute=1, hour="*"),
        },
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=0, hour=0),
        },
    }

CELERY_CONFIG = CeleryConfig   # pylint: disable=invalid-name