from typing import List
import pandas as pd
from bi_superset.bi_security_manager.models.access_method import AccessMethod

from bi_superset.bi_security_manager.port.a_sql import ASql
from bi_superset.bi_security_manager.models.superset_role_permission import (
    SupersetRolePermission,
)
from bi_superset.bi_security_manager.sql.queries import (
    ROLE_DEFINITIONS_QUERY,
    ROLES_QUERY,
)
from flask import current_app

BQ_DATASET = current_app.config.get("BQ_DATASET")


class RoleGathererService:
    """Gather roles."""

    def __init__(self, sql: ASql):
        self.sql: ASql = sql

    def get_roles(self, access_method: str) -> List[str]:
        """
        Retrieves list of roles located in `bi_superset_access.roles`
        """
        if not any(method.value == access_method for method in AccessMethod):
            raise ValueError("access_method is required")

        query = ROLES_QUERY.format(dataset=BQ_DATASET, access_method=access_method)

        df = self.sql.get_df(query)

        if df.empty:
            raise ValueError("No roles found")

        return df["name"].tolist()

    def _parse_roles(self, df: pd.DataFrame) -> List[dict]:
        """
        Returns mapped roles into superset permissions
        """
        if df is None:
            raise ValueError("df is required")

        permissions = []
        for _, row in df.iterrows():
            permission = SupersetRolePermission.from_permission_name(
                row["permission_name"]
            )
            permissions.append(permission)

        return permissions

    def get_role_permission(
        self, role_name: str, access_method: str
    ) -> List[SupersetRolePermission]:
        """
        Returns a list of SupersetRolePermission from bq
        """
        if role_name in [None, ""]:
            raise ValueError("role_name is required")

        if not any(method.value == access_method for method in AccessMethod):
            raise ValueError("access_method is required")

        query = ROLE_DEFINITIONS_QUERY.format(
            dataset=BQ_DATASET, role_name=role_name, access_method=access_method
        )

        df = self.sql.get_df(query)

        return self._parse_roles(df=df)
