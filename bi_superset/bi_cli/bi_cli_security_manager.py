import os
import logging
from superset.security import SupersetSecurityManager

from bi_superset.bi_security_manager.models.access_method import AccessMethod


class BICLISecurityManager(SupersetSecurityManager):
    def __init__(self, appbuilder):
        super(BICLISecurityManager, self).__init__(appbuilder)

        self._access_method = os.getenv("SUPERSET_ACCESS_METHOD", None)

        # Validates that the access method is set
        if not any(method.value == self._access_method for method in AccessMethod):
            raise Exception("CONFIGURATION SUPERSET_ACCESS_METHOD is not set")

    def sync_roles_and_permissions(self):
        """
        Obtain all roles and permission from bigquery
        this creates roles and assing permission
        info located on `csdataanalysis.bi_superset_access.role_definitions_{access_method}`
        """
        from bi_superset.bi_security_manager.services.role_gatherer_service import (
            RoleGathererService,
        )
        from bi_superset.bi_security_manager.adapter.bigquery_sql import BigquerySQL

        bq_client = BigquerySQL()
        role_gatherer = RoleGathererService(bq_client)

        logging.info("Getting roles from BigQuery")

        roles = role_gatherer.get_roles(access_method=self._access_method)

        for role_name in roles:
            logging.info(f"Getting role  from superset {role_name}")
            role = self.find_role(role_name)

            logging.info(f"Getting roles permissions for {role_name}")
            role_permissions = role_gatherer.get_role_permission(
                role_name=role_name, access_method=self._access_method
            )

            permisions = [
                self.find_permission_view_menu(
                    permission_name=permission.permission,
                    view_menu_name=permission.view_menu,
                )
                for permission in role_permissions
            ]
            if role is None:
                role = self.add_role(role_name, permissions=permisions)
            else:
                try:
                    role.permissions = permisions
                    self.get_session.merge(role)
                    self.get_session.commit()
                except Exception as e:
                    logging.error(e)
                    self.get_session.rollback()
                    raise Exception("Error updating role")

    # Loads datasource access per role
    def loads_data_sources_access(self):
        """
        Generates `data_source_access` table that contains all the data sources
        that each role has access to.
        """
        from bi_superset.bi_security_manager.services.role_gatherer_service import (
            RoleGathererService,
        )
        from bi_superset.bi_security_manager.adapter.bigquery_sql import BigquerySQL
        from bi_superset.bi_security_manager.services.data_source_permission_service import (
            DataSourcePermissionService,
        )
        from superset.utils.database import get_main_database
        from sqlalchemy import inspect, String, Integer
        import pandas as pd

        bq_client = BigquerySQL()
        role_gatherer = RoleGathererService(bq_client)
        data_source_permission = DataSourcePermissionService(bq_client)

        logging.info("Getting roles from BigQuery")

        roles = role_gatherer.get_roles(access_method=self._access_method)

        results = []
        for role_name in roles:
            results.extend(
                data_source_permission.get_data_sources(role_name, self._access_method)
            )

        res_df = pd.DataFrame([result.to_dict() for result in results])

        tbl_name = "bi_data_source_access"
        database = get_main_database()
        with database.get_sqla_engine_with_context() as engine:
            schema = inspect(engine).default_schema_name

            res_df.to_sql(
                tbl_name,
                engine,
                schema=schema,
                if_exists="replace",
                chunksize=500,
                dtype={
                    "id": Integer,
                    "database": String(255),
                    "table_catalog": String(255),
                    "table_schema": String(255),
                    "table_name": String(255),
                    "role_name": String(255),
                },
                index=True,
                index_label="id",
            )
        # TODO: COMMENTING OUT TILL WE HAVE DECIDE ON HOW TO HANDLE INTERNAL ACCESS
        # if access method is internal
        # if AccessMethod.is_internal(self._access_method):
        #     from superset.connectors.sqla.models import SqlaTable

        #     permission_name = "datasource_access"
        #     session = self.get_session()
        #     # iterate over res_df
        #     for row in res_df.to_dict(orient="records"):
        #         # role
        #         role_to_find = row["role_name"]
        #         if "admin" == role_to_find:
        #             continue

        #         role = self.find_role(row["role_name"])
        #         if role is None:
        #             logging.warning(f"Role {role_to_find} does not exist.")
        #             continue
        #         table_name = row["table_name"]
        #         table_schema = row["table_schema"]
        #         logging.info(f"Getting Table {table_schema} {table_name}")
        #         dataset = (
        #             session.query(SqlaTable)
        #             .filter(
        #                 SqlaTable.table_name == table_name,
        #                 SqlaTable.schema == table_schema,
        #             )
        #             .one_or_none()
        #         )
        #         if dataset is None:
        #             logging.warning(
        #                 f"Dataset {table_schema}.{table_name} does not exist."
        #             )
        #             continue
        #         dataset_permission_view = self.find_permission_view_menu(
        #             permission_name, dataset.get_perm()
        #         )
        #         self.add_permission_role(role, dataset_permission_view)
        #         session.commit()

    def loads_roles_per_job_title(self):
        """
        Generates `roles_per_job_title` table that contains `internal zf`
        role assignation per job title
        """
        if not AccessMethod.is_internal(self._access_method):
            logging.info("This method only works with internal access method")
            return

        from bi_superset.bi_security_manager.adapter.bigquery_sql import BigquerySQL
        from bi_superset.bi_security_manager.services.roles_per_job_title_service import (
            RolePerJobTitleService,
        )
        from superset.utils.database import get_main_database
        from sqlalchemy import inspect, String

        bq_client = BigquerySQL()
        role_per_job_title_service = RolePerJobTitleService(bq_client)

        roles_per_job_title_df = role_per_job_title_service.get_role_per_job_title()

        tbl_name = "bi_roles_per_job_title"
        database = get_main_database()
        with database.get_sqla_engine_with_context() as engine:
            schema = inspect(engine).default_schema_name

            roles_per_job_title_df.to_sql(
                tbl_name,
                engine,
                schema=schema,
                if_exists="replace",
                chunksize=500,
                dtype={
                    "username": String(255),
                    "role_name": String(255),
                    "rbac_roles": String(255),
                },
                index=False,
            )

    def loads_dashboard_access_external(self):
        """
        Generates `dashboard_role_access_external` table that contains `external zf`
        role assignation per dashboard
        """
        if not AccessMethod.is_external(self._access_method):
            logging.info("This method only works with external access method")
            return

        from bi_superset.bi_security_manager.adapter.bigquery_sql import BigquerySQL
        from bi_superset.bi_security_manager.services.dashboard_role_access_service import (
            DashboardRoleAccessService,
        )
        from superset.utils.database import get_main_database
        from sqlalchemy import inspect, String, Integer

        bq_client = BigquerySQL()
        dashboard_role_access = DashboardRoleAccessService(bq_client)

        dashboard_role_access_df = (
            dashboard_role_access.get_dashboard_role_access_external()
        )

        tbl_name = "bi_dashboard_role_access_external"
        database = get_main_database()
        with database.get_sqla_engine_with_context() as engine:
            schema = inspect(engine).default_schema_name

            dashboard_role_access_df.to_sql(
                tbl_name,
                engine,
                schema=schema,
                if_exists="replace",
                chunksize=500,
                dtype={
                    "id": Integer,
                    "dashboard_id": Integer,
                    "role_name": String(255),
                },
                index_label="id",
            )

    def update_dashboard_default_access(self):
        """
        Re-create all dashboard role RBAC relationship based on
        `bi_dashboard_role_access_external` table
        """

        if not AccessMethod.is_external(self._access_method):
            logging.info("This method only works with external access method")
            return

        from bi_superset.bi_security_manager.models.models import (
            DashboardRoleAccessExternal,
        )
        from superset.models.dashboard import Dashboard

        # First delete all rows of DashboardRoles table
        session = self.get_session()

        # Get All Dashboards
        query = session.query(Dashboard)

        dashboards = query.all()

        # Every Dashboard will remove role relationship
        for dashboard in dashboards:
            dashboard.roles = []
            session.merge(dashboard)

        # Fetch role_name and dashboard_id from DashboardRoleAccessExternal
        query = session.query(
            DashboardRoleAccessExternal.role_name,
            DashboardRoleAccessExternal.dashboard_id,
        )
        dashboard_role_accesses = query.all()

        # Iterate over role accesses and Add role to dashboard
        for dashboard_role_access in dashboard_role_accesses:
            role = self.find_role(dashboard_role_access.role_name)

            # If role no exists clone from default role
            if role is None:
                role = self.find_role("view_only")

                role = self.add_role(
                    dashboard_role_access.role_name,
                    permissions=role.permissions,
                )

            # Get dashboard by ID
            dashboard = (
                session.query(Dashboard)
                .filter(Dashboard.id == dashboard_role_access.dashboard_id)
                .one_or_none()
            )

            if dashboard is None:
                continue

            # Assing role to dashboard
            dashboard.roles += [role]

            # Update dashboard
            session.merge(dashboard)
        # Commit changes
        session.commit()

    def sync_rbac_role_list(self):
        if not AccessMethod.is_internal(self._access_method):
            logging.info("This method only works with internal access method")
            return

        from bi_superset.bi_security_manager.adapter.bigquery_sql import BigquerySQL
        from bi_superset.bi_security_manager.services.dashboard_role_access_service import (
            DashboardRoleAccessService,
        )
        from superset.utils.database import get_main_database
        from sqlalchemy import inspect, String, Integer, delete
        from bi_superset.bi_security_manager.models.models import (
                            RBACRoles,
                        )
        from superset.models.dashboard import DashboardRoles

        from flask_appbuilder.security.sqla.models import Role, assoc_user_role
        
        bq_client = BigquerySQL()
        dashabord_role_access_service = DashboardRoleAccessService(bq_client)

        roles_per_job_title_df = dashabord_role_access_service.get_rbac_roles()

        tbl_name = "bi_rbac_roles"
        database = get_main_database()
        with database.get_sqla_engine_with_context() as engine:
            schema = inspect(engine).default_schema_name

            roles_per_job_title_df.to_sql(
                tbl_name,
                engine,
                schema=schema,
                if_exists="replace",
                chunksize=500,
                dtype={
                    "id": Integer,
                    "role_name": String(255),
                },
                index_label="id",
            )
        session = self.get_session()


        logging.info("Gettint RBAC Roles from Role table")
        query = (
                    session
                    .query(Role)
                    .filter(Role.name.startswith("rbac_"))
                )
        roles = query.all()

        logging.info("Getting RBAC Roles from RBAC Role Table")
        query = (
                    session
                    .query(RBACRoles)
                    .filter(RBACRoles.role_name.startswith("rbac_"))
                )
        rbac_roles = query.all()

        # delete roles thar are not in rbac_roles
        for role in roles:
            # Search by role.name in rbac_roles.role_name
            if role.name not in [rbac_role.role_name for rbac_role in rbac_roles]:
                logging.info("Deleting role from superset %s", role.name)
                # need to search all role_id in `assoc_user_role` and delete
                # Delete user role association
                session.query(assoc_user_role).filter(assoc_user_role.c.role_id == role.id).delete(synchronize_session=False)
                session.commit()
                # Delete dashboard role association
                session.query(DashboardRoles).filter(DashboardRoles.c.role_id == role.id).delete(synchronize_session=False)
                session.commit()
                # Delete Role
                session.delete(role)
                session.commit()

        # Skip existing RBAC Roles
        for rbac_role in rbac_roles:
            if rbac_role.role_name not in [role.name for role in roles]:
                logging.info("Creating role from superset %s", rbac_role.role_name)
                self.add_role(rbac_role.role_name)


    def sync_dashboard_rbac_role_assignation(self):
        if not AccessMethod.is_internal(self._access_method):
            logging.info("This method only works with internal access method")
            return

        from bi_superset.bi_security_manager.adapter.bigquery_sql import BigquerySQL
        from bi_superset.bi_security_manager.services.dashboard_role_access_service import (
            DashboardRoleAccessService,
        )
        from superset.utils.database import get_main_database
        from sqlalchemy import inspect, String, Integer



        bq_client = BigquerySQL()
        dashabord_role_access_service = DashboardRoleAccessService(bq_client)

        roles_per_job_title_df = dashabord_role_access_service.get_dashboard_rbac_role_assignation()

        tbl_name = "bi_dashboard_rbac_role_assignation"
        database = get_main_database()
        with database.get_sqla_engine_with_context() as engine:
            schema = inspect(engine).default_schema_name

            roles_per_job_title_df.to_sql(
                tbl_name,
                engine,
                schema=schema,
                if_exists="replace",
                chunksize=500,
                dtype={
                    "id": Integer,
                    "role_name": String(255),
                    "dashboard_id": Integer,
                },
                index_label="id",
            )

        from superset.models.dashboard import Dashboard
        session = self.get_session()
        
        # Get All Dashboards
        query = session.query(Dashboard)

        dashboards = query.all()



        from bi_superset.bi_security_manager.models.models import (
                            DashboardRBACRoleAssignation,
                        )
        import datetime
        query = (
                    session
                    .query(DashboardRBACRoleAssignation)
                    .filter(DashboardRBACRoleAssignation.role_name.startswith("rbac_"))
                )
        rbac_roles = query.all()

        # Every Dashboard will remove role relationship
        # where dashboard_id is not -1
        exclusion_dashboard_ids = [rbac_role.dashboard_id for rbac_role in rbac_roles if rbac_role.dashboard_id != -1]

        for dashboard in dashboards:
            roles =  []
            for rbac_role in rbac_roles:
                if rbac_role.dashboard_id == dashboard.id:
                    role = self.find_role(rbac_role.role_name)
                    if role is None:
                        raise Exception("Role not found")
                    roles.append(role)
                elif rbac_role.dashboard_id == -1 and dashboard.id not in exclusion_dashboard_ids:
                    role = self.find_role(rbac_role.role_name)
                    if role is None:
                        raise Exception("Role not found")
                    roles.append(role)
            dashboard.roles = roles
            session.merge(dashboard)
        session.commit()