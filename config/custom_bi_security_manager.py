from typing import (
    Dict,
    Optional,
    Set,
)
from collections import defaultdict

import logging
from superset.security import SupersetSecurityManager

from bi_security_manager.services.role_gatherer import RoleGatherer
from bi_security_manager.services.user_gatherer import UserGatherer
from bi_security_manager.adapter.bigquery_sql import BigquerySQL


class CustomBISecurityManager(SupersetSecurityManager):
    def __init__(self, appbuilder):
        super(CustomBISecurityManager, self).__init__(appbuilder)

    def auth_user_db(self, username, password):
        """
        Authenticate user against an external system.

        :param username: The username for the user
        :param password: The password for the user
        """
        # Retrieves roles df
        # df = self._role_gatherer.retrieves_roles("View only", "external")
        # Parse roles into parsed
        # roles_parsed = self._role_gatherer.parse_roles(df)
        roles_parsed = []

        # rls = self.get_all_row_level_security()
        logging.debug(self.get_all_data_sources())
        user = self.find_user(username=username)

        # If user does not exists, create it and assing view and permissions

        if user is None:
            # Base method that get role or create it
            permissions = []

            for permission in roles_parsed:
                permissions.append(
                    self.find_permission_view_menu(
                        permission_name=permission["permission"]["name"],
                        view_menu_name=permission["view_menu"]["name"],
                    )
                )
            role = self.add_role("View only2", permissions=permissions)

            user = self.add_user(
                username=username,
                first_name="First",
                last_name="Last",
                email=username + "@example.com",
                role=role,
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

    def create_rls(self, name, enterprise_id, roles, tables):
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

        self.get_session().add(rls)
        self.get_session().commit()

    def find_rls_by_name(self, name: str) -> Optional["RowLevelSecurityFilter"]:
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
