from typing import List
import pandas as pd

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

    def get_user_role_name(self, user: User) -> str:
        """
        Retrieves user role name based on user_email

        For external users, default is `View_only`

        For internal users, will look in `bi_superset_access.roles_per_job_title`

        """
        if user is None:
            raise ValueError("user is required")

        # External users default role is view_only
        if user.access_method == "external":
            return "view_only"

        # Loads and parse roles_per_job_title
        query = ROLES_PER_JOB_TITLE.format(email=user.email)

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
            permissions.append(permission.to_superset_permision_dict())

        return permissions

    def get_user_role_permission(self, user: User):
        """
        Returns a list of SupersetRolePermission from bq
        """
        if user is None:
            raise ValueError("user is required")

        if user.role_name is None:
            raise ValueError("user.role_name is required")

        query = ROLE_DEFINITIONS_QUERY.format(
            role_name=user.role_name, access_method=user.access_method
        )

        df = self.sql.get_df(query)

        return self._parse_roles(df=df)
