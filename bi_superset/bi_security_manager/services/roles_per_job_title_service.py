import pandas as pd

from bi_superset.bi_security_manager.port.a_sql import ASql
from bi_superset.bi_security_manager.sql.queries import ROLES_PER_JOB_TITLE
from bi_superset.bi_security_manager.models.models import RolesPerJobTitle


class RolePerJobTitleService:
    def __init__(self, sql: ASql):
        self.sql: ASql = sql

    def get_role_per_job_title(self):
        """
        Retrieves user role name based on user_email

        For external users, default is `View_only`

        For internal users, will look in `bi_superset_access.roles_per_job_title`

        """

        query = ROLES_PER_JOB_TITLE

        df = self.sql.get_df(query)

        if df.empty:
            raise ValueError("user not found in roles_per_job_title")

        roles_per_job_title = []
        for _, row in df.iterrows():
            permission = RolesPerJobTitle.from_dict(row)
            roles_per_job_title.append(permission)

        df = pd.DataFrame([permission.to_dict() for permission in roles_per_job_title])
        # nmapping
        return df
