import pandas as pd

from bi_superset.bi_security_manager.port.a_sql import ASql
from bi_superset.bi_security_manager.sql.queries import DASHBOARD_ROLE_ACCESS_EXTERNAL, RBAC_ROLES, DASHBOARD_RBAC_ROLE_ASSIGNATION
from bi_superset.bi_security_manager.models.models import (
    DashboardRoleAccessExternal,
    RBACRoles,
    DashboardRBACRoleAssignation
)
from flask import current_app

BQ_DATASET = current_app.config.get("BQ_DATASET")


class DashboardRoleAccessService:
    def __init__(self, sql: ASql):
        self.sql: ASql = sql


    def get_dashboard_role_access_external(self):
        """
        Get dashboard role access for external users
        """

        query = DASHBOARD_ROLE_ACCESS_EXTERNAL.format(dataset=BQ_DATASET)

        df = self.sql.get_df(query)

        if df.empty:
            raise ValueError("no dashboard role access found")

        dashboard_role_accesses = []
        for _, row in df.iterrows():
            role_access = DashboardRoleAccessExternal.from_dict(row)
            dashboard_role_accesses.append(role_access)

        df = pd.DataFrame(
            [
                dashboard_role_access.to_dict()
                for dashboard_role_access in dashboard_role_accesses
            ]
        )
        # nmapping
        return df

    def get_rbac_roles(self):
        """Retrieves RBAC roles from the database

        Returns:
            pd.DataFrame: Return a Dataframe of the RBAC roles
        """
        query = RBAC_ROLES.format(dataset=BQ_DATASET)
        df = self.sql.get_df(query)
        if df.empty:
            raise ValueError("no rbac roles found")
        
        rbac_roles = []
        for _, row in df.iterrows():
            rbac_role = RBACRoles.from_dict(row)
            rbac_roles.append(rbac_role)

        df = pd.DataFrame(
            [
                rbac_role.to_dict()
                for rbac_role in rbac_roles
            ]
        )
        # nmapping
        return df
    
    def get_dashboard_rbac_role_assignation(self):
        query = DASHBOARD_RBAC_ROLE_ASSIGNATION.format(dataset=BQ_DATASET)
        df = self.sql.get_df(query)
        if df.empty:
            raise ValueError("no rbac role assignation found")
        
        dashboard_rbac_role_assignations = []
        for _, row in df.iterrows():
            dashboard_rbac_role_assignation = DashboardRBACRoleAssignation.from_dict(row)
            dashboard_rbac_role_assignations.append(dashboard_rbac_role_assignation)

        df = pd.DataFrame(
            [
                dashboard_rbac_role_assignation.to_dict()
                for dashboard_rbac_role_assignation in dashboard_rbac_role_assignations
            ]
        )
        # nmapping
        return df