from typing import (
    Optional,
)
import os
import logging
from superset.security import SupersetSecurityManager

from bi_superset.bi_security_manager.models.user import User as ZFUser
from bi_superset.bi_security_manager.models.access_method import AccessMethod
from bi_superset.bi_security_manager.models.access_origin import AccessOrigin
from bi_superset.bi_security_manager.services.user_service import UserService
from flask import current_app

logger = logging.getLogger(__name__)


class BICustomSecurityManager(SupersetSecurityManager):
    def __init__(self, appbuilder):
        super(BICustomSecurityManager, self).__init__(appbuilder)

        self._access_method = os.getenv("SUPERSET_ACCESS_METHOD", None)
        self._access_origin = AccessOrigin.SUPERSET_UI.value

        # Validates that the access method is set
        if not any(method.value == self._access_method for method in AccessMethod):
            raise Exception("CONFIGURATION SUPERSET_ACCESS_METHOD is not set")

    def oauth_user_info(self, provider, response=None):
        zf_api_host = current_app.config.get("ZF_API_HOST")
        logger.debug("Oauth2 provider: {0}.".format(provider))
        if provider == "zfapi":
            me = (
                self.appbuilder.sm.oauth_remotes[provider]
                .get(f"{zf_api_host}/1.0/users/me/")
                .json()
            )
            details = {
                "id": me["id"],
                "username": me["email"],
                "email": me["email"],
                "first_name": me["first_name"],
                "last_name": me["last_name"],
                "is_staff": me.get("is_staff", False),
                "is_active": me.get("is_active", False),
                "enterprise_id": me.get("enterprises_id", None),
            }

            return details

    def auth_user_oauth(self, userinfo):
        user = super(BICustomSecurityManager, self).auth_user_oauth(userinfo)
        zf_user: ZFUser = ZFUser.from_dict(userinfo)

        if not zf_user.is_active:
            return None
        if (
            AccessMethod.is_internal(self._access_method)
            and zf_user.is_internal_user is False
        ):
            return None

        userService = UserService(self._access_method, self._access_origin, self)
        user = userService.update_roles_rls(user, zf_user)
        return user
