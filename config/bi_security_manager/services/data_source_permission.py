from typing import List
from functools import lru_cache

from bi_security_manager.port.a_sql import ASql
from bi_security_manager.models.datasource import DataSource
from bi_security_manager.sql.queries import DATA_SOURCE_PERMISSIONS_QUERY


class DataSourcePermission:
    """
    Gather information about Datasource permission of a given role
    this data lives on bigquery
    """

    def __init__(self, sql: ASql):
        self.sql: ASql = sql

    @lru_cache(typed=True)
    def get_data_sources(self, role_name: str, access_method: str) -> List[DataSource]:
        """
        Retrieves list of datasources based on `role_name` and `access_method`
        """
        if role_name in [None, ""]:
            raise ValueError("role_name is required")

        if access_method not in ["internal", "external"]:
            raise ValueError("access_method is required")

        query = DATA_SOURCE_PERMISSIONS_QUERY.format(
            role_name=role_name, access_method=access_method
        )

        df = self.sql.get_df(query)

        if df.empty:
            raise ValueError(
                f"Datasource not found based on role name = {role_name} and access method = {access_method} "
            )

        data_sources = []

        for row in df.to_dict(orient="records"):
            data_sources.append(DataSource.from_dict(row))

        return data_sources
