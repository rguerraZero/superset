import pandas as pd

from bi_superset.bi_security_manager.port.a_sql import ASql
from bi_superset.bi_security_manager.sql.queries import DASHBOARD_ROLE_ACCESS_EXTERNAL
from bi_superset.bi_security_manager.models.models import (
    DashboardRoleAccessExternal,
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
