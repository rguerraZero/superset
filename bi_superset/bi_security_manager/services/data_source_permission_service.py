from typing import List
import pandas as pd
from bi_superset.bi_security_manager.port.a_sql import ASql
from bi_superset.bi_security_manager.models.models import DataSourceAccess
from bi_superset.bi_security_manager.sql.queries import DATA_SOURCE_PERMISSIONS_QUERY
from bi_superset.bi_security_manager.models.access_method import AccessMethod
from flask import current_app

BQ_DATASET = current_app.config.get("BQ_DATASET")

class DataSourcePermissionService:
    """
    Gather information about Datasource permission of a given role
    this data lives on bigquery
    """

    def __init__(self, sql: ASql):
        self.sql: ASql = sql

    def get_data_sources(
        self, role_name: str, access_method: str
    ) -> List[DataSourceAccess]:
        """
        Retrieves list of datasources based on `role_name` and `access_method`
        """
        if role_name in [None, ""]:
            raise ValueError("role_name is required")

        if not any(method.value == access_method for method in AccessMethod):
            raise ValueError("access_method is required")

        query = DATA_SOURCE_PERMISSIONS_QUERY.format(
            dataset=BQ_DATASET, role_name=role_name, access_method=access_method
        )

        df = self.sql.get_df(query)

        if df.empty:
            raise ValueError(
                f"Datasource not found based on role name = {role_name} and access method = {access_method} "
            )

        data_sources = []

        for row in df.to_dict(orient="records"):
            data_sources.append(DataSourceAccess.from_dict(row, role_name=role_name))

        return data_sources
