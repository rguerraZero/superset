from typing import Optional
import logging

from bi_superset.bi_security_manager.models.user import User as ZFUser
from bi_superset.bi_security_manager.models.access_method import AccessMethod
from bi_superset.bi_security_manager.models.access_origin import AccessOrigin
logger = logging.getLogger(__name__)


class UserService:

    def __init__(self, access_method, access_origin, sm):
        self._access_method = access_method
        self._access_origin = access_origin
        self.sm = sm
        self.session = self.sm.get_session

    def update_roles_rls(self, user, zf_user):
        """
        Check and Update user roles and rls,
        based on the current instance and user is_internal value
        """
        if user is None:
            return None

        user = self.get_and_update_user_roles(user, zf_user)
        self.sm.update_user(user)
        if not self.check_and_update_user_rls(zf_user):
            return None
        return user

    def check_and_update_user_rls(self, zf_user: ZFUser) -> bool:
        """
        Checks current user info against user_info from oauth_user_info
        This will update user row level security.
        """
        if AccessOrigin.is_from_zf_dashboard(self._access_origin):
            # Generates row level security access \
            rls = self.find_rls(
                name=f"{AccessMethod.EXTERNAL.value} {zf_user.enterprise_id}"
            )
            if rls is None:
                # Only applied to enteprise role of the current user
                enterprise_role = self.sm.find_role(
                    zf_user.superset_role_name(self._access_origin))
                self.add_rls(
                    enterprise_id=zf_user.enterprise_id,
                    roles=[enterprise_role],
                    tables=self.get_all_data_sources(),
                )
            else:
                try:
                    rls.tables = self.get_all_data_sources()
                    self.session.merge(rls)
                    self.session.commit()
                except Exception as e:
                    self.session.rollback()
                    return False
        return True

    def get_and_update_user_roles(self, user, zf_user: ZFUser):
        """
        Checks current user info against user_info from oauth_user_info
        this will update user role
        """
        if user.roles == "Admin" and AccessOrigin.is_from_superset_ui(self._access_origin):
            return user

        if zf_user.is_internal_user and AccessOrigin.is_from_superset_ui(self._access_origin):
            if AccessMethod.is_external(self._access_method):
                role = self.sm.find_role("Admin")
            else:
                # pylint: disable=import-outside-toplevel
                from bi_superset.bi_security_manager.models.models import (
                    RolesPerJobTitle,
                )

                query = (
                    self.session()
                    .query(RolesPerJobTitle)
                    .filter(RolesPerJobTitle.username == zf_user.email)
                )

                user_role_job_title = query.one_or_none()

                # comment due that is not viable to use yet
                # role = self.find_role(user_role_job_title.role_name)
                role = self.sm.find_role("zerofox_internal")
            user.roles += [role]

        else:
            # Check if role exists, `view_only enterprise_id``
            default_role = self.sm.find_role("view_only")
            role = self.sm.find_role(
                zf_user.superset_role_name(self._access_origin))
            if role is None:
                # If not copy from default role permissions
                # Creates new roles
                role = self.sm.add_role(
                    zf_user.superset_role_name(
                        self._access_origin), default_role.permissions
                )
            # Assign it to current user
            user.roles = [default_role, role]
        return user

    def get_all_data_sources(self):
        """
        Collect datasources that are present on superset

        :returns: The list of datasources
        """

        # pylint: disable=import-outside-toplevel
        from superset.connectors.sqla.models import SqlaTable

        session = self.session
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

        self.session.add(rls)
        self.session.commit()

    def find_rls(self, name: str) -> Optional["RowLevelSecurityFilter"]:
        """
        Find a row level security filter by name.

        :param name: The name of the row level security filter
        :returns: The row level security filter if found, None otherwise
        """
        # pylint: disable=import-outside-toplevel
        from superset.connectors.sqla.models import RowLevelSecurityFilter

        query = (
            self.session()
            .query(RowLevelSecurityFilter)
            .filter(RowLevelSecurityFilter.name == name)
        )

        rls = query.one_or_none()

        return rls
