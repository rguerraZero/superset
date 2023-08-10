from typing import List
import pandas as pd
from functools import lru_cache

from bi_security_manager.port.a_sql import ASql
from bi_security_manager.models.superset_role_permission import SupersetRolePermission
from bi_security_manager.models.user import User
from bi_security_manager.sql.queries import (
    ROLES_PER_JOB_TITLE,
    ROLE_DEFINITIONS_QUERY,
)


class RoleGatherer:
    """Gather roles."""

    def __init__(self, sql: ASql):
        self.sql: ASql = sql

    @lru_cache()
    def get_user_role_name(self, email: str, access_method: str) -> str:
        """
        Retrieves user role name based on user_email

        For external users, default is `View_only`

        For internal users, will look in `bi_superset_access.roles_per_job_title`

        """
        if email in [None, ""]:
            raise ValueError("user is required")

        if access_method not in ["internal", "external"]:
            raise ValueError("access_method is required")

        # External users default role is view_only
        if access_method == "external":
            return "view_only"

        # Loads and parse roles_per_job_title
        query = ROLES_PER_JOB_TITLE.format(email=email)

        df = self.sql.get_df(query)

        if df.empty:
            raise ValueError("user not found in roles_per_job_title")

        if df.shape[0] > 1:
            raise ValueError("user found in more than one role in roles_per_job_title")

        # Got role name
        role_name = df.iloc[0]["role_name"]

        role_name = role_name.replace(" ", "_")

        role_name = role_name.lower()

        return role_name

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

    @lru_cache()
    def get_user_role_permission(
        self, role_name: str, access_method: str
    ) -> List[SupersetRolePermission]:
        """
        Returns a list of SupersetRolePermission from bq
        """
        if role_name in [None, ""]:
            raise ValueError("role_name is required")

        if access_method not in ["internal", "external"]:
            raise ValueError("access_method is required")

        query = ROLE_DEFINITIONS_QUERY.format(
            role_name=role_name, access_method=access_method
        )

        df = self.sql.get_df(query)

        return self._parse_roles(df=df)
