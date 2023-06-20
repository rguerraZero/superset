from typing import List
import pandas as pd

from bi_security_manager.port.a_sql import ASql
from bi_security_manager.models.datasource import DataSource
from bi_security_manager.models.user import User
from bi_security_manager.sql.queries import DATA_SOURCE_PERMISSIONS_QUERY


class DataSourcePermission:
    """
    Gather information about Datasource permission of a given role
    this data lives on bigquery
    """

    def __init__(self, sql: ASql):
        self.sql: ASql = sql

    def get_data_sources(self, user: User) -> List[DataSource]:
        query = DATA_SOURCE_PERMISSIONS_QUERY.format(
            role_name=user.role_name, access_method=user.access_method
        )

        df = self.sql.get_df(query)

        if df.empty:
            raise ValueError(
                f"Datasource not found based on role name = {user.role_name} "
            )

        data_sources = []

        for row in df.to_dict(orient="records"):
            data_sources.append(DataSource.from_dict(row))

        return data_sources
