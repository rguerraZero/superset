from typing import (
    Optional,
)
import os
import logging
from superset.security import SupersetSecurityManager

from bi_superset.bi_security_manager.models.user import User as ZFUser
from bi_superset.bi_security_manager.models.access_method import AccessMethod


class BICustomSecurityManager(SupersetSecurityManager):
    def __init__(self, appbuilder):
        super(BICustomSecurityManager, self).__init__(appbuilder)

        self._access_method = os.getenv("SUPERSET_ACCESS_METHOD", None)

        # Validates that the access method is set
        if not any(method.value == self._access_method for method in AccessMethod):
            raise Exception("CONFIGURATION SUPERSET_ACCESS_METHOD is not set")

    def oauth_user_info(self, provider, response=None):
        logging.debug("Oauth2 provider: {0}.".format(provider))
        if provider == "zfapi":
            me = (
                self.appbuilder.sm.oauth_remotes[provider]
                .get("https://api.zerofox.com/1.0/users/me/")
                .json()
            )
            logging.info(response)
            logging.debug("user_data: {0}".format(me))
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
        logging.debug(f" Current User: {user} ")
        logging.debug(f" User Info: {userinfo}")

        zf_user: ZFUser = ZFUser.from_dict(userinfo)

        # When external user want to access internal system do not authenticate
        if (
            self._access_method == AccessMethod.INTERNAL.value
            and zf_user.is_internal_user is False
        ):
            return None

        user = self.check_and_update_user_role(user, zf_user)

        user = self.check_and_update_user_rls(user, zf_user)

        return user

    def check_and_update_user_rls(self, user, zf_user: ZFUser):
        """
        Checks current user info against user_info from oauth_user_info
        This will update user row level security
        """
        if user is not None and zf_user.is_internal_user is False:
            # Generates row level security access \
            rls = self.find_rls(
                name=f"{AccessMethod.EXTERNAL.value} {zf_user.enterprise_id}"
            )
            if rls is None:
                # Only applied to enteprise role of the current user
                enterprise_role = self.find_role(zf_user.superset_role_name)
                self.add_rls(
                    enterprise_id=zf_user.enterprise_id,
                    roles=[enterprise_role],
                    tables=self.get_all_data_sources(),
                )
            else:
                try:
                    rls.tables = self.get_all_data_sources()
                    self.get_session.merge(rls)
                    self.get_session.commit()
                except Exception as e:
                    logging.error(e)
                    self.get_session.rollback()
                    return None
        return user

    def check_and_update_user_role(self, user, zf_user: ZFUser):
        """
        Checks current user info against user_info from oauth_user_info
        this will update user role
        """

        if "Admin" in user.roles:
            return user

        if zf_user.is_active is False:
            return None

        if zf_user.is_internal_user:
            if self._access_method == AccessMethod.EXTERNAL.value:
                role = self.find_role("Admin")
            else:
                # pylint: disable=import-outside-toplevel
                from bi_superset.bi_security_manager.models.models import (
                    RolesPerJobTitle,
                )

                query = (
                    self.get_session()
                    .query(RolesPerJobTitle)
                    .filter(RolesPerJobTitle.username == zf_user.email)
                )

                user_role_job_title = query.one_or_none()

                # comment due that is not viable to use yet
                # role = self.find_role(user_role_job_title.role_name)
                role = self.find_role("zerofox_internal")
            user.roles += [role]

        else:
            # Check if role exists, `view_only enterprise_id``
            default_role = self.find_role("view_only")
            role = self.find_role(zf_user.superset_role_name)
            if role is None:
                # If not copy from default role permissions
                # Creates new roles
                role = self.add_role(
                    zf_user.superset_role_name, default_role.permissions
                )
            # Assign it to current user
            user.roles = [default_role, role]

        self.update_user(user)
        return user

    def get_all_data_sources(self):
        """
        Collect datasources that are present on superset

        :returns: The list of datasources
        """

        # pylint: disable=import-outside-toplevel
        from superset.connectors.sqla.models import SqlaTable

        session = self.get_session
        all_datasources = SqlaTable.get_all_datasources(session)
        return all_datasources

    def add_rls(self, enterprise_id, roles, tables):
        """
        Create a row level security filter.

        :param name: The name of the row level security filter
        :param roles: The roles that have access to the row level security filter
        :param tables: The tables that the row level security filter applies to
        """
        # pylint: disable=import-outside-toplevel
        from superset.connectors.sqla.models import (
            RowLevelSecurityFilter,
        )

        rls = RowLevelSecurityFilter(
            name=f"{AccessMethod.EXTERNAL.value} {enterprise_id}"
        )
        rls.roles = roles
        rls.tables = tables
        rls.clause = f"ENTERPRISE_ID = {enterprise_id}"
        rls.filter_type = "Regular"

        self.get_session.add(rls)
        self.get_session.commit()

    def find_rls(self, name: str) -> Optional["RowLevelSecurityFilter"]:
        """
        Find a row level security filter by name.

        :param name: The name of the row level security filter
        :returns: The row level security filter if found, None otherwise
        """
        # pylint: disable=import-outside-toplevel
        from superset.connectors.sqla.models import RowLevelSecurityFilter

        query = (
            self.get_session()
            .query(RowLevelSecurityFilter)
            .filter(RowLevelSecurityFilter.name == name)
        )

        rls = query.one_or_none()

        return rls
