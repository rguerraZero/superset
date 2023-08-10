from typing import (
    Dict,
    Optional,
    Set,
)
from collections import defaultdict
import logging
from superset.security import SupersetSecurityManager

# Models
from bi_security_manager.models.user import User as ZFUser


class CustomBISecurityManager(SupersetSecurityManager):
    def __init__(self, appbuilder):
        super(CustomBISecurityManager, self).__init__(appbuilder)

    def get_or_create_role(self, zf_user: ZFUser):
        # Get role
        role = self.find_role(zf_user.superset_role_name)

        if zf_user.role_name == "admin":
            return role
        from bi_security_manager.services.role_gatherer import RoleGatherer
        from bi_security_manager.adapter.bigquery_sql import BigquerySQL

        bq_client = BigquerySQL()
        role_gatherer = RoleGatherer(bq_client)
        role_permissions = role_gatherer.get_user_role_permission(
            role_name=zf_user.role_name, access_method=zf_user.access_method
        )
        permisions = [
            self.find_permission_view_menu(
                permission_name=permission.permission,
                view_menu_name=permission.view_menu,
            )
            for permission in role_permissions
        ]

        if role is None:
            role = self.add_role(zf_user.superset_role_name, permissions=permisions)
        else:
            try:
                role.permissions = permisions
                self.get_session.merge(role)
                self.get_session.commit()
            except Exception as e:
                logging.error(e)
                self.get_session.rollback()
                return
        return role

    def get_zf_user(self, username: str) -> Optional[ZFUser]:
        """
        Retrieves user from zf cache

        :param username: The username for the user
        """
        from bi_security_manager.services.user_gatherer import UserGatherer
        from bi_security_manager.adapter.bigquery_sql import BigquerySQL
        from bi_security_manager.services.role_gatherer import RoleGatherer

        bq_client = BigquerySQL()
        user_gatherer = UserGatherer(bq_client)
        role_gatherer = RoleGatherer(bq_client)
        zf_user = user_gatherer.get_user(user_email=username)
        zf_user.role_name = role_gatherer.get_user_role_name(
            email=zf_user.email, access_method=zf_user.access_method
        )

        return zf_user

    def auth_user_db(self, username, password):
        """
        Authenticate user against an external system.

        :param username: The username for the user
        :param password: The password for the user
        """

        if username == "admin":
            user = self.find_user(username=username)

            return user
        # Get user from zf cache

        zf_user = self.get_zf_user(username)

        if zf_user is None:
            logging.ERROR("User not found")
            return None

        # Check if user exists
        user = self.find_user(username=zf_user.email)

        # Get Role
        role = self.get_or_create_role(zf_user=zf_user)

        if role is None:
            logging.ERROR("Role not found")
            return None

        if user is None:
            user = self.add_user(
                username=zf_user.email,
                first_name=zf_user.first_name,
                last_name=zf_user.last_name,
                email=zf_user.email,
                role=role,
            )
        # Sync datasources
        # Temporary only for external users
        if zf_user.access_method == "external":
            pass
        # Check for access method
        if zf_user.access_method == "external":
            rls = self.find_rls(name=f"External {zf_user.enterprise_id}")
            if rls is None:
                self.add_rls(
                    enterprise_id=zf_user.enterprise_id,
                    roles=[role],
                    tables=self.get_all_data_sources()[self.find_database("bigquery")],
                )
        return user

    def get_all_data_sources(self):
        """
        Collect datasources which the user has explicit permissions to.

        :returns: The list of datasources
        """

        # pylint: disable=import-outside-toplevel
        from superset.connectors.sqla.models import SqlaTable
        from superset.models.core import Database

        # group all datasources by database
        session = self.get_session
        all_datasources = SqlaTable.get_all_datasources(session)
        datasources_by_database: Dict["Database", Set["SqlaTable"]] = defaultdict(set)
        for datasource in all_datasources:
            datasources_by_database[datasource.database].add(datasource)

        return datasources_by_database

    def add_rls(self, enterprise_id, roles, tables):
        """
        Create a row level security filter.

        :param name: The name of the row level security filter
        :param roles: The roles that have access to the row level security filter
        :param tables: The tables that the row level security filter applies to
        """
        from superset.connectors.sqla.models import RowLevelSecurityFilter

        rls = RowLevelSecurityFilter(name=f"External {enterprise_id}")
        rls.roles = roles
        rls.tables = tables
        rls.clause = f"ENTERPRISE_ID = {enterprise_id}"

        self.get_session.add(rls)
        self.get_session.commit()

    def find_rls(self, name: str) -> Optional["RowLevelSecurityFilter"]:
        """
        Find a row level security filter by name.

        :param name: The name of the row level security filter
        :returns: The row level security filter if found, None otherwise
        """
        from superset.connectors.sqla.models import RowLevelSecurityFilter

        query = (
            self.get_session()
            .query(RowLevelSecurityFilter)
            .filter(RowLevelSecurityFilter.name == name)
        )

        rls = query.one_or_none()

        logging.debug(rls.name)
        for role in rls.roles:
            logging.debug(role.name)
        logging.debug(rls.clause)
        for table in rls.tables:
            logging.debug(table.table_name)
        return rls
