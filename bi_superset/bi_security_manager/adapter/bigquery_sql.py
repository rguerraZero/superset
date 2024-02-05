"""
Bigquery sql adapter for sql database
"""
# Libraries
import pandas as pd
import pandas_gbq as gbq
import google.auth
from flask import current_app

# Abstract class
from bi_superset.bi_security_manager.port.a_sql import ASql

BQ_DATASET = current_app.config.get("BQ_DATASET")
class BigquerySQL(ASql):
    def __init__(self) -> None:
        credentials, _ = google.auth.default(
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/bigquery",
            ]
        )
        gbq.context.credentials = credentials
        # set project
        gbq.context.project = "csdataanalysis"

    def get_df(self, query: str) -> pd.DataFrame:
        """
        Returns a dataframe from a given query in Bigquery
        """
        if query is None or query == "":
            raise ValueError("query is required")

        try:
            df = gbq.read_gbq(query, project_id="csdataanalysis")
            return df
        except Exception as e:
            raise ValueError(f"Error getting dataframe from bigquery: {e}")

    def get_schema(self, schema_name: str, table_name: str) -> pd.DataFrame:
        """
        Returns a dataframe containing the schema of the table in Bigquery
        """
        if schema_name is None or table_name is None:
            raise ValueError("schema_name and table_name are required")

        query = """
            SELECT
                column_name,
                data_type
            FROM
            `{dataset}.{schema}.INFORMATION_SCHEMA.COLUMNS`
            WHERE 1 = 1
            AND table_name='{table_name}'
        """.format(
            dataset="csdataanalysis", schema=schema_name, table_name=table_name
        )

        try:
            df = self.get_df(query=query)
            return df
        except Exception as e:
            raise ValueError(f"Error getting schema from bigquery: {e}")
